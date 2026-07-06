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
    # 1. Get initial dataset list (should auto-seed default dataset)
    response = client_as_admin.get("/api/v1/admin/datasets/")
    assert response.status_code == 200
    datasets = response.json()
    assert len(datasets) == 1
    assert datasets[0]["name"] == "System Seed"
    assert datasets[0]["is_active"] is True
    
    default_dataset_id = datasets[0]["id"]

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
    assert new_ds["is_active"] is False
    
    new_dataset_id = new_ds["id"]
    
    # Verify records are created with the new dataset_id
    crimes = db_session.query(CrimeEvent).filter(CrimeEvent.dataset_id == new_dataset_id).all()
    assert len(crimes) == 2
    assert crimes[0].crime_type == "Theft"

    # 3. Switch active dataset to the new one
    response = client_as_admin.post(
        "/api/v1/admin/datasets/activate",
        json={"dataset_id": new_dataset_id}
    )
    assert response.status_code == 200
    activated_ds = response.json()
    assert activated_ds["is_active"] is True
    
    # Check that previous dataset is deactivated
    old_ds = db_session.query(Dataset).filter(Dataset.id == default_dataset_id).first()
    assert old_ds.is_active is False

    # 4. Attempt to delete active dataset (should fail because it's active)
    response = client_as_admin.delete(f"/api/v1/admin/datasets/{new_dataset_id}")
    assert response.status_code != 200

    # 5. Attempt to delete protected "System Seed" dataset (should fail)
    response = client_as_admin.delete(f"/api/v1/admin/datasets/{default_dataset_id}")
    assert response.status_code != 200

    # 6. Switch active dataset back to default, then soft delete new dataset
    response = client_as_admin.post(
        "/api/v1/admin/datasets/activate",
        json={"dataset_id": default_dataset_id}
    )
    assert response.status_code == 200

    # Now delete the deactivated new dataset
    response = client_as_admin.delete(f"/api/v1/admin/datasets/{new_dataset_id}")
    assert response.status_code == 200
    assert response.json()["detail"] == "Dataset deleted successfully."

    # Verify soft delete: status becomes Archived
    deleted_ds = db_session.query(Dataset).filter(Dataset.id == new_dataset_id).first()
    assert deleted_ds.status == "Archived"
    assert deleted_ds.is_active is False

    # Check that associated crime events are NOT deleted (soft delete keeps data for auditability)
    crimes_after_delete = db_session.query(CrimeEvent).filter(CrimeEvent.dataset_id == new_dataset_id).all()
    assert len(crimes_after_delete) == 2

    # 7. Test dataset summary API
    response = client_as_admin.get(f"/api/v1/admin/datasets/{default_dataset_id}/summary")
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

def test_new_dataset_features(client_as_admin, db_session):
    # Get auto-seeded default dataset ID
    response = client_as_admin.get("/api/v1/admin/datasets/")
    assert response.status_code == 200
    datasets = response.json()
    default_dataset_id = datasets[0]["id"]

    # 1. Test Dataset Details API
    resp_details = client_as_admin.get(f"/api/v1/admin/datasets/{default_dataset_id}")
    assert resp_details.status_code == 200
    details = resp_details.json()
    assert details["name"] == "System Seed"
    assert details["original_filename"] == "crime_events.csv"
    assert "column_count" in details
    assert "upload_status" in details
    assert "storage_path" in details

    # 2. Test Dataset Preview API
    resp_preview = client_as_admin.get(f"/api/v1/admin/datasets/{default_dataset_id}/preview")
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
    resp_stats = client_as_admin.get(f"/api/v1/admin/datasets/{default_dataset_id}/statistics")
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

