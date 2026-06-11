import pytest
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
from backend.models.crime_participation import CrimeParticipation

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
        # Seed test data
        loc = Location(id=5, state="Karnataka", district="Mysuru", latitude=12.30, longitude=76.64)
        crim = Criminal(id=1, name="Jane Smith", gender="Female", age=28.0, occupation="Cashier", caste="OBC", risk_score=0.4, status="accused")
        crime = CrimeEvent(id=10, crime_type="Robbery", crime_category="Violent Crime", crime_subcategory="Bank Robbery", severity=3.0, status="reported", crime_date=date(2026, 6, 12), location_id=5)
        part = CrimeParticipation(id=1, crime_event_id=10, criminal_id=1, role="accused")
        
        db.add(loc)
        db.add(crim)
        db.add(crime)
        db.add(part)
        db.commit()
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

def test_get_criminal_network_success(client):
    response = client.get("/api/v1/network/criminal/1")
    assert response.status_code == 200
    data = response.json()
    
    assert "nodes" in data
    assert "edges" in data
    assert data["total_nodes"] == 3
    assert data["total_edges"] == 2
    
    # Check node details
    nodes = {n["id"]: n for n in data["nodes"]}
    assert "criminal_1" in nodes
    assert nodes["criminal_1"]["type"] == "criminal"
    assert nodes["criminal_1"]["label"] == "Jane Smith"
    assert "gender" in nodes["criminal_1"]["metadata"]
    
    # Check edges details
    edges = data["edges"]
    assert any(e["source"] == "criminal_1" and e["target"] == "crime_10" and e["relationship"] == "INVOLVED_IN" for e in edges)

def test_get_criminal_network_not_found(client):
    response = client.get("/api/v1/network/criminal/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_get_crime_network_success(client):
    response = client.get("/api/v1/network/crime/10")
    assert response.status_code == 200
    data = response.json()
    
    assert "nodes" in data
    assert "edges" in data
    assert data["total_nodes"] == 3
    assert data["total_edges"] == 2
    
    # Check node details
    nodes = {n["id"]: n for n in data["nodes"]}
    assert "crime_10" in nodes
    assert nodes["crime_10"]["type"] == "crime"
    assert nodes["crime_10"]["label"] == "Robbery"
    
    # Check edges details
    edges = data["edges"]
    assert any(e["source"] == "crime_10" and e["target"] == "location_5" and e["relationship"] == "OCCURRED_AT" for e in edges)

def test_get_crime_network_not_found(client):
    response = client.get("/api/v1/network/crime/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_get_location_network_success(client):
    response = client.get("/api/v1/network/location/5")
    assert response.status_code == 200
    data = response.json()
    
    assert "nodes" in data
    assert "edges" in data
    assert data["total_nodes"] == 3
    assert data["total_edges"] == 2
    
    # Check node details
    nodes = {n["id"]: n for n in data["nodes"]}
    assert "location_5" in nodes
    assert nodes["location_5"]["type"] == "location"
    assert nodes["location_5"]["label"] == "Mysuru, Karnataka"
    
    # Check edges details
    edges = data["edges"]
    assert any(e["source"] == "criminal_1" and e["target"] == "crime_10" and e["relationship"] == "INVOLVED_IN" for e in edges)

def test_get_location_network_not_found(client):
    response = client.get("/api/v1/network/location/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
