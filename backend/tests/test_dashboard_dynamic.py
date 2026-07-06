import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.core.database import Base, get_db
from backend.api.auth.router import get_current_user
from backend.models.crime import CrimeEvent
from backend.models.dataset import Dataset
from backend.models.criminal import Criminal
from backend.models.location import Location
from backend.models.police_station import PoliceStation
from backend.app.main import app
from backend.services.analytics_service import AnalyticsService

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
    
    # 1. Create a dummy dataset
    ds = Dataset(id=1, name="test_dataset", original_filename="test_dataset.csv", display_name="Test Dataset", is_active=True, status="Ready")
    db.add(ds)
    
    # 2. Add locations & police stations
    loc1 = Location(id=1, state="Karnataka", district="Bengaluru East", latitude=12.97, longitude=77.59)
    loc2 = Location(id=2, state="Karnataka", district="Bengaluru West", latitude=12.96, longitude=77.58)
    db.add(loc1)
    db.add(loc2)
    
    ps = PoliceStation(id=1, station_name="Koramangala PS", district="Bengaluru East", capacity=50, location_id=1)
    db.add(ps)
    
    # 3. Add mock crime events
    crimes = [
        # Closed case
        CrimeEvent(
            id=1,
            crime_type="Theft",
            crime_category="Theft",
            crime_subcategory="Vehicle Theft",
            crime_date=date(2026, 6, 1),
            victim_count=1,
            accused_count=1,
            status="Closed",
            severity=3.0,
            dataset_id=1,
            location_id=1,
            police_station_id=1
        ),
        # Active cases
        CrimeEvent(
            id=2,
            crime_type="Assault",
            crime_category="Violent Crime",
            crime_subcategory="Simple Assault",
            crime_date=date(2026, 6, 2),
            victim_count=2,
            accused_count=1,
            status="Under Investigation",
            severity=5.0,
            dataset_id=1,
            location_id=1,
            police_station_id=1
        ),
        CrimeEvent(
            id=3,
            crime_type="Burglary",
            crime_category="Theft",
            crime_subcategory="House Theft",
            crime_date=date(2026, 6, 3),
            victim_count=1,
            accused_count=2,
            status="Chargesheet Filed",
            severity=4.0,
            dataset_id=1,
            location_id=2,
            police_station_id=1
        ),
        # Non-closed (Active)
        CrimeEvent(
            id=4,
            crime_type="Fraud",
            crime_category="Financial Crime",
            crime_subcategory="Online Fraud",
            crime_date=date(2026, 6, 4),
            victim_count=0,
            accused_count=1,
            status="Pending Trial",
            severity=2.0,
            dataset_id=1,
            location_id=2,
            police_station_id=1
        )
    ]
    db.add_all(crimes)
    
    # 4. Add mock criminals
    criminals = [
        Criminal(id=1, name="Criminal A", risk_score=8.5, dataset_id=1),
        Criminal(id=2, name="Criminal B", risk_score=4.0, dataset_id=1)
    ]
    db.add_all(criminals)
    
    db.commit()
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

def test_dynamic_dashboard_summary(client):
    response = client.get("/api/v1/analytics/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    
    # Assert primary metric correctness
    assert data["total_crimes"] == 4
    assert data["total_victims"] == 4
    assert data["total_accused"] == 5
    assert data["active_cases"] == 3
    
    # Criminal Registry Assertions
    assert data["total_criminals"] == 2
    assert data["high_risk_criminals"] == 1
    
    # Redesigned KPIs formatting checks
    assert data["crime_resolution_rate"] == 25.0
    assert data["average_severity"] == 3.5
    assert data["districts_count"] == 2
    assert data["stations_count"] == 1

def test_empty_dataset_handling(client, db_session):
    # Deactivate dataset 1 and create a new empty dataset
    db_session.query(Dataset).filter(Dataset.id == 1).update({"is_active": False})
    empty_ds = Dataset(id=2, name="empty_dataset", original_filename="empty_dataset.csv", display_name="Empty Dataset", is_active=True, status="Ready")
    db_session.add(empty_ds)
    db_session.commit()
    
    response = client.get("/api/v1/analytics/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    
    # Assert zero values with no errors
    assert data["total_crimes"] == 0
    assert data["active_cases"] == 0
    assert data["total_victims"] == 0
    assert data["high_risk_criminals"] == 0
    assert data["crime_resolution_rate"] == 0.0
    assert data["average_severity"] == 0.0
    assert data["districts_count"] == 0
    assert data["stations_count"] == 0
