import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.core.database import Base
from backend.models.location import Location
from backend.models.criminal import Criminal
from backend.models.crime import CrimeEvent
from backend.models.crime_participation import CrimeParticipation
from backend.services.network_service import NetworkService

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

def test_build_criminal_network(db_session):
    service = NetworkService(db_session)
    res = service.build_criminal_network(1)
    
    assert res is not None
    assert "nodes" in res
    assert "edges" in res
    assert res["total_nodes"] == 3
    assert res["total_edges"] == 2
    
    nodes = {n["id"]: n for n in res["nodes"]}
    assert "criminal_1" in nodes
    assert "crime_10" in nodes
    assert "location_5" in nodes
    
    assert nodes["criminal_1"]["type"] == "criminal"
    assert nodes["criminal_1"]["label"] == "Jane Smith"
    assert nodes["crime_10"]["type"] == "crime"
    assert nodes["crime_10"]["label"] == "Robbery"
    assert nodes["location_5"]["type"] == "location"
    assert nodes["location_5"]["label"] == "Mysuru, Karnataka"
    
    edges = res["edges"]
    assert any(e["source"] == "criminal_1" and e["target"] == "crime_10" and e["relationship"] == "INVOLVED_IN" for e in edges)
    assert any(e["source"] == "crime_10" and e["target"] == "location_5" and e["relationship"] == "OCCURRED_AT" for e in edges)
    
    # Missing criminal
    assert service.build_criminal_network(999) is None

def test_build_crime_network(db_session):
    service = NetworkService(db_session)
    res = service.build_crime_network(10)
    
    assert res is not None
    assert "nodes" in res
    assert "edges" in res
    assert res["total_nodes"] == 3
    assert res["total_edges"] == 2
    
    nodes = {n["id"]: n for n in res["nodes"]}
    assert "criminal_1" in nodes
    assert "crime_10" in nodes
    assert "location_5" in nodes
    
    edges = res["edges"]
    assert any(e["source"] == "criminal_1" and e["target"] == "crime_10" and e["relationship"] == "INVOLVED_IN" for e in edges)
    assert any(e["source"] == "crime_10" and e["target"] == "location_5" and e["relationship"] == "OCCURRED_AT" for e in edges)
    
    # Missing crime
    assert service.build_crime_network(999) is None

def test_build_location_network(db_session):
    service = NetworkService(db_session)
    res = service.build_location_network(5)
    
    assert res is not None
    assert "nodes" in res
    assert "edges" in res
    assert res["total_nodes"] == 3
    assert res["total_edges"] == 2
    
    nodes = {n["id"]: n for n in res["nodes"]}
    assert "criminal_1" in nodes
    assert "crime_10" in nodes
    assert "location_5" in nodes
    
    edges = res["edges"]
    assert any(e["source"] == "criminal_1" and e["target"] == "crime_10" and e["relationship"] == "INVOLVED_IN" for e in edges)
    assert any(e["source"] == "crime_10" and e["target"] == "location_5" and e["relationship"] == "OCCURRED_AT" for e in edges)
    
    # Missing location
    assert service.build_location_network(999) is None
