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
from backend.services.network_analytics_service import NetworkAnalyticsService

# Setup in-memory sqlite database for test isolation
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
        # Seed test network topology
        # Locations
        loc5 = Location(id=5, state="Karnataka", district="Mysuru", latitude=12.30, longitude=76.64)
        loc6 = Location(id=6, state="Karnataka", district="Bengaluru", latitude=12.97, longitude=77.59)
        db.add(loc5)
        db.add(loc6)
        
        # Criminals
        c1 = Criminal(id=1, name="Jane Smith", gender="Female", age=28.0, occupation="Cashier", caste="OBC", risk_score=0.4, status="accused")
        c2 = Criminal(id=2, name="John Doe", gender="Male", age=32.0, occupation="Unemployed", caste="General", risk_score=0.8, status="convicted")
        c3 = Criminal(id=3, name="Lone Ranger", gender="Male", age=45.0, occupation="Driver", caste="SC", risk_score=0.1, status="suspect")
        db.add(c1)
        db.add(c2)
        db.add(c3)
        
        # Crimes
        crime10 = CrimeEvent(id=10, crime_type="Robbery", crime_category="Violent Crime", severity=3.0, status="reported", crime_date=date(2026, 6, 12), location_id=5)
        crime11 = CrimeEvent(id=11, crime_type="Burglary", crime_category="Property Crime", severity=2.0, status="reported", crime_date=date(2026, 6, 13), location_id=5)
        crime12 = CrimeEvent(id=12, crime_type="Theft", crime_category="Property Crime", severity=1.0, status="reported", crime_date=date(2026, 6, 14), location_id=6)
        db.add(crime10)
        db.add(crime11)
        db.add(crime12)
        
        # Participations (Co-offenders on Crime 10 and 11)
        db.add(CrimeParticipation(id=1, crime_event_id=10, criminal_id=1, role="accused"))
        db.add(CrimeParticipation(id=2, crime_event_id=10, criminal_id=2, role="accomplice"))
        db.add(CrimeParticipation(id=3, crime_event_id=11, criminal_id=1, role="accused"))
        db.add(CrimeParticipation(id=4, crime_event_id=11, criminal_id=2, role="accused"))
        
        # Isolated Criminal 3 commits Crime 12 in location 6
        db.add(CrimeParticipation(id=5, crime_event_id=12, criminal_id=3, role="accused"))
        
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

# --- SERVICE TESTS ---

def test_service_graph_construction(db_session):
    service = NetworkAnalyticsService(db_session)
    G = service.get_graph(force_rebuild=True)
    
    assert len(G.nodes) == 8 # 3 criminals + 3 crimes + 2 locations
    assert G.has_node("criminal_1")
    assert G.has_node("crime_10")
    assert G.has_node("location_5")
    
    # Check relationship counts
    assert G.has_edge("criminal_1", "crime_10")
    assert G.has_edge("crime_10", "location_5")

def test_service_centrality(db_session):
    service = NetworkAnalyticsService(db_session)
    res = service.get_centrality()
    
    assert "degree" in res
    assert "betweenness" in res
    assert "closeness" in res
    
    # Degree centrality of crime_10 (connected to criminal_1, criminal_2, and location_5)
    degree_top = res["degree"][0]
    assert degree_top["id"] in ["crime_10", "crime_11", "criminal_1", "criminal_2", "location_5"]

def test_service_clusters(db_session):
    service = NetworkAnalyticsService(db_session)
    clusters = service.get_clusters()
    
    # Two separate networks: {c1, c2, crime10, crime11, loc5} and {c3, crime12, loc6}
    assert len(clusters) == 2
    assert clusters[0]["size"] == 5
    assert clusters[1]["size"] == 3
    assert clusters[0]["criminal_count"] == 2
    assert clusters[1]["criminal_count"] == 1

def test_service_associations(db_session):
    service = NetworkAnalyticsService(db_session)
    associations = service.get_repeat_associations()
    
    # Criminal 1 and 2 share 2 crimes (crime 10 and 11)
    assert len(associations) >= 1
    assoc = associations[0]
    assert assoc["criminal_a"]["id"] == "criminal_1"
    assert assoc["criminal_b"]["id"] == "criminal_2"
    assert assoc["frequency"] == 2
    assert assoc["strength"] > 0.0

def test_service_location_intelligence(db_session):
    service = NetworkAnalyticsService(db_session)
    loc_intel = service.get_location_intelligence()
    
    assert "most_active" in loc_intel
    assert "most_connected" in loc_intel
    assert "location_links" in loc_intel
    
    # Location 5 is most active (2 crimes: 10, 11)
    assert loc_intel["most_active"][0]["id"] == "location_5"
    assert loc_intel["most_active"][0]["crime_count"] == 2

def test_service_shortest_path(db_session):
    service = NetworkAnalyticsService(db_session)
    
    # Criminal 1 to Location 5 path: criminal_1 -> crime_10 -> location_5
    path_res = service.find_shortest_path("criminal_1", "location_5")
    assert path_res["path_found"] is True
    assert path_res["path_length"] == 2
    assert path_res["nodes"][0]["id"] == "criminal_1"
    assert path_res["nodes"][1]["id"] in ["crime_10", "crime_11"]
    assert path_res["nodes"][2]["id"] == "location_5"
    
    # No path between separate networks (Criminal 1 to Location 6)
    no_path = service.find_shortest_path("criminal_1", "location_6")
    assert no_path["path_found"] is False
    assert no_path["path_length"] == 0

# --- API TESTS ---

def test_api_centrality_success(client):
    response = client.get("/api/v1/network/centrality")
    assert response.status_code == 200
    data = response.json()
    assert "degree" in data
    assert len(data["degree"]) > 0

def test_api_clusters_success(client):
    response = client.get("/api/v1/network/clusters")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["cluster_id"] == "cluster_1"

def test_api_associations_success(client):
    response = client.get("/api/v1/network/associations")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["frequency"] == 2

def test_api_location_intelligence_success(client):
    response = client.get("/api/v1/network/location-intelligence")
    assert response.status_code == 200
    data = response.json()
    assert len(data["most_active"]) > 0

def test_api_link_analysis_success(client):
    response = client.get("/api/v1/network/link-analysis?source_id=criminal_1&target_id=location_5")
    assert response.status_code == 200
    data = response.json()
    assert data["path_found"] is True
    assert data["path_length"] == 2

def test_api_link_analysis_missing_entities(client):
    response = client.get("/api/v1/network/link-analysis?source_id=criminal_1&target_id=criminal_999")
    assert response.status_code == 200
    data = response.json()
    assert data["path_found"] is False
    assert data["path_length"] == 0
