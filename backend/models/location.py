from sqlalchemy import Column, Integer, String, Float, DateTime, func
from sqlalchemy.orm import relationship
from backend.core.database import Base

class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    state = Column(String(100), default="Karnataka", nullable=False)
    district = Column(String(100), index=True, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    police_stations = relationship("PoliceStation", back_populates="location")
    crime_events = relationship("CrimeEvent", back_populates="location")
    victims = relationship("Victim", back_populates="location")
