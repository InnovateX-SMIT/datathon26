import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.core.database import Base, get_db
from backend.api.auth.router import get_current_user
from backend.app.main import app
from backend.models.recommendation import Recommendation, ResourceAllocation
from backend.models.police_station import PoliceStation
from backend.models.location import Location

# Test database setup (in-memory SQLite)
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
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def override_get_current_user():
        return {"email": "admin@police.gov.in", "role": "admin"}

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

def test_solve_resource_allocation_api_fail_no_stations(client):
    payload = {
        "district": "Unknown District",
        "sanctioned_asi": 5,
        "sanctioned_chc": 10,
        "sanctioned_cpc": 30
    }
    response = client.post("/api/v1/recommendations/solve", json=payload)
    assert response.status_code == 404
    assert "No police stations found" in response.json()["detail"]

def test_solve_resource_allocation_api_success(client, db_session):
    # Seed location and police station
    loc = Location(district="Mysuru", state="Karnataka", latitude=12.2958, longitude=76.6394)
    db_session.add(loc)
    db_session.commit()
    db_session.refresh(loc)

    ps = PoliceStation(station_name="Mysuru Town", district="Mysuru", beat="Beat A", location_id=loc.id, capacity=50)
    db_session.add(ps)
    db_session.commit()

    payload = {
        "district": "Mysuru",
        "sanctioned_asi": 5,
        "sanctioned_chc": 10,
        "sanctioned_cpc": 30
    }
    response = client.post("/api/v1/recommendations/solve", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["district"] == "Mysuru"
    assert len(data["solved_allocation"]) == 1
    assert data["solved_allocation"][0]["beat_name"] == "Mysuru Town"
    assert data["solved_allocation"][0]["asi_allocated"] == 5
    assert data["solved_allocation"][0]["cpc_allocated"] == 30

def test_get_resource_allocation_history_api(client, db_session):
    # Seed a ResourceAllocation log
    alloc = ResourceAllocation(
        district="Bengaluru Urban",
        allocated_asi=10,
        allocated_chc=25,
        allocated_cpc=70,
        solved_allocation='[{"beat_name": "Beat Alpha", "asi_allocated": 10, "chc_allocated": 25, "cpc_allocated": 70, "normalized_severity": 1.0}]'
    )
    db_session.add(alloc)
    db_session.commit()

    response = client.get("/api/v1/recommendations/resource-allocation")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["district"] == "Bengaluru Urban"
    assert len(data[0]["solved_allocation"]) == 1
    assert data[0]["solved_allocation"][0]["beat_name"] == "Beat Alpha"

def test_get_recommendations_api(client, db_session):
    # Seed recommendations
    rec1 = Recommendation(priority="high", recommendation_text="Deploy patrols", status="pending")
    rec2 = Recommendation(priority="low", recommendation_text="Check-ins", status="resolved")
    db_session.add_all([rec1, rec2])
    db_session.commit()

    # Get all
    response = client.get("/api/v1/recommendations")
    assert response.status_code == 200
    assert len(response.json()) == 2

    # Filter by status
    response = client.get("/api/v1/recommendations?status=resolved")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["status"] == "resolved"

    # Filter by priority
    response = client.get("/api/v1/recommendations?priority=high")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["priority"] == "high"

def test_generate_recommendations_api(client):
    response = client.post("/api/v1/recommendations/generate")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["status"] == "pending"

def test_update_recommendation_status_api(client, db_session):
    rec = Recommendation(priority="high", recommendation_text="Deploy patrols", status="pending")
    db_session.add(rec)
    db_session.commit()
    db_session.refresh(rec)

    payload = {"status": "resolved"}
    response = client.put(f"/api/v1/recommendations/{rec.id}", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "resolved"
    
    # Verify in DB
    db_rec = db_session.query(Recommendation).filter(Recommendation.id == rec.id).first()
    assert db_rec.status == "resolved"
