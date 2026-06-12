import datetime
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.core.database import Base
from backend.models.police_station import PoliceStation
from backend.models.crime import CrimeEvent
from backend.models.location import Location
from backend.services.recommendation_service import RecommendationService
from backend.schemas.recommendation import RecommendationCreate

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

def test_greedy_proportional_fallback(db_session):
    service = RecommendationService(db_session)
    targets = [1.5, 3.5, 5.0]  # sum is 10
    allocated = service._greedy_proportional(targets, 10)
    assert sum(allocated) == 10
    assert allocated[0] in [1, 2]
    assert allocated[1] in [3, 4]
    assert allocated[2] == 5

def test_solve_resource_optimization_success(db_session):
    # Seed location
    loc = Location(district="Mysuru", state="Karnataka", latitude=12.2958, longitude=76.6394)
    db_session.add(loc)
    db_session.commit()
    db_session.refresh(loc)

    # Seed police stations
    ps1 = PoliceStation(station_name="Mysuru Town", district="Mysuru", beat="Beat A", location_id=loc.id, capacity=50)
    ps2 = PoliceStation(station_name="Mysuru Rural", district="Mysuru", beat="Beat B", location_id=loc.id, capacity=30)
    db_session.add_all([ps1, ps2])
    db_session.commit()
    db_session.refresh(ps1)
    db_session.refresh(ps2)

    # Seed crime events to create different severity profiles
    c1 = CrimeEvent(crime_type="Theft", crime_category="Property", severity=2.0, police_station_id=ps1.id, location_id=loc.id, crime_date=datetime.date(2026, 6, 1))
    c2 = CrimeEvent(crime_type="Assault", crime_category="Violent", severity=4.0, police_station_id=ps1.id, location_id=loc.id, crime_date=datetime.date(2026, 6, 2))
    c3 = CrimeEvent(crime_type="Theft", crime_category="Property", severity=1.0, police_station_id=ps2.id, location_id=loc.id, crime_date=datetime.date(2026, 6, 3))
    db_session.add_all([c1, c2, c3])

    db_session.commit()

    service = RecommendationService(db_session)
    result = service.run_resource_optimization(
        district="Mysuru",
        sanctioned_asi=4,
        sanctioned_chc=8,
        sanctioned_cpc=20
    )

    assert len(result) == 2
    # Verify exact sum conservation
    total_asi = sum(r["asi_allocated"] for r in result)
    total_chc = sum(r["chc_allocated"] for r in result)
    total_cpc = sum(r["cpc_allocated"] for r in result)
    
    assert total_asi == 4
    assert total_chc == 8
    assert total_cpc == 20

    # Mysuru Town has higher severity score, so it should get more resources
    town_alloc = next(r for r in result if r["beat_name"] == "Mysuru Town")
    rural_alloc = next(r for r in result if r["beat_name"] == "Mysuru Rural")
    
    assert town_alloc["normalized_severity"] > rural_alloc["normalized_severity"]
    assert town_alloc["cpc_allocated"] > rural_alloc["cpc_allocated"]

def test_generate_dynamic_recommendations_fallbacks(db_session):
    service = RecommendationService(db_session)
    # Seeding empty DB, expect defaults
    recs = service.generate_dynamic_recommendations()
    assert len(recs) == 2
    assert "Bengaluru Urban" in recs[0].recommendation_text
    assert recs[0].priority == "high"
