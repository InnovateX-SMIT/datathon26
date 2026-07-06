import pytest
import io
import json
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.core.database import Base, get_db
from backend.api.auth.router import get_current_user
from backend.app.main import app
from backend.models.location import Location
from backend.models.criminal import Criminal
from backend.models.crime import CrimeEvent

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
def client_as_officer(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def mock_officer_user():
        return {"id": 2, "email": "officer@police.gov.in", "role": "OFFICER", "status": "active"}

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = mock_officer_user
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_database_stats_as_admin(client_as_admin, db_session):
    # Seed a criminal
    criminal = Criminal(name="John Doe", risk_score=0.8, status="accused")
    db_session.add(criminal)
    db_session.commit()

    response = client_as_admin.get("/api/v1/admin/database/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["health"] == "healthy"
    assert data["counts"]["criminals"] == 1
    assert data["counts"]["crime_events"] == 0
    assert data["last_updated"]["criminals"] is not None


def test_database_stats_requires_admin(client_as_officer):
    response = client_as_officer.get("/api/v1/admin/database/stats")
    assert response.status_code == 403


def test_crud_criminal(client_as_admin, db_session):
    # 1. Create
    payload = {
        "name": "Jane Miller",
        "gender": "Female",
        "age": 32.5,
        "occupation": "Technician",
        "risk_score": 0.45,
        "status": "suspect"
    }
    response = client_as_admin.post("/api/v1/admin/database/criminals", json=payload)
    assert response.status_code == 201
    created = response.json()
    assert created["id"] is not None
    assert created["name"] == "Jane Miller"
    assert created["risk_score"] == 0.45

    # 2. Read / Search
    response = client_as_admin.get("/api/v1/admin/database/criminals")
    assert response.status_code == 200
    grid_data = response.json()
    assert grid_data["total"] == 1
    assert grid_data["records"][0]["name"] == "Jane Miller"

    # Search query
    response = client_as_admin.get("/api/v1/admin/database/criminals?q=Jane")
    assert response.json()["total"] == 1

    # Empty search match
    response = client_as_admin.get("/api/v1/admin/database/criminals?q=Nonexistent")
    assert response.json()["total"] == 0

    # 3. Read single record
    rec_id = created["id"]
    response = client_as_admin.get(f"/api/v1/admin/database/criminals/{rec_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Jane Miller"

    # 4. Update
    update_payload = {
        "name": "Jane Miller-Smith",
        "risk_score": 0.20,
        "status": "acquitted"
    }
    response = client_as_admin.put(f"/api/v1/admin/database/criminals/{rec_id}", json=update_payload)
    assert response.status_code == 200
    updated = response.json()
    assert updated["name"] == "Jane Miller-Smith"
    assert updated["risk_score"] == 0.20
    assert updated["status"] == "acquitted"

    # 5. Delete
    response = client_as_admin.delete(f"/api/v1/admin/database/criminals/{rec_id}")
    assert response.status_code == 200
    
    # Verify deletion
    response = client_as_admin.get(f"/api/v1/admin/database/criminals/{rec_id}")
    assert response.status_code == 404


def test_invalid_field_validation(client_as_admin):
    # Required name is missing
    payload = {
        "risk_score": 0.5
    }
    response = client_as_admin.post("/api/v1/admin/database/criminals", json=payload)
    assert response.status_code == 400
    assert "validation" in response.json()["detail"].lower() or "missing" in response.json()["detail"].lower()


def test_bulk_upload_validation_and_import(client_as_admin, db_session):
    # Create CSV file with 1 valid row and 1 invalid row (missing district)
    csv_content = (
        "state,district,latitude,longitude\n"
        "Karnataka,Bangalore Urban,12.97,77.59\n"
        "Karnataka,,13.01,77.62\n"  # missing required district
    )
    
    file_payload = {
        "file": ("locations.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")
    }

    # 1. Preview mode (should not save to DB)
    response = client_as_admin.post(
        "/api/v1/admin/database/locations/bulk-upload?preview=true",
        files=file_payload
    )
    assert response.status_code == 200
    preview_data = response.json()
    assert preview_data["total_rows"] == 2
    assert preview_data["valid_count"] == 1
    assert preview_data["invalid_count"] == 1
    assert len(preview_data["errors"]) == 1
    assert preview_data["errors"][0]["row"] == 3 # row index 3 is invalid

    # DB should still be empty
    assert db_session.query(Location).count() == 0

    # 2. Import mode (should save only the valid row)
    file_payload_import = {
        "file": ("locations.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")
    }
    response = client_as_admin.post(
        "/api/v1/admin/database/locations/bulk-upload?preview=false",
        files=file_payload_import
    )
    assert response.status_code == 200
    import_data = response.json()
    assert import_data["valid_count"] == 1
    
    # Check DB count
    assert db_session.query(Location).count() == 1
    seeded_loc = db_session.query(Location).first()
    assert seeded_loc.district == "Bangalore Urban"


def test_export_data(client_as_admin, db_session):
    # Seed locations
    loc1 = Location(state="Karnataka", district="Bangalore", latitude=12.0, longitude=77.0)
    loc2 = Location(state="Karnataka", district="Mysore", latitude=12.2, longitude=76.6)
    db_session.add_all([loc1, loc2])
    db_session.commit()

    # 1. Export as CSV
    response = client_as_admin.get("/api/v1/admin/database/locations/export?export_format=csv")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    csv_bytes = response.content
    csv_str = csv_bytes.decode("utf-8")
    assert "Bangalore" in csv_str
    assert "Mysore" in csv_str

    # 2. Export as Excel
    response = client_as_admin.get("/api/v1/admin/database/locations/export?export_format=excel")
    assert response.status_code == 200
    assert "vnd.openxmlformats-officedocument" in response.headers["content-type"]
