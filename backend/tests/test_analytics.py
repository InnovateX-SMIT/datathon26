import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.core.database import Base, get_db
from backend.api.auth.router import get_current_user
from backend import models
from backend.models.crime import CrimeEvent
from backend.app.main import app
from backend.services.analytics_service import AnalyticsService

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
        # Seed test data
        crimes = [
            CrimeEvent(
                crime_type="Theft",
                crime_category="Theft",
                crime_subcategory="Vehicle Theft",
                crime_date=date(2026, 6, 1),
                victim_count=1,
                accused_count=1,
                status="reported"
            ),
            CrimeEvent(
                crime_type="Assault",
                crime_category="Violent Crime",
                crime_subcategory="Simple Assault",
                crime_date=date(2026, 6, 2),
                victim_count=2,
                accused_count=1,
                status="reported"
            ),
            # Prev month (June 2026 is current month, so May 2026 is prev month)
            CrimeEvent(
                crime_type="Theft",
                crime_category="Theft",
                crime_subcategory="House Theft",
                crime_date=date(2026, 5, 15),
                victim_count=1,
                accused_count=2,
                status="reported"
            ),
            # Prev year
            CrimeEvent(
                crime_type="Fraud",
                crime_category="Financial Crime",
                crime_subcategory="Online Fraud",
                crime_date=date(2025, 6, 1),
                victim_count=1,
                accused_count=1,
                status="reported"
            )
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

def test_overview_metrics(client):
    response = client.get("/api/v1/analytics/overview")
    assert response.status_code == 200
    data = response.json()
    assert data["total_crimes"] == 4
    assert data["total_victims"] == 5
    assert data["total_accused"] == 5

def test_trends_daily(client):
    response = client.get("/api/v1/analytics/trends?granularity=daily")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 4
    periods = [x["period"] for x in data]
    assert periods == ["2025-06-01", "2026-05-15", "2026-06-01", "2026-06-02"]

def test_trends_monthly(client):
    response = client.get("/api/v1/analytics/trends?granularity=monthly")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    periods = [x["period"] for x in data]
    assert periods == ["2025-06", "2026-05", "2026-06"]

def test_category_distribution(client):
    response = client.get("/api/v1/analytics/categories")
    assert response.status_code == 200
    data = response.json()
    assert "categories" in data
    assert "subcategories" in data
    
    categories = data["categories"]
    assert len(categories) == 3
    assert categories[0]["name"] == "Theft"
    assert categories[0]["count"] == 2

def test_historical_comparison(client):
    from unittest.mock import patch
    class MockDate(date):
        @classmethod
        def today(cls):
            return date(2026, 6, 15)

    with patch("backend.services.analytics_service.date", MockDate):
        response = client.get("/api/v1/analytics/comparison")
        assert response.status_code == 200
        data = response.json()
        assert data["current_month"] == 2
        assert data["previous_month"] == 1
        assert data["month_change_percent"] == 100.0
        assert data["current_year"] == 3
        assert data["previous_year"] == 1
        assert data["year_change_percent"] == 200.0

def test_trends_invalid_granularity(client):
    response = client.get("/api/v1/analytics/trends?granularity=hourly")
    assert response.status_code == 400
