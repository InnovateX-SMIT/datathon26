from datetime import datetime
from pydantic import BaseModel

class RecommendationBase(BaseModel):
    crime_event_id: int | None = None
    priority: str = "medium"
    recommendation_text: str
    reason: str | None = None
    status: str = "pending"

class RecommendationCreate(RecommendationBase):
    pass

class RecommendationResponse(RecommendationBase):
    id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
