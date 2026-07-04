from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
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

