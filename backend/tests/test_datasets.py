import pytest
import io
import json
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.core.database import Base, get_db
from backend.api.auth.router import get_current_user
from backend.app.main import app
from backend.models.dataset import Dataset
from backend.models.crime import CrimeEvent
from backend.models.location import Location
from backend.models.police_station import PoliceStation

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # Seed location and police station master data required for import validation
    loc = Location(id=1, state="Karnataka", district="Bengaluru", latitude=12.97, longitude=77.59)
    station = PoliceStation(id=1, station_name="Koramangala PS", district="Bengaluru", capacity=50, location_id=1)
    db.add(loc)
    db.add(station)
    db.commit()
    
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client_as_admin(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def mock_admin_user():
        return {"id": 1, "email": "admin@police.gov.in", "role": "ADMIN", "status": "active"}

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = mock_admin_user
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

def test_dataset_operations(client_as_admin, db_session):
    # 1. Get initial dataset list (clean registry, no seed dataset)
    response = client_as_admin.get("/api/v1/admin/datasets/")
    assert response.status_code == 200
    datasets = response.json()
    assert datasets == []

    # 2. Upload a new dataset CSV
    csv_content = (
        "fir_id,crime_type,crime_date,crime_time,district,police_station,victim_age,accused_age,gender,occupation,repeat_offender,severity,status\n"
        "FIR001,Theft,2025-05-10,14:30,Bengaluru,Koramangala PS,34,22,Male,Driver,1,3.0,reported\n"
        "FIR002,Assault,2025-05-11,09:15,Bengaluru,Koramangala PS,45,28,Female,Business,0,2.0,reported\n"
    )
    
    file_payload = {"file": ("test_crimes.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    form_data = {"display_name": "Test Upload", "description": "Test dataset description"}
    
    response = client_as_admin.post(
        "/api/v1/admin/datasets/upload",
        data=form_data,
        files=file_payload
    )
    assert response.status_code == 200
    new_ds = response.json()
    assert new_ds["display_name"] == "Test Upload"
    assert new_ds["row_count"] == 2
    assert new_ds["status"] == "Ready"
    assert new_ds["is_active"] is True
    
    new_dataset_id = new_ds["id"]
    
    # Verify records are created with the new dataset_id
    crimes = db_session.query(CrimeEvent).filter(CrimeEvent.dataset_id == new_dataset_id).all()
    assert len(crimes) == 2
    assert crimes[0].crime_type == "Theft"

    # 3. Delete the active dataset and verify the archive flow still works without a seed fallback
    response = client_as_admin.delete(f"/api/v1/admin/datasets/{new_dataset_id}")
    assert response.status_code == 200

    # Verify soft delete: status becomes Archived
    deleted_ds = db_session.query(Dataset).filter(Dataset.id == new_dataset_id).first()
    assert deleted_ds.status == "Archived"
    assert deleted_ds.is_active is False

    # Check that associated crime events are NOT deleted (soft delete keeps data for auditability)
    crimes_after_delete = db_session.query(CrimeEvent).filter(CrimeEvent.dataset_id == new_dataset_id).all()
    assert len(crimes_after_delete) == 2

    # 4. Test dataset summary API
    response = client_as_admin.get(f"/api/v1/admin/datasets/{new_dataset_id}/summary")
    assert response.status_code == 200
    summary = response.json()
    assert "total_crimes" in summary
    assert "criminals" in summary
    assert "victims" in summary
    assert "date_range" in summary
    assert "districts" in summary
    assert summary["file_size"] >= 0

    # 8. Test transactional rollback on validation failure during upload
    bad_csv_content = (
        "fir_id,crime_type,crime_date,crime_time,district,police_station,victim_age,accused_age,gender,occupation,repeat_offender,severity,status\n"
        "FIR001,Theft,2025-05-10,14:30,InvalidDistrict,Koramangala PS,34,22,Male,Driver,1,3.0,reported\n"
    )
    file_payload_bad = {"file": ("bad_crimes.csv", io.BytesIO(bad_csv_content.encode("utf-8")), "text/csv")}
    form_data_bad = {"display_name": "Bad Upload", "description": "Should fail"}
    response = client_as_admin.post(
        "/api/v1/admin/datasets/upload",
        data=form_data_bad,
        files=file_payload_bad
    )
    assert response.status_code == 400
    
    # Verify that the dataset was registered as Failed in the DB
    failed_ds = db_session.query(Dataset).filter(Dataset.display_name == "Bad Upload").first()
    assert failed_ds is not None
    assert failed_ds.status == "Failed"
    
    # Verify that NO crimes were imported for this dataset (transactional rollback)
    failed_crimes = db_session.query(CrimeEvent).filter(CrimeEvent.dataset_id == failed_ds.id).all()
    assert len(failed_crimes) == 0

def test_new_dataset_features(client_as_admin, db_session, monkeypatch):
    import os
    import pandas as pd
    csv_content = (
        "fir_id,crime_type,crime_date,crime_time,district,police_station,victim_age,accused_age,gender,occupation,repeat_offender,severity,status\n"
        "FIR001,Theft,2025-05-10,14:30,Bengaluru,Koramangala PS,34,22,Male,Driver,1,3.0,reported\n"
    )
    file_payload = {"file": ("preview_source.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    form_data = {"display_name": "Preview Source"}
    response = client_as_admin.post("/api/v1/admin/datasets/upload", data=form_data, files=file_payload)
    assert response.status_code == 200
    dataset_id = response.json()["id"]

    # 1. Test Dataset Details API
    resp_details = client_as_admin.get(f"/api/v1/admin/datasets/{dataset_id}")
    assert resp_details.status_code == 200
    details = resp_details.json()
    assert details["display_name"] == "Preview Source"
    assert "column_count" in details
    assert "upload_status" in details
    assert "storage_path" in details

    # 2. Test Dataset Preview API
    resp_preview = client_as_admin.get(f"/api/v1/admin/datasets/{dataset_id}/preview")
    assert resp_preview.status_code == 200
    preview = resp_preview.json()
    assert "first_20_rows" in preview
    assert "total_rows" in preview
    assert "total_columns" in preview
    assert "columns" in preview
    assert "data_types" in preview
    assert len(preview["first_20_rows"]) <= 20
    assert "district" in preview["columns"]

    # 3. Test Dataset Statistics API
    resp_stats = client_as_admin.get(f"/api/v1/admin/datasets/{dataset_id}/statistics")
    assert resp_stats.status_code == 200
    stats = resp_stats.json()
    assert "total_rows" in stats
    assert "total_columns" in stats
    assert "missing_values" in stats
    assert "duplicate_rows" in stats
    assert "numeric_columns" in stats
    assert "categorical_columns" in stats
    assert stats["total_rows"] > 0
    assert "district" in stats["missing_values"]

    # 4. Test Multi-File Upload API
    csv_content_1 = (
        "fir_id,crime_type,crime_date,crime_time,district,police_station,victim_age,accused_age,gender,occupation,repeat_offender,severity,status\n"
        "FIR101,Theft,2025-05-10,14:30,Bengaluru,Koramangala PS,34,22,Male,Driver,1,3.0,reported\n"
    )
    csv_content_2 = (
        "fir_id,crime_type,crime_date,crime_time,district,police_station,victim_age,accused_age,gender,occupation,repeat_offender,severity,status\n"
        "FIR202,Assault,2025-05-11,09:15,Bengaluru,Koramangala PS,45,28,Female,Business,0,2.0,reported\n"
    )
    
    file_payload = [
        ("files", ("test_multi_1.csv", io.BytesIO(csv_content_1.encode("utf-8")), "text/csv")),
        ("files", ("test_multi_2.csv", io.BytesIO(csv_content_2.encode("utf-8")), "text/csv"))
    ]
    form_data = {"display_name": "Multi Upload"}
    
    resp_multi = client_as_admin.post(
        "/api/v1/admin/datasets/upload",
        data=form_data,
        files=file_payload
    )
    assert resp_multi.status_code == 200
    multi_res = resp_multi.json()
    assert isinstance(multi_res, list)
    assert len(multi_res) == 2
    assert multi_res[0]["row_count"] == 1
    assert multi_res[1]["row_count"] == 1


def test_dataset_active_management(client_as_admin, db_session):
    from backend.models.dataset import Dataset
    from datetime import datetime, timedelta

    # 1. Test GET configuration
    response = client_as_admin.get("/api/v1/admin/datasets/config")
    assert response.status_code == 200
    assert response.json()["max_active_datasets"] == "1"

    # 2. Test PUT configuration
    resp_put = client_as_admin.put("/api/v1/admin/datasets/config", json={"max_active_datasets": "2"})
    assert resp_put.status_code == 200
    assert resp_put.json()["max_active_datasets"] == "2"

    # Add 3 dummy datasets in the DB in ready status
    now = datetime.utcnow()
    ds1 = Dataset(
        name="ds1", display_name="Dataset 1", original_filename="ds1.csv",
        source_type="CSV", status="Ready", upload_time=now - timedelta(minutes=10)
    )
    ds2 = Dataset(
        name="ds2", display_name="Dataset 2", original_filename="ds2.csv",
        source_type="CSV", status="Ready", upload_time=now - timedelta(minutes=5)
    )
    ds3 = Dataset(
        name="ds3", display_name="Dataset 3", original_filename="ds3.csv",
        source_type="CSV", status="Ready", upload_time=now
    )
    db_session.add_all([ds1, ds2, ds3])
    db_session.commit()

    # Make sure we deactivate any other active datasets first to isolate our test
    db_session.query(Dataset).update({Dataset.is_active: False})
    db_session.commit()

    # 3. Activate ds1
    resp_act1 = client_as_admin.post("/api/v1/admin/datasets/activate", json={"dataset_id": ds1.id})
    assert resp_act1.status_code == 200
    assert resp_act1.json()["is_active"] is True

    # 4. Activate ds2
    resp_act2 = client_as_admin.post("/api/v1/admin/datasets/activate", json={"dataset_id": ds2.id})
    assert resp_act2.status_code == 200
    assert resp_act2.json()["is_active"] is True

    # Verify both ds1 and ds2 are active (active count = 2)
    db_session.refresh(ds1)
    db_session.refresh(ds2)
    assert ds1.is_active is True
    assert ds2.is_active is True

    # 5. Activate ds3 -> should trigger overflow deactivation since limit is 2
    # ds1 is the oldest (uploaded 10m ago), so it must be automatically deactivated.
    resp_act3 = client_as_admin.post("/api/v1/admin/datasets/activate", json={"dataset_id": ds3.id})
    assert resp_act3.status_code == 200
    assert resp_act3.json()["is_active"] is True

    db_session.refresh(ds1)
    db_session.refresh(ds2)
    db_session.refresh(ds3)
    assert ds1.is_active is False  # Oldest deactivated
    assert ds2.is_active is True
    assert ds3.is_active is True

    # 6. Test GET active datasets
    resp_act = client_as_admin.get("/api/v1/admin/datasets/active")
    assert resp_act.status_code == 200
    active_list = resp_act.json()
    assert len(active_list) == 2
    active_ids = {d["id"] for d in active_list}
    assert ds2.id in active_ids
    assert ds3.id in active_ids

    # 7. Test POST deactivate
    resp_deact = client_as_admin.post("/api/v1/admin/datasets/deactivate", json={"dataset_id": ds2.id})
    assert resp_deact.status_code == 200
    assert resp_deact.json()["is_active"] is False

    db_session.refresh(ds2)
    assert ds2.is_active is False


def test_analytics_dynamic_integration(client_as_admin, db_session, monkeypatch):
    from backend.models.dataset import Dataset
    from backend.models.crime import CrimeEvent
    from backend.services.analytics_service import AnalyticsService
    from backend.core.exceptions import NoActiveDatasetException
    from backend.core.analytics_cache import AnalyticsCache
    from backend.services.dataset_service import DatasetService
    from datetime import date, datetime
    import pytest

    service = AnalyticsService(db_session)

    # 1. Mock get_active_dataset_ids to return [] -> raises NoActiveDatasetException
    monkeypatch.setattr(DatasetService, "get_active_dataset_ids", lambda self: [])
    with pytest.raises(NoActiveDatasetException):
        service.get_dashboard_summary()

    # Restore the original get_active_dataset_ids for the rest of the test
    monkeypatch.undo()

    # Create two ready datasets
    ds1 = Dataset(name="ds1", display_name="DS 1", original_filename="ds1.csv", source_type="CSV", status="Ready", is_active=True)
    ds2 = Dataset(name="ds2", display_name="DS 2", original_filename="ds2.csv", source_type="CSV", status="Ready", is_active=False)
    db_session.add_all([ds1, ds2])
    db_session.commit()

    # Add crime events
    c1 = CrimeEvent(dataset_id=ds1.id, crime_type="Theft", crime_category="Property", severity=4.0, crime_date=date(2025, 5, 10), status="reported")
    c2 = CrimeEvent(dataset_id=ds2.id, crime_type="Assault", crime_category="Violent", severity=7.0, crime_date=date(2025, 5, 11), status="reported")
    db_session.add_all([c1, c2])
    db_session.commit()

    # Clear caches before starting test to isolate
    AnalyticsCache.clear()

    # 2. Test analytics loading from ds1
    summary = service.get_dashboard_summary()
    assert summary["total_crimes"] == 1
    assert summary["average_severity"] == 4.0

    # 3. Test caching hit
    # Modify data directly in the database without updating the dataset timestamp to test cache persistence
    c1.severity = 10.0
    db_session.commit()
    
    # Cache hit should return the old average severity (4.0)
    summary_cached = service.get_dashboard_summary()
    assert summary_cached["average_severity"] == 4.0

    # 4. Invalidate cache: update the dataset's updated_at timestamp
    ds1.updated_at = datetime.utcnow()
    db_session.commit()
    
    # Re-fetch -> cache miss, recompute -> average severity becomes 10.0
    summary_new = service.get_dashboard_summary()
    assert summary_new["average_severity"] == 10.0

    # 5. Multi-dataset combination: activate ds2 as well
    # Set limit to 2 first
    from backend.models.dataset import DatasetConfig
    config = db_session.query(DatasetConfig).first()
    if config:
        config.max_active_datasets = "2"
    else:
        db_session.add(DatasetConfig(max_active_datasets="2"))
    db_session.commit()

    ds2.is_active = True
    db_session.commit()

    # Analytics should now combine ds1 and ds2 (total crimes = 2)
    summary_multi = service.get_dashboard_summary()
    assert summary_multi["total_crimes"] == 2


def test_ml_pipeline_and_registry(client_as_admin, db_session, monkeypatch):
    from backend.models.dataset import Dataset
    from backend.models.crime import CrimeEvent
    from backend.models.criminal import Criminal
    from backend.models.crime_participation import CrimeParticipation
    from backend.models.location import Location
    from backend.models.ml_model import MLModel
    from backend.services.ml_training_service import MLTrainingService
    from backend.services.prediction_service import PredictionService
    from datetime import date
    import pytest
    import os

    # Mock SessionLocal to return the test db_session
    from backend.services import ml_training_service
    monkeypatch.setattr(ml_training_service, "SessionLocal", lambda: db_session)
    monkeypatch.setattr(db_session, "close", lambda: None)
    monkeypatch.setattr(db_session, "commit", db_session.flush)

    # Prevent background threads from running to avoid concurrency issues with SQLite in-memory
    import threading
    monkeypatch.setattr(threading.Thread, "start", lambda self: None)

    # 1. Clean DB
    db_session.query(MLModel).delete()
    db_session.query(Dataset).delete()
    db_session.flush()

    service = MLTrainingService(db_session)

    # Validate dataset raises ValueError on empty active_ids
    with pytest.raises(Exception):
        service.validate_dataset_for_ml("repeat_offender", [])

    # Seed dataset and 12 criminals + events to pass validation
    ds = Dataset(name="ml_ds", display_name="ML DS", original_filename="ml.csv", source_type="CSV", status="Ready", is_active=True)
    db_session.add(ds)
    db_session.commit()

    loc = Location(district="D1", latitude=12.0, longitude=77.0)
    db_session.add(loc)
    db_session.commit()

    for i in range(40):
        score = 0.85 if i % 2 == 0 else 0.20
        c = Criminal(dataset_id=ds.id, name=f"Criminal {i}", age=25.0 + i, occupation="Unemployed", caste="General", risk_score=score)
        ce = CrimeEvent(dataset_id=ds.id, location_id=loc.id, crime_type="Theft", crime_category="Property", severity=4.0, crime_date=date(2025, 5, 10), status="reported")
        db_session.add_all([c, ce])
        db_session.commit()
        
        cp = CrimeParticipation(dataset_id=ds.id, criminal_id=c.id, crime_event_id=ce.id, role="accused")
        db_session.add(cp)
        db_session.commit()

    # 2. Trigger retraining (returns Queued model)
    model = service.trigger_retraining("repeat_offender")
    assert model.status == "Queued"
    assert model.is_production is False

    # 3. Execute training pipeline synchronously in test
    service._run_training_pipeline_thread(model.id, [ds.id])

    # Refresh and assert completed status
    db_session.refresh(model)
    if model.status == "Failed":
        raise Exception(f"Training failed. Logs:\n{model.training_logs}")
    assert model.status == "Completed"
    assert model.accuracy is not None
    assert model.is_production is True
    assert model.model_path is not None
    assert os.path.exists(model.model_path)

    # 4. Trigger second training
    model2 = service.trigger_retraining("repeat_offender")
    service._run_training_pipeline_thread(model2.id, [ds.id])
    db_session.refresh(model2)
    assert model2.status == "Completed"
    assert model2.is_production is False  # First model is still production

    # 5. Promoted to production
    service.mark_production(model2.id)
    db_session.refresh(model)
    db_session.refresh(model2)
    assert model.is_production is False
    assert model2.is_production is True

    # 6. Verify prediction uses the new production model
    pred_service = PredictionService(db_session)
    res = pred_service.predict_repeat_offender(age=30, occupation="Unemployed", caste="General", district="D1")
    assert "probability" in res
    assert "risk_level" in res

    # 7. Rollback to first model
    service.rollback_model(model.id)
    db_session.refresh(model)
    db_session.refresh(model2)
    assert model.is_production is True
    assert model2.is_production is False

    # 8. Clean up created model files
    path1, path2 = model.model_path, model2.model_path
    service.delete_model(model.id)
    service.delete_model(model2.id)
    assert not os.path.exists(path1)
    assert not os.path.exists(path2)


def test_dataset_permanent_delete(client_as_admin, db_session):
    # 0. Seed default dataset by listing datasets
    client_as_admin.get("/api/v1/admin/datasets/")

    # 1. Upload new dataset
    csv_content = (
        "fir_id,crime_type,crime_date,crime_time,district,police_station,victim_age,accused_age,gender,occupation,repeat_offender,severity,status\n"
        "FIR999,Theft,2025-05-10,14:30,Bengaluru,Koramangala PS,34,22,Male,Driver,1,3.0,reported\n"
    )
    file_payload = {"file": ("test_perm_del.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    form_data = {"display_name": "Test Perm Delete", "description": "Temp dataset"}
    
    response = client_as_admin.post(
        "/api/v1/admin/datasets/upload",
        data=form_data,
        files=file_payload
    )
    assert response.status_code == 200
    ds = response.json()
    ds_id = ds["id"]

    # Verify records created
    crimes = db_session.query(CrimeEvent).filter(CrimeEvent.dataset_id == ds_id).all()
    assert len(crimes) == 1

    # 2. Try to permanent delete
    response = client_as_admin.delete(f"/api/v1/admin/datasets/{ds_id}/permanent")
    assert response.status_code == 200
    assert response.json()["detail"] == "Dataset and all associated records permanently deleted."

    # Verify database clean
    assert db_session.query(Dataset).filter(Dataset.id == ds_id).first() is None
    crimes_after = db_session.query(CrimeEvent).filter(CrimeEvent.dataset_id == ds_id).all()
    assert len(crimes_after) == 0

    # 3. Test archiving, then uploading again with same name works
    # Upload first time
    file_payload = {"file": ("test_perm_del.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    response = client_as_admin.post(
        "/api/v1/admin/datasets/upload",
        data=form_data,
        files=file_payload
    )
    assert response.status_code == 200
    ds1 = response.json()
    ds1_id = ds1["id"]

    # Soft delete (Archive) it
    response = client_as_admin.delete(f"/api/v1/admin/datasets/{ds1_id}")
    assert response.status_code == 200

    # Upload same file again (should succeed because it's archived)
    file_payload_2 = {"file": ("test_perm_del.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    response = client_as_admin.post(
        "/api/v1/admin/datasets/upload",
        data={"display_name": "Test Perm Delete 2", "description": "Temp dataset 2"},
        files=file_payload_2
    )
    assert response.status_code == 200
    ds2 = response.json()
    ds2_id = ds2["id"]
    assert ds1_id != ds2_id

    # Clean up both permanently
    client_as_admin.delete(f"/api/v1/admin/datasets/{ds1_id}/permanent")
    client_as_admin.delete(f"/api/v1/admin/datasets/{ds2_id}/permanent")





