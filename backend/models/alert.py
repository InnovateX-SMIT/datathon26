from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from backend.core.database import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    crime_event_id = Column(Integer, ForeignKey("crime_events.id"), index=True, nullable=True)
    alert_type = Column(String(100), nullable=False, default="default")
    message = Column(String(500), nullable=False, default="")
    title = Column(String(150), nullable=False)
    description = Column(String(1000), nullable=False)
    severity = Column(String(50), index=True, default="medium")  # CRITICAL, HIGH, MEDIUM, LOW
    source = Column(String(100), index=True, nullable=False)    # prediction, network, decision_support, geo
    status = Column(String(50), index=True, default="NEW")       # NEW, ACKNOWLEDGED, IN_PROGRESS, RESOLVED, DISMISSED
    assigned_user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=True)
    metadata_payload = Column(String(2000), nullable=True)       # JSON string for structured parameters
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    crime_event = relationship("CrimeEvent", back_populates="alerts")
    assigned_user = relationship("User", backref="assigned_alerts")
