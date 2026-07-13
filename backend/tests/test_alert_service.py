import pytest
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.core.database import Base
from backend.models.alert import Alert
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
