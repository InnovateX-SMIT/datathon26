from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.sql import func
from backend.core.database import Base

class MLModel(Base):
    __tablename__ = "ml_models"

    id = Column(Integer, primary_key=True, index=True)
    version = Column(String(50), nullable=False)
    model_type = Column(String(50), nullable=False)  # "repeat_offender", "crime_type", "crime_risk", "hotspot"
    training_dataset_ids = Column(String(200), nullable=False)  # Comma-separated list of IDs: e.g. "1,2"
    algorithm = Column(String(100), nullable=False, default="XGBoost")
    accuracy = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    roc_auc = Column(Float, nullable=True)
    training_duration = Column(Float, nullable=True)  # in seconds
    status = Column(String(50), nullable=False, default="Queued")  # "Queued", "Preparing Data", "Preprocessing", "Training", "Evaluating", "Saving Model", "Completed", "Failed"
    model_path = Column(String(500), nullable=True)
    is_production = Column(Boolean, nullable=False, default=False)
    training_logs = Column(String(4000), nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
