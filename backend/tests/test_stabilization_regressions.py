"""
Regression tests for the stabilization phase.
Tests BUG 1 (Dataset Registry), BUG 2 (Import Header Normalization),
BUG 3 (Dataset Activation UX), and BUG 4 (Executive Reports 500).
"""
import pytest
import io
import json
from datetime import date, datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.core.database import Base, get_db
from backend.api.auth.router import get_current_user
from backend.app.main import app
from backend.models.dataset import Dataset
from backend.models.crime import CrimeEvent
from backend.models.criminal import Criminal
from backend.models.location import Location
from backend.models.police_station import PoliceStation
from backend.models.report import Report
from backend.models.user import User, UserRole

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
    # Seed location and station master data for import tests
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


@pytest.fixture(scope="function")
def client_superintendent(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def override_get_current_user():
        return User(id=1, email="sp@police.gov.in", name="Superintendent Patil",
                    role=UserRole.SUPERINTENDENT, status="active")

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# ── BUG 1 REGRESSION: Dataset Registry Always Loads ──────────────────────────

class TestDatasetRegistryLoads:
    """BUG 1: Dataset Registry page must always load with at least System Seed."""

    def test_registry_returns_datasets_on_first_call(self, client_as_admin):
        """Registry must auto-seed System Seed and return at least one dataset."""
        response = client_as_admin.get("/api/v1/admin/datasets/")
        assert response.status_code == 200
        datasets = response.json()
        assert len(datasets) >= 1, "Registry should auto-seed System Seed"
        system_seed = next((d for d in datasets if d["name"] == "System Seed"), None)
        assert system_seed is not None, "System Seed must exist"
        assert system_seed["is_active"] is True, "System Seed should be active by default"

    def test_registry_response_contains_all_fields(self, client_as_admin):
        """All DatasetResponse fields must be present without serialization errors."""
        response = client_as_admin.get("/api/v1/admin/datasets/")
        assert response.status_code == 200
        datasets = response.json()
        ds = datasets[0]
        # All required fields present (even if null for optional ones)
        assert "id" in ds
        assert "name" in ds
        assert "display_name" in ds
        assert "original_filename" in ds
        assert "source_type" in ds
        assert "status" in ds
        assert "is_active" in ds
        assert "row_count" in ds
        assert "file_size" in ds

    def test_active_dataset_always_visible(self, client_as_admin):
        """At least one dataset must be active."""
        response = client_as_admin.get("/api/v1/admin/datasets/")
        assert response.status_code == 200
        datasets = response.json()
        active = [d for d in datasets if d["is_active"]]
        assert len(active) == 1, "Exactly one dataset should be active"


# ── BUG 2 REGRESSION: Import Header Normalization ────────────────────────────

class TestImportHeaderNormalization:
    """BUG 2: Import must handle various header formats via normalization."""

    def test_import_csv_with_standard_headers(self, client_as_admin):
        """Standard lowercase underscore headers should import cleanly."""
        csv_content = (
            "fir_id,crime_type,crime_date,crime_time,district,police_station,victim_age,accused_age,gender,occupation,repeat_offender,severity,status\n"
            "FIR001,Theft,2025-05-10,14:30,Bengaluru,Koramangala PS,34,22,Male,Driver,1,3.0,reported\n"
        )
        file_payload = {"file": ("test.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
        form_data = {"display_name": "Standard CSV"}
        response = client_as_admin.post("/api/v1/admin/datasets/upload", data=form_data, files=file_payload)
        assert response.status_code == 200
        ds = response.json()
        assert ds["row_count"] == 1
        assert ds["status"] == "Ready"

    def test_import_csv_with_title_case_headers(self, client_as_admin):
        """Title Case headers like 'Crime Type' should normalize correctly."""
        csv_content = (
            "FIR ID,Crime Type,Crime Date,Crime Time,District,Police Station,Victim Age,Accused Age,Gender,Occupation,Repeat Offender,Severity,Status\n"
            "FIR001,Theft,2025-05-10,14:30,Bengaluru,Koramangala PS,34,22,Male,Driver,1,3.0,reported\n"
        )
        file_payload = {"file": ("title_case.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
        form_data = {"display_name": "Title Case CSV"}
        response = client_as_admin.post("/api/v1/admin/datasets/upload", data=form_data, files=file_payload)
        assert response.status_code == 200
        ds = response.json()
        assert ds["row_count"] == 1

    def test_import_csv_with_uppercase_headers(self, client_as_admin):
        """ALL CAPS headers should normalize correctly."""
        csv_content = (
            "FIR_ID,CRIME_TYPE,CRIME_DATE,CRIME_TIME,DISTRICT,POLICE_STATION,VICTIM_AGE,ACCUSED_AGE,GENDER,OCCUPATION,REPEAT_OFFENDER,SEVERITY,STATUS\n"
            "FIR001,Theft,2025-05-10,14:30,Bengaluru,Koramangala PS,34,22,Male,Driver,1,3.0,reported\n"
        )
        file_payload = {"file": ("upper.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
        form_data = {"display_name": "Upper Case CSV"}
        response = client_as_admin.post("/api/v1/admin/datasets/upload", data=form_data, files=file_payload)
        assert response.status_code == 200
        ds = response.json()
        assert ds["row_count"] == 1

    def test_import_csv_with_alias_headers(self, client_as_admin):
        """Alias headers like 'CrimeType', 'PoliceStation' should work."""
        csv_content = (
            "FirId,CrimeType,CrimeDate,CrimeTime,District,PoliceStation,VictimAge,AccusedAge,Gender,Occupation,RepeatOffender,Severity,Status\n"
            "FIR001,Theft,2025-05-10,14:30,Bengaluru,Koramangala PS,34,22,Male,Driver,1,3.0,reported\n"
        )
        file_payload = {"file": ("alias.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
        form_data = {"display_name": "Alias CSV"}
        response = client_as_admin.post("/api/v1/admin/datasets/upload", data=form_data, files=file_payload)
        assert response.status_code == 200
        ds = response.json()
        assert ds["row_count"] == 1

    def test_import_csv_with_whitespace_headers(self, client_as_admin):
        """Headers with leading/trailing whitespace should be trimmed."""
        csv_content = (
            " fir_id , crime_type , crime_date , crime_time , district , police_station ,victim_age,accused_age,gender,occupation,repeat_offender,severity,status\n"
            "FIR001,Theft,2025-05-10,14:30,Bengaluru,Koramangala PS,34,22,Male,Driver,1,3.0,reported\n"
        )
        file_payload = {"file": ("whitespace.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
        form_data = {"display_name": "Whitespace CSV"}
        response = client_as_admin.post("/api/v1/admin/datasets/upload", data=form_data, files=file_payload)
        assert response.status_code == 200
        ds = response.json()
        assert ds["row_count"] == 1

    def test_import_csv_missing_required_columns_gives_clear_error(self, client_as_admin):
        """Missing required columns should return a clear error listing columns found."""
        csv_content = (
            "id,name,value\n"
            "1,Test,100\n"
        )
        file_payload = {"file": ("bad.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
        form_data = {"display_name": "Bad CSV"}
        response = client_as_admin.post("/api/v1/admin/datasets/upload", data=form_data, files=file_payload)
        assert response.status_code == 400
        detail = response.json().get("detail", "")
        assert "Missing required columns" in detail
        assert "Columns found in file" in detail


# ── BUG 3 REGRESSION: Dataset Activation ─────────────────────────────────────

class TestDatasetActivation:
    """BUG 3: Dataset activation must clearly switch and reflect active state."""

    def test_activate_switches_active_dataset(self, client_as_admin, db_session):
        """Activating a dataset should deactivate the previous one."""
        # Get initial datasets (auto-seeded)
        resp = client_as_admin.get("/api/v1/admin/datasets/")
        assert resp.status_code == 200
        datasets = resp.json()
        seed_id = datasets[0]["id"]
        assert datasets[0]["is_active"] is True

        # Upload new dataset
        csv_content = (
            "fir_id,crime_type,crime_date,crime_time,district,police_station,victim_age,accused_age,gender,occupation,repeat_offender,severity,status\n"
            "FIR001,Theft,2025-05-10,14:30,Bengaluru,Koramangala PS,34,22,Male,Driver,1,3.0,reported\n"
        )
        file_payload = {"file": ("switch.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
        form_data = {"display_name": "Switch Target"}
        upload_resp = client_as_admin.post("/api/v1/admin/datasets/upload", data=form_data, files=file_payload)
        assert upload_resp.status_code == 200
        new_id = upload_resp.json()["id"]

        # Activate new dataset
        activate_resp = client_as_admin.post("/api/v1/admin/datasets/activate", json={"dataset_id": new_id})
        assert activate_resp.status_code == 200
        activated = activate_resp.json()
        assert activated["is_active"] is True

        # Verify old dataset is deactivated
        list_resp = client_as_admin.get("/api/v1/admin/datasets/")
        datasets = list_resp.json()
        active_count = sum(1 for d in datasets if d["is_active"])
        assert active_count == 1, "Only one dataset should be active"

    def test_active_badge_data_present(self, client_as_admin):
        """Every dataset response must include is_active field for UI badge."""
        resp = client_as_admin.get("/api/v1/admin/datasets/")
        for ds in resp.json():
            assert "is_active" in ds


# ── BUG 4 REGRESSION: Executive Reports No 500 ──────────────────────────────

class TestReportDetailsNoServerError:
    """BUG 4: GET /reports/{id} must never return 500 for existing reports."""

    def test_report_detail_for_legacy_report_without_payload(self, client_superintendent, db_session):
        """Legacy reports without data_payload should still load via slow-path reassembly."""
        # Manually insert a legacy report without data_payload
        legacy = Report(
            title="Legacy Report",
            report_type="crime_trend",
            summary="A legacy summary",
            data_payload=None,
            generated_at=datetime.utcnow()
        )
        db_session.add(legacy)
        db_session.commit()
        db_session.refresh(legacy)

        response = client_superintendent.get(f"/api/v1/reports/{legacy.id}")
        assert response.status_code == 200, f"Expected 200 but got {response.status_code}: {response.text}"
        data = response.json()
        assert data["report_id"] == legacy.id
        assert data["title"] == "Legacy Report"
        assert "crime_overview" in data
        assert "predictive_insights" in data
        assert "network_insights" in data
        assert "recommendations" in data
        assert "alerts" in data

    def test_report_detail_for_generated_report(self, client_superintendent):
        """Newly generated reports should load from cached data_payload."""
        payload = {"title": "Test Report", "report_type": "executive_summary"}
        gen_resp = client_superintendent.post("/api/v1/reports/generate", json=payload)
        assert gen_resp.status_code == 201
        report_id = gen_resp.json()["report_id"]

        detail_resp = client_superintendent.get(f"/api/v1/reports/{report_id}")
        assert detail_resp.status_code == 200
        data = detail_resp.json()
        assert data["report_id"] == report_id
        assert data["title"] == "Test Report"

    def test_nonexistent_report_returns_404(self, client_superintendent):
        """Non-existent report ID should return 404, not 500."""
        response = client_superintendent.get("/api/v1/reports/99999")
        assert response.status_code == 404
