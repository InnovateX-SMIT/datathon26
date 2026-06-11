import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.core.database import Base
from backend import models
from backend.models.location import Location
from backend.models.criminal import Criminal
from backend.models.crime import CrimeEvent
from backend.models.crime_participation import CrimeParticipation
from backend.repositories.network_repository import NetworkRepository

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
        loc = Location(id=1, state="Karnataka", district="Bengaluru", latitude=12.97, longitude=77.59)
        crim = Criminal(id=1, name="John Doe", gender="Male", age=34.0, occupation="Unemployed", caste="General", risk_score=0.8, status="accused")
        crime = CrimeEvent(id=1, crime_type="Theft", crime_category="Theft", crime_subcategory="Vehicle Theft", severity=1.5, status="reported", crime_date=date(2026, 6, 12), location_id=1)
        part = CrimeParticipation(id=1, crime_event_id=1, criminal_id=1, role="accused")
        
        db.add(loc)
        db.add(crim)
        db.add(crime)
        db.add(part)
        db.commit()
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_get_by_id_methods(db_session):
    repo = NetworkRepository(db_session)
    
    crim = repo.get_criminal_by_id(1)
    assert crim is not None
    assert crim.name == "John Doe"
    
    crime = repo.get_crime_by_id(1)
    assert crime is not None
    assert crime.crime_type == "Theft"
    
    loc = repo.get_location_by_id(1)
    assert loc is not None
    assert loc.district == "Bengaluru"
    
    # Missing handling
    assert repo.get_criminal_by_id(999) is None
    assert repo.get_crime_by_id(999) is None
    assert repo.get_location_by_id(999) is None

def test_get_criminal_network(db_session):
    repo = NetworkRepository(db_session)
    crim_net = repo.get_criminal_network(1)
    
    assert crim_net is not None
    assert crim_net.name == "John Doe"
    assert len(crim_net.participations) == 1
    assert crim_net.participations[0].crime_event is not None
    assert crim_net.participations[0].crime_event.crime_type == "Theft"
    assert crim_net.participations[0].crime_event.location is not None
    assert crim_net.participations[0].crime_event.location.district == "Bengaluru"
    
    # Missing criminal
    assert repo.get_criminal_network(999) is None

def test_get_crime_network(db_session):
    repo = NetworkRepository(db_session)
    crime_net = repo.get_crime_network(1)
    
    assert crime_net is not None
    assert crime_net.crime_type == "Theft"
    assert crime_net.location is not None
    assert crime_net.location.district == "Bengaluru"
    assert len(crime_net.participations) == 1
    assert crime_net.participations[0].criminal is not None
    assert crime_net.participations[0].criminal.name == "John Doe"
    
    # Missing crime
    assert repo.get_crime_network(999) is None

def test_get_location_network(db_session):
    repo = NetworkRepository(db_session)
    loc_net = repo.get_location_network(1)
    
    assert loc_net is not None
    assert loc_net.district == "Bengaluru"
    assert len(loc_net.crime_events) == 1
    assert loc_net.crime_events[0].crime_type == "Theft"
    assert len(loc_net.crime_events[0].participations) == 1
    assert loc_net.crime_events[0].participations[0].criminal is not None
    assert loc_net.crime_events[0].participations[0].criminal.name == "John Doe"
    
    # Missing location
    assert repo.get_location_network(999) is None
