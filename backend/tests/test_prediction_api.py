import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.core.database import Base, get_db
from backend.api.auth.router import get_current_user
from backend.app.main import app
from backend.models.prediction import Prediction

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

def test_predictions_health(client):
    response = client.get("/api/v1/predictions/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "status" in data["data"]
    assert "models_loaded" in data["data"]

def test_predict_repeat_offender_success(client, db_session):
    payload = {
        "age": 30,
        "occupation": "Farmer",
        "caste": "General",
        "district": "Ballari"
    }
    response = client.post("/api/v1/predictions/repeat-offender", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "probability" in data["data"]
    assert "risk_level" in data["data"]
    assert data["data"]["risk_level"] in ["LOW", "MEDIUM", "HIGH"]
    
    # Verify database persistence
    db_record = db_session.query(Prediction).filter(Prediction.prediction_type == "repeat-offender").first()
    assert db_record is not None
    assert "Risk" in db_record.prediction_value

def test_predict_crime_risk_success(client, db_session):
    payload = {
        "district": "Mysuru",
        "crime_category": "Theft",
        "historical_crime_count": 150
    }
    response = client.post("/api/v1/predictions/crime-risk", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "risk_score" in data["data"]
    assert "risk_level" in data["data"]
    assert 0 <= data["data"]["risk_score"] <= 100
    
    # Verify database persistence
    db_record = db_session.query(Prediction).filter(Prediction.prediction_type == "crime-risk").first()
    assert db_record is not None

def test_predict_crime_type_success(client, db_session):
    payload = {
        "district": "Shivamogga",
        "month": 6,
        "hour": 15,
        "day_of_week": 3,
        "historical_crime_count": 80
    }
    response = client.post("/api/v1/predictions/crime-type", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "crime_type" in data["data"]
    assert "confidence" in data["data"]
    
    # Verify database persistence
    db_record = db_session.query(Prediction).filter(Prediction.prediction_type == "crime-type").first()
    assert db_record is not None

def test_predict_hotspot_success(client, db_session):
    payload = {
        "district": "Ballari",
        "trend_metrics": 45,
        "historical_crime_growth": 1.12
    }
    response = client.post("/api/v1/predictions/hotspot", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "hotspot_probability" in data["data"]
    assert "trend" in data["data"]
    assert data["data"]["trend"] in ["RISING", "STABLE", "FALLING"]
    
    # Verify database persistence
    db_record = db_session.query(Prediction).filter(Prediction.prediction_type == "hotspot").first()
    assert db_record is not None

def test_predict_explain_success(client):
    payload = {
        "prediction_type": "repeat-offender",
        "features": {
            "age": 30,
            "occupation": "Farmer",
            "caste": "General",
            "district": "Ballari"
        }
    }
    response = client.post("/api/v1/predictions/explain", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)
    assert len(data["data"]) > 0
    assert "feature" in data["data"][0]
    assert "impact" in data["data"][0]

def test_prediction_validation_failures(client):
    # Repeat offender: age < 0
    payload_repeat = {
        "age": -5,
        "occupation": "Farmer",
        "caste": "General",
        "district": "Ballari"
    }
    response = client.post("/api/v1/predictions/repeat-offender", json=payload_repeat)
    assert response.status_code == 422
    
    # Crime risk: historical_crime_count < 0
    payload_risk = {
        "district": "Mysuru",
        "crime_category": "Theft",
        "historical_crime_count": -10
    }
    response = client.post("/api/v1/predictions/crime-risk", json=payload_risk)
    assert response.status_code == 422

    # Crime type: invalid month (15)
    payload_type = {
        "district": "Shivamogga",
        "month": 15,
        "hour": 15,
        "day_of_week": 3,
        "historical_crime_count": 80
    }
    response = client.post("/api/v1/predictions/crime-type", json=payload_type)
    assert response.status_code == 422
