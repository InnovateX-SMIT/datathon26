from datetime import datetime
from pydantic import BaseModel

class PredictionBase(BaseModel):
    crime_event_id: int | None = None
    prediction_type: str
    prediction_value: str
    confidence_score: float = 1.0

class PredictionCreate(PredictionBase):
    pass

class PredictionResponse(PredictionBase):
    id: int
    generated_at: datetime

    model_config = {
        "from_attributes": True
    }
