from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, func
from sqlalchemy.orm import relationship
from backend.core.database import Base

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    original_filename = Column(String(200), nullable=False)
    display_name = Column(String(150), nullable=False)
    description = Column(String(500), nullable=True)
    source_type = Column(String(50), nullable=False, default="CSV") # "CSV", "Excel", "System Seed"
    upload_time = Column(DateTime(timezone=True), server_default=func.now())
    row_count = Column(Integer, default=0)
    file_size = Column(Integer, default=0)
    status = Column(String(50), default="Processing") # "Processing", "Ready", "Failed"
    is_active = Column(Boolean, default=False)
    import_summary = Column(Text, nullable=True) # JSON field as string
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    crime_events = relationship("CrimeEvent", back_populates="dataset", cascade="all, delete-orphan")
    criminals = relationship("Criminal", back_populates="dataset", cascade="all, delete-orphan")
    victims = relationship("Victim", back_populates="dataset", cascade="all, delete-orphan")
    crime_participations = relationship("CrimeParticipation", back_populates="dataset", cascade="all, delete-orphan")
