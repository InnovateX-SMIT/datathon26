from sqlalchemy import Column, Integer, String, DateTime, func
from backend.core.database import Base

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    summary = Column(String(2000), nullable=True)
    report_type = Column(String(100), index=True, nullable=False)
    
    generated_at = Column(DateTime(timezone=True), index=True, server_default=func.now())
