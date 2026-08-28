import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.core.database import SessionLocal, engine, Base
from backend.models.dataset import Dataset

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield

from fastapi import HTTPException
from backend.api.deps import get_session_id

def test_missing_session_id_header_returns_400(monkeypatch):
    """Verify that requests missing X-Session-ID raise HTTP 400 Bad Request."""
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    from backend.core.config import settings
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")

    with pytest.raises(HTTPException) as excinfo:
        get_session_id(None)
    assert excinfo.value.status_code == 400
    assert "Missing or invalid X-Session-ID header" in excinfo.value.detail

def test_multi_user_dataset_isolation():
    """
    Verify complete multi-user data isolation:
    User A's datasets and processing results cannot be seen, accessed, activated,
    or mutated by User B.
    """
    db = SessionLocal()
    try:
        # Create dataset belonging to Session A directly
        ds_a = Dataset(
            name="dataset_user_a",
            original_filename="user_a_data.csv",
            display_name="User A Private Data",
            is_active=True,
            status="Ready",
            upload_status="Completed",
            schema_type="legacy_crime_intel",
            session_id="session-user-a"
        )
        db.add(ds_a)
        db.commit()
        db.refresh(ds_a)
        ds_a_id = ds_a.id

        # User A fetches datasets -> sees dataset A
        res_a = client.get("/api/v1/datasets/", headers={"X-Session-ID": "session-user-a"})
        assert res_a.status_code == 200
        datasets_a = res_a.json()
        assert any(d["id"] == ds_a_id for d in datasets_a)

        # User B fetches datasets -> MUST NOT see dataset A
        res_b = client.get("/api/v1/datasets/", headers={"X-Session-ID": "session-user-b"})
        assert res_b.status_code == 200
        datasets_b = res_b.json()
        assert not any(d["id"] == ds_a_id for d in datasets_b)

        # User B attempts to view dataset A by ID -> MUST return 404
        res_b_detail = client.get(f"/api/v1/datasets/{ds_a_id}", headers={"X-Session-ID": "session-user-b"})
        assert res_b_detail.status_code == 404

        # User B attempts to activate dataset A -> MUST return 404
        res_b_activate = client.post("/api/v1/datasets/activate", json={"dataset_id": ds_a_id}, headers={"X-Session-ID": "session-user-b"})
        assert res_b_activate.status_code == 404

        # User B attempts to delete dataset A -> MUST return 404
        res_b_delete = client.delete(f"/api/v1/datasets/{ds_a_id}", headers={"X-Session-ID": "session-user-b"})
        assert res_b_delete.status_code == 404

    finally:
        db.close()
