import pytest
from datetime import date, datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.core.database import Base, get_db
from backend.api.auth.router import get_current_user
from backend.models.crime import CrimeEvent
from backend.models.criminal import Criminal
from backend.models.location import Location
from backend.models.user import User, UserRole
from backend.app.main import app

# Setup test DB (in-memory SQLite)
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
    try:
        # Seed active dataset
        from backend.models.dataset import Dataset
        ds = Dataset(id=1, name="test_report", original_filename="test_report.csv", display_name="Test Report", is_active=True, status="Ready", upload_status="Completed")
        db.add(ds)
        db.flush()

        # Seed test tables
        loc = Location(state="Karnataka", district="Bengaluru Urban", latitude=12.97, longitude=77.59)
        db.add(loc)
        db.commit()
        db.refresh(loc)

        crimes = [
            CrimeEvent(
                dataset_id=1,
                crime_type="Theft",
                crime_category="Theft",
                crime_subcategory="Vehicle Theft",
                crime_date=date(2026, 6, 1),
                victim_count=1,
                accused_count=1,
                status="reported",
                location_id=loc.id,
                severity=2.0
            ),
            CrimeEvent(
                dataset_id=1,
                crime_type="Assault",
                crime_category="Violent Crime",
                crime_subcategory="Simple Assault",
                crime_date=date(2026, 6, 2),
                victim_count=2,
                accused_count=1,
                status="reported",
                location_id=loc.id,
                severity=3.5
            )
        ]
        db.add_all(crimes)
        db.commit()

        criminals = [
            Criminal(dataset_id=1, name="Raman", risk_score=8.5, status="active", age=28.0, gender="Male", occupation="None", caste="General"),
            Criminal(dataset_id=1, name="Shekhar", risk_score=4.2, status="active", age=32.0, gender="Male", occupation="Laborer", caste="OBC")
        ]
        db.add_all(criminals)
        db.commit()



        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client_superintendent(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def override_get_current_user():
        # returns superintendent role
        return User(id=1, email="sp@police.gov.in", name="Superintendent Patil", role=UserRole.SUPERINTENDENT, status="active")

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def client_officer(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def override_get_current_user():
        # returns regular officer role (clearance failure)
        return User(id=2, email="officer@police.gov.in", name="Officer Sharma", role=UserRole.OFFICER, status="active")

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

def test_get_report_types(client_superintendent):
    response = client_superintendent.get("/api/v1/reports/types")
    assert response.status_code == 200
    data = response.json()
    assert "types" in data
    assert len(data["types"]) == 5
    keys = [x["key"] for x in data["types"]]
    assert "district_intelligence" in keys
    assert "executive_summary" in keys

def test_officer_access_denied(client_officer):
    # officer role should fail with 403 Forbidden
    response = client_officer.get("/api/v1/reports/types")
    assert response.status_code == 403

    response = client_officer.get("/api/v1/reports/")
    assert response.status_code == 403

def test_generate_and_retrieve_report(client_superintendent):
    # 1. Generate Report
    payload = {
        "title": "Quarterly Intel Review",
        "report_type": "district_intelligence"
    }
    response = client_superintendent.post("/api/v1/reports/generate", json=payload)
    assert response.status_code == 201
    report_data = response.json()
    
    assert "report_id" in report_data
    assert report_data["title"] == "Quarterly Intel Review"
    assert report_data["report_type"] == "district_intelligence"
    assert "executive_summary" in report_data
    assert "District Intelligence Briefing" in report_data["executive_summary"]
    
    # Check overview section
    overview = report_data["crime_overview"]
    assert overview["total_crimes"] == 2
    assert len(overview["top_categories"]) > 0

    # Check predictions section
    preds = report_data["predictive_insights"]
    assert preds["hotspot_count"] == 0
    assert preds["risk_score_summary"]["high_risk_criminals_count"] == 1
    
    # 2. Get list of reports
    list_resp = client_superintendent.get("/api/v1/reports/")
    assert list_resp.status_code == 200
    list_data = list_resp.json()
    assert len(list_data) == 1
    assert list_data[0]["title"] == "Quarterly Intel Review"

    # 3. Retrieve single report by ID
    report_id = list_data[0]["report_id"]
    get_resp = client_superintendent.get(f"/api/v1/reports/{report_id}")
    assert get_resp.status_code == 200
    retrieved_data = get_resp.json()
    assert retrieved_data["report_id"] == report_id
    assert retrieved_data["crime_overview"]["total_crimes"] == 2

def test_get_invalid_report_id(client_superintendent):
    response = client_superintendent.get("/api/v1/reports/99999")
    assert response.status_code == 404

def test_download_report_csv_success(client_superintendent):
    # 1. Generate Report
    payload = {
        "title": "Quarterly Export review",
        "report_type": "district_intelligence"
    }
    response = client_superintendent.post("/api/v1/reports/generate", json=payload)
    assert response.status_code == 201
    report_id = response.json()["report_id"]

    # 2. Download Report
    dl_resp = client_superintendent.get(f"/api/v1/reports/{report_id}/download")
    assert dl_resp.status_code == 200
    assert dl_resp.headers["content-type"] == "text/csv; charset=utf-8"
    assert f"attachment; filename=dossier_intel_{report_id}.csv" in dl_resp.headers["content-disposition"]
    csv_content = dl_resp.text
    assert "EXECUTIVE BRIEFING DOSSIER" in csv_content
    assert "SECTION I: CRIME ANALYTICS OVERVIEW" in csv_content

def test_download_report_csv_not_found(client_superintendent):
    response = client_superintendent.get("/api/v1/reports/99999/download")
    assert response.status_code == 404
