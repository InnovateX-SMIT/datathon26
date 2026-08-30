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

def test_generate_smart_alerts(db_session):
    from backend.models.dataset import Dataset
    from backend.models.criminal import Criminal
    from backend.models.crime_participation import CrimeParticipation
    from datetime import date, timedelta

    # 1. Seed active test dataset
    test_ds = Dataset(
        id=9999,
        name="Test Dataset",
        original_filename="test.csv",
        display_name="Test Dataset",
        is_active=True,
        status="Ready",
        upload_status="Completed",
        schema_type="legacy_crime_intel"
    )
    db_session.add(test_ds)
    
    # 2. Seed Locations
    loc1 = Location(id=1, district="Bengaluru Urban", latitude=12.97, longitude=77.59)
    loc2 = Location(id=2, district="Mysuru", latitude=12.29, longitude=76.63)
    db_session.add_all([loc1, loc2])
    db_session.commit()

    # 3. Seed Crime Spikes (Bengaluru Urban: 10 crimes in last 10 days, 1 crime 45 days ago)
    anchor_date = date.today()
    for i in range(10):
        db_session.add(CrimeEvent(
            crime_type="Burglary",
            crime_category="Property",
            crime_date=anchor_date - timedelta(days=i),
            location_id=1,
            dataset_id=9999,
            description="Entered backyard door at night and stole jewelry"
        ))
    db_session.add(CrimeEvent(
        crime_type="Burglary",
        crime_category="Property",
        crime_date=anchor_date - timedelta(days=45),
        location_id=1,
        dataset_id=9999,
        description="Stole gold jewelry using crowbar"
    ))

    # 4. Seed Anomaly (Mysuru: 15 crimes in current week, 1 crime in each of the past 12 weeks)
    for i in range(15):
        db_session.add(CrimeEvent(
            crime_type="Theft",
            crime_category="Property",
            crime_date=anchor_date - timedelta(days=1),
            location_id=2,
            dataset_id=9999,
            description="Stole locked bicycle from parking lot"
        ))
    for w in range(1, 13):
        db_session.add(CrimeEvent(
            crime_type="Theft",
            crime_category="Property",
            crime_date=anchor_date - timedelta(days=w*7 + 3),
            location_id=2,
            dataset_id=9999,
            description="Stole bicycle from front porch"
        ))

    # 5. Seed Criminals & Network Co-Offending Links (John Doe & Jane Smith offending together in 2 crimes)
    c1 = Criminal(id=1, name="John Doe", age=22, gender="Male", risk_score=0.85, dataset_id=9999)
    c2 = Criminal(id=2, name="Jane Smith", age=24, gender="Female", risk_score=0.90, dataset_id=9999)
    db_session.add_all([c1, c2])
    db_session.commit()

    crime1 = CrimeEvent(id=101, crime_type="Robbery", crime_category="Violent", crime_date=anchor_date, location_id=1, dataset_id=9999, description="The suspect entered the shop through forced entry using a crowbar to target a commercial establishment.")
    crime2 = CrimeEvent(id=102, crime_type="Robbery", crime_category="Violent", crime_date=anchor_date - timedelta(days=1), location_id=2, dataset_id=9999, description="The suspect entered the store through forced entry using a crowbar to target a commercial establishment.")
    db_session.add_all([crime1, crime2])
    db_session.commit()

    db_session.add_all([
        CrimeParticipation(criminal_id=1, crime_event_id=101, dataset_id=9999),
        CrimeParticipation(criminal_id=2, crime_event_id=101, dataset_id=9999),
        CrimeParticipation(criminal_id=1, crime_event_id=102, dataset_id=9999),
        CrimeParticipation(criminal_id=2, crime_event_id=102, dataset_id=9999)
    ])
    db_session.commit()

    # 6. Run alerts generation
    service = AlertService(db_session)
    new_alerts = service.generate_alerts_from_intelligence()
    
    # 7. Assertions for each type
    alert_types = [a.alert_type for a in new_alerts]
    sources = [a.source for a in new_alerts]
    
    # Verify Crime Spike
    assert "crime_spike" in alert_types
    assert "crime_analytics" in sources
    
    # Verify Anomaly
    assert "anomaly" in alert_types
    assert "statistical_anomaly" in sources
    
    # Verify Predicted Hotspot
    assert "predicted_hotspot" in alert_types
    
    # Verify High-Risk Offenders
    assert "high_risk_offender" in alert_types
    
    # Verify Criminal Network
    assert "criminal_network" in alert_types
    assert "network" in sources
    
    # Verify Similar MO pattern
    assert "similar_mo" in alert_types
    assert "mo_intelligence" in sources
