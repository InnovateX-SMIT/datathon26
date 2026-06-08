from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from backend.core.database import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    crime_event_id = Column(Integer, ForeignKey("crime_events.id"), index=True, nullable=True)
    alert_type = Column(String(100), nullable=False)
    severity = Column(String(50), index=True, default="medium")
    message = Column(String(500), nullable=False)
    status = Column(String(50), index=True, default="unread")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    crime_event = relationship("CrimeEvent", back_populates="alerts")
