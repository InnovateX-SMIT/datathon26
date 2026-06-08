from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from backend.core.database import Base

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    crime_event_id = Column(Integer, ForeignKey("crime_events.id"), index=True, nullable=True)
    prediction_type = Column(String(100), index=True, nullable=False)
    prediction_value = Column(String(255), nullable=False)
    confidence_score = Column(Float, default=1.0)
    
    generated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    crime_event = relationship("CrimeEvent", back_populates="predictions")
