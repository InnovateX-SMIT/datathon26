import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.core.database import Base, get_db
from backend.api.auth.router import get_current_user
from backend import models
from backend.models.crime import CrimeEvent
from backend.models.location import Location
from backend.models.police_station import PoliceStation
from backend.app.main import app

from sqlalchemy.pool import StaticPool

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
        # Seed active dataset
        from backend.models.dataset import Dataset
        ds = Dataset(id=1, name="test_geo", original_filename="test_geo.csv", display_name="Test Geo", is_active=True, status="Ready", upload_status="Completed")
        db.add(ds)
        db.flush()

        # Seed locations
        loc1 = Location(id=1, state="Karnataka", district="Ballari", latitude=14.94, longitude=76.24)
        loc2 = Location(id=2, state="Karnataka", district="Shivamogga", latitude=16.98, longitude=78.27)
        db.add_all([loc1, loc2])
        db.commit()

        # Seed police stations
        ps1 = PoliceStation(id=1, station_name="BAL_PS_37", district="Ballari", location_id=1)
        ps2 = PoliceStation(id=2, station_name="SHI_PS_31", district="Shivamogga", location_id=2)
        db.add_all([ps1, ps2])
        db.commit()

        # Seed crime events
        crimes = [
            CrimeEvent(
                id=1,
                dataset_id=1,
                crime_type="Theft",
                crime_category="Theft",
                crime_date=date(2026, 6, 1),
                location_id=1,
                police_station_id=1,
                status="reported"
            ),
            CrimeEvent(
                id=2,
                dataset_id=1,
                crime_type="Theft",
                crime_category="Theft",
                crime_date=date(2026, 6, 2),
                location_id=1,
                police_station_id=1,
                status="reported"
            ),
            CrimeEvent(
                id=3,
                dataset_id=1,
                crime_type="Assault",
                crime_category="Violent Crime",
                crime_date=date(2026, 6, 3),
                location_id=2,
                police_station_id=2,
                status="reported"
            ),
            CrimeEvent(id=4, dataset_id=1, crime_type="Theft", crime_category="Theft", crime_date=date(2026, 6, 1), location_id=1, police_station_id=1, status="reported"),
            CrimeEvent(id=5, dataset_id=1, crime_type="Theft", crime_category="Theft", crime_date=date(2026, 6, 1), location_id=1, police_station_id=1, status="reported"),
            CrimeEvent(id=6, dataset_id=1, crime_type="Theft", crime_category="Theft", crime_date=date(2026, 6, 1), location_id=1, police_station_id=1, status="reported"),
        ]
        db.add_all(crimes)
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

def test_get_districts(client):
    response = client.get("/api/v1/geo/districts")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["district"] == "Ballari"
    assert data[0]["crime_count"] == 5

def test_get_stations(client):
    response = client.get("/api/v1/geo/stations")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["station"] == "BAL_PS_37"
    assert data[0]["crime_count"] == 5

def test_get_heatmap(client):
    response = client.get("/api/v1/geo/heatmap")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["weight"] == 5

def test_get_hotspots(client):
    response = client.get("/api/v1/geo/hotspots")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["crime_count"] == 5
    assert abs(data[0]["latitude"] - 14.94) < 0.01

def test_get_districts_filtered(client):
    response = client.get("/api/v1/geo/districts?district=Ballari")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["district"] == "Ballari"

def test_get_districts_filtered_crime_type(client):
    response = client.get("/api/v1/geo/districts?crime_type=Assault")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["district"] == "Shivamogga"
    assert data[0]["crime_count"] == 1
