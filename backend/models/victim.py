from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from backend.core.database import Base

class Victim(Base):
    __tablename__ = "victims"

    id = Column(Integer, primary_key=True, index=True)
    crime_event_id = Column(Integer, ForeignKey("crime_events.id"), index=True, nullable=False)
    gender = Column(String(20), nullable=True)
    age = Column(Float, index=True, nullable=True)
    occupation = Column(String(100), nullable=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    crime_event = relationship("CrimeEvent", back_populates="victims")
    location = relationship("Location", back_populates="victims")
