from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from backend.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    entity_type = Column(String(50), nullable=True, index=True)
    entity_id = Column(Integer, nullable=True)
    details = Column(String(2000), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Use backref to avoid modifying user.py
    user = relationship("User", backref="audit_logs")
