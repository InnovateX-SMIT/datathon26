import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.core.database import Base, get_db
from backend.api.auth.router import get_current_user
from backend.app.main import app
from backend.models.alert import Alert

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
        return {"id": 1, "email": "officer@police.gov.in", "role": "OFFICER"}

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

def test_get_alerts_list_filtering(client, db_session):
    a1 = Alert(title="Title 1", description="Desc 1", severity="CRITICAL", source="prediction", status="NEW")
    a2 = Alert(title="Title 2", description="Desc 2", severity="HIGH", source="network", status="IN_PROGRESS")
    db_session.add_all([a1, a2])
    db_session.commit()

    # Get all
    response = client.get("/api/v1/alerts/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    # Filter by severity
    response = client.get("/api/v1/alerts/?severity=CRITICAL")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Title 1"

    # Filter by source
    response = client.get("/api/v1/alerts/?source=network")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Title 2"

    # Filter by status
    response = client.get("/api/v1/alerts/?status=NEW")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_get_alert_by_id_success_and_fail(client, db_session):
    a = Alert(title="Detail Alert", description="Check details", severity="LOW", source="geo", status="NEW")
    db_session.add(a)
    db_session.commit()
    db_session.refresh(a)

    # 200 Success
    response = client.get(f"/api/v1/alerts/{a.id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Detail Alert"

    # 404 Fail
    response = client.get("/api/v1/alerts/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_generate_alerts_api(client, db_session):
    from backend.models.recommendation import Recommendation
    rec = Recommendation(
        recommendation_text="Urgent action needed in Area 51",
        priority="high",
        status="pending"
    )
    db_session.add(rec)
    db_session.commit()

    response = client.post("/api/v1/alerts/generate")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["status"] == "NEW"


def test_update_alert_status_api(client, db_session):
    a = Alert(title="Status Alert", description="Check status changes", severity="MEDIUM", source="geo", status="NEW")
    db_session.add(a)
    db_session.commit()
    db_session.refresh(a)

    # Transition from NEW to IN_PROGRESS (should assign current user ID = 1)
    payload = {"status": "IN_PROGRESS"}
    response = client.put(f"/api/v1/alerts/{a.id}/status", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "IN_PROGRESS"
    assert data["assigned_user_id"] == 1

    # Transition to RESOLVED (should clear assigned user or keep it, according to logic)
    payload_resolve = {"status": "RESOLVED"}
    response = client.put(f"/api/v1/alerts/{a.id}/status", json=payload_resolve)
    assert response.status_code == 200
    assert response.json()["status"] == "RESOLVED"

def test_get_alerts_summary_api(client, db_session):
    a = Alert(title="Summary Alert", description="Aggregate stats", severity="CRITICAL", source="prediction", status="NEW")
    db_session.add(a)
    db_session.commit()

    response = client.get("/api/v1/alerts/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_active"] == 1
    assert data["critical_count"] == 1
    assert len(data["by_source"]) == 1
    assert data["by_source"][0]["source"] == "prediction"
