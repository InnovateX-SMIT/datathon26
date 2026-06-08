from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from backend.core.database import Base

class CrimeParticipation(Base):
    __tablename__ = "crime_participation"

    id = Column(Integer, primary_key=True, index=True)
    crime_event_id = Column(Integer, ForeignKey("crime_events.id"), index=True, nullable=False)
    criminal_id = Column(Integer, ForeignKey("criminals.id"), index=True, nullable=False)
    role = Column(String(100), default="accused")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    crime_event = relationship("CrimeEvent", back_populates="participations")
    criminal = relationship("Criminal", back_populates="participations")
