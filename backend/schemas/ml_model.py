from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class MLModelBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class MLModelResponse(MLModelBase):
    id: int
    version: str
    model_type: str
    training_dataset_ids: str
    algorithm: str
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    roc_auc: Optional[float] = None
    training_duration: Optional[float] = None
    status: str
    model_path: Optional[str] = None
    is_production: bool
    training_logs: Optional[str] = None
    created_at: datetime

class MLModelCompareRequest(BaseModel):
    model_id_1: int
    model_id_2: int

class MLModelCompareResponse(BaseModel):
    model_1: MLModelResponse
    model_2: MLModelResponse
    metrics_difference: dict

class TrainingProgressResponse(BaseModel):
    model_id: int
    status: str
    progress: int  # 0 to 100 percentage
    logs: Optional[str] = None

class TrainModelRequest(BaseModel):
    model_type: str  # "repeat_offender", "crime_type", "crime_risk", "hotspot"
