from sqlalchemy import Column, Integer, String, Float, DateTime, func
from sqlalchemy.orm import relationship
from backend.core.database import Base

class Criminal(Base):
    __tablename__ = "criminals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    gender = Column(String(20), nullable=True)
    age = Column(Float, index=True, nullable=True)
    occupation = Column(String(100), index=True, nullable=True)
    caste = Column(String(100), nullable=True)
    risk_score = Column(Float, index=True, default=0.0)
    status = Column(String(50), default="accused")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    participations = relationship("CrimeParticipation", back_populates="criminal")
