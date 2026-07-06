from sqlalchemy import Column, Integer, String, Date, Time, DateTime, Float, ForeignKey, func
from sqlalchemy.orm import relationship
from backend.core.database import Base

class CrimeEvent(Base):
    __tablename__ = "crime_events"

    id = Column(Integer, primary_key=True, index=True)
    crime_type = Column(String(100), index=True, nullable=False)
    crime_category = Column(String(100), index=True, nullable=False)
    crime_subcategory = Column(String(100), nullable=True)
    description = Column(String(500), nullable=True)
    severity = Column(Float, default=1.0)
    status = Column(String(50), default="reported")
    
    crime_date = Column(Date, index=True, nullable=False)
    crime_time = Column(Time, nullable=True)
    
    location_id = Column(Integer, ForeignKey("locations.id"), index=True, nullable=True)
    police_station_id = Column(Integer, ForeignKey("police_stations.id"), index=True, nullable=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id", ondelete="CASCADE"), index=True, nullable=True)
    
    victim_count = Column(Integer, default=0)
    accused_count = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    location = relationship("Location", back_populates="crime_events")
    police_station = relationship("PoliceStation", back_populates="crime_events")
    dataset = relationship("Dataset", back_populates="crime_events")
    
    victims = relationship("Victim", back_populates="crime_event")
    participations = relationship("CrimeParticipation", back_populates="crime_event")
    predictions = relationship("Prediction", back_populates="crime_event")
    alerts = relationship("Alert", back_populates="crime_event")
    recommendations = relationship("Recommendation", back_populates="crime_event")
