from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, func
from sqlalchemy.orm import relationship
from backend.core.database import Base

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    crime_event_id = Column(Integer, ForeignKey("crime_events.id"), index=True, nullable=True)
    priority = Column(String(50), index=True, default="medium")
    recommendation_text = Column(String(1000), nullable=False)
    reason = Column(String(1000), nullable=True)
    status = Column(String(50), index=True, default="pending")
    confidence = Column(Float, nullable=True, default=0.80)
    supporting_analytics = Column(String(1000), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    crime_event = relationship("CrimeEvent", back_populates="recommendations")


class ResourceAllocation(Base):
    __tablename__ = "resource_allocations"

    id = Column(Integer, primary_key=True, index=True)
    district = Column(String(100), nullable=False, index=True)
    allocated_asi = Column(Integer, nullable=False)
    allocated_chc = Column(Integer, nullable=False)
    allocated_cpc = Column(Integer, nullable=False)
    solved_allocation = Column(String(2000), nullable=False)  # JSON-serialized list of beat allocations
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class RecommendationHistory(Base):
    __tablename__ = "recommendation_history"

    id = Column(Integer, primary_key=True, index=True)
    dataset_ids = Column(String(200), nullable=False)
    model_version = Column(String(100), nullable=False)
    alert_count = Column(Integer, nullable=False, default=0)
    generated_recommendations_count = Column(Integer, nullable=False, default=0)
    status = Column(String(50), nullable=False, default="completed")  # "completed", "failed"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
