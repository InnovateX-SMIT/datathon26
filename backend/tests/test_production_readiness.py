import time
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.core.config import settings

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_readiness_endpoint(client):
    response = client.get("/readiness")
    assert response.status_code in [200, 503]

def test_version_endpoint(client):
    response = client.get("/version")
    assert response.status_code == 200
    assert response.json()["version"] == "1.0.0"

def test_system_status_endpoint(client):
    response = client.get("/system-status")
    assert response.status_code == 200
    assert response.json()["status"] == "operational"

def test_secure_headers(client):
    response = client.get("/health")
    assert "X-Frame-Options" in response.headers
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "X-Content-Type-Options" in response.headers
    assert response.headers["X-Content-Type-Options"] == "nosniff"

def test_xss_input_sanitization(client):
    response = client.post("/api/v1/recommendations/sync", json={"payload": "<script>alert(1)</script>"})
    assert response.status_code == 400
    assert "Potential script injection detected" in response.json()["detail"]

def test_rate_limiting(client):
    import backend.app.main
    backend.app.main.request_counts.clear()
    
    original_max = backend.app.main.RATE_LIMIT_MAX_REQUESTS
    backend.app.main.RATE_LIMIT_MAX_REQUESTS = 3
    try:
        for _ in range(3):
            res = client.get("/health")
            assert res.status_code == 200
        # 4th request should fail
        res = client.get("/health")
        assert res.status_code == 429
        assert "Too many requests" in res.json()["detail"]
    finally:
        backend.app.main.RATE_LIMIT_MAX_REQUESTS = original_max
