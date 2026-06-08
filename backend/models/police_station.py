from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from backend.core.database import Base

class PoliceStation(Base):
    __tablename__ = "police_stations"

    id = Column(Integer, primary_key=True, index=True)
    station_name = Column(String(150), index=True, nullable=False)
    district = Column(String(100), index=True, nullable=False)
    beat = Column(String(100), nullable=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    
    officer_count = Column(Integer, default=0)
    vehicle_count = Column(Integer, default=0)
    equipment_count = Column(Integer, default=0)
    capacity = Column(Integer, default=0)
    availability = Column(String(50), default="available")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    location = relationship("Location", back_populates="police_stations")
    crime_events = relationship("CrimeEvent", back_populates="police_station")
