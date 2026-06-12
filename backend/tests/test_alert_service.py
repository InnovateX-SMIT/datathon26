import pytest
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.core.database import Base
from backend.models.alert import Alert
from backend.models.prediction import Prediction
from backend.models.location import Location
from backend.models.crime import CrimeEvent
from backend.models.recommendation import Recommendation, ResourceAllocation
from backend.services.alert_service import AlertService
from backend.schemas.alert import AlertCreate

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

def test_alert_exists_deduplication(db_session):
    service = AlertService(db_session)
    alert_dto = AlertCreate(
        title="Deduplication Test",
        description="This is a test description",
        severity="HIGH",
        source="prediction"
    )
    
    # 1. Create first time
    service.repo.create_alert(alert_dto)
    
    # 2. Verify duplicate check returns True
    exists = service.repo.check_alert_exists(
        title=alert_dto.title,
        description=alert_dto.description,
        active_statuses=["NEW", "ACKNOWLEDGED", "IN_PROGRESS"]
    )
    assert exists is True

def test_generate_predictive_hotspot_alerts(db_session):
    # Seed location and crime event
    loc = Location(district="Shivamogga", state="Karnataka", latitude=13.9299, longitude=75.5681)
    db_session.add(loc)
    db_session.commit()
    db_session.refresh(loc)

    crime = CrimeEvent(
        crime_type="Theft",
        crime_category="Property",
        crime_date=datetime.date(2026, 6, 1),
        location_id=loc.id
    )
    db_session.add(crime)
    db_session.commit()
    db_session.refresh(crime)

    # Seed hotspot predictions
    # 1. High probability (>=0.85 -> CRITICAL)
    p1 = Prediction(
        crime_event_id=crime.id,
        prediction_type="hotspot",
        prediction_value="Hotspot Prob: 0.90",
        confidence_score=0.90
    )
    # 2. Low probability (<0.70 -> Should not trigger alert)
    p2 = Prediction(
        crime_event_id=crime.id,
        prediction_type="hotspot",
        prediction_value="Hotspot Prob: 0.50",
        confidence_score=0.50
    )
    db_session.add_all([p1, p2])
    db_session.commit()

    service = AlertService(db_session)
    new_alerts = service.generate_alerts_from_intelligence()
    
    # Verify one alert is generated (from p1)
    assert len(new_alerts) == 1
    assert new_alerts[0].severity == "CRITICAL"
    assert "Shivamogga" in new_alerts[0].description
    assert new_alerts[0].source == "prediction"

    # Re-run and verify deduplication (should return 0 new alerts)
    re_run = service.generate_alerts_from_intelligence()
    assert len(re_run) == 0

def test_generate_decision_support_alerts(db_session):
    # Seed high priority pending recommendation
    rec = Recommendation(
        recommendation_text="Optimize Bengaluru Urban patrols",
        priority="high",
        status="pending"
    )
    db_session.add(rec)
    db_session.commit()

    service = AlertService(db_session)
    new_alerts = service.generate_alerts_from_intelligence()
    
    # At least recommendation alert + fallbacks (since we have no predictions/networks/etc.)
    # In generate_alerts_from_intelligence, it runs all sections. Since we have no geo stats >= 150,
    # recommendation is generated. Let's filter by source.
    rec_alerts = [a for a in new_alerts if a.source == "decision_support"]
    assert len(rec_alerts) >= 1
    assert rec_alerts[0].severity == "HIGH"
    assert " Bengaluru Urban patrols" in rec_alerts[0].description

def test_alert_summary_statistics(db_session):
    service = AlertService(db_session)
    
    # Seed some alerts
    a1 = Alert(title="Alert 1", description="Desc 1", severity="CRITICAL", source="prediction", status="NEW")
    a2 = Alert(title="Alert 2", description="Desc 2", severity="HIGH", source="network", status="IN_PROGRESS")
    a3 = Alert(title="Alert 3", description="Desc 3", severity="LOW", source="geo", status="RESOLVED")
    db_session.add_all([a1, a2, a3])
    db_session.commit()

    summary = service.get_summary()
    assert summary["total_active"] == 2
    assert summary["critical_count"] == 1
    assert summary["resolved_count"] == 1
    assert len(summary["by_source"]) == 3
    assert len(summary["by_severity"]) == 3
