from datetime import datetime
from pydantic import BaseModel

class RecommendationBase(BaseModel):
    crime_event_id: int | None = None
    priority: str = "medium"
    recommendation_text: str
    reason: str | None = None
    status: str = "pending"
    confidence: float | None = 0.80
    supporting_analytics: str | None = None

class RecommendationCreate(RecommendationBase):
    pass

class RecommendationResponse(RecommendationBase):
    id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class AllocationPayload(BaseModel):
    district: str
    sanctioned_asi: int
    sanctioned_chc: int
    sanctioned_cpc: int


class BeatAllocation(BaseModel):
    beat_name: str
    asi_allocated: int
    chc_allocated: int
    cpc_allocated: int
    normalized_severity: float


class AllocationResponse(BaseModel):
    status: str
    district: str
    solved_allocation: list[BeatAllocation]


class ResourceAllocationResponse(BaseModel):
    id: int
    district: str
    allocated_asi: int
    allocated_chc: int
    allocated_cpc: int
    solved_allocation: list[BeatAllocation]
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class RecommendationStatusUpdate(BaseModel):
    status: str


class RecommendationHistoryResponse(BaseModel):
    id: int
    dataset_ids: str
    model_version: str
    alert_count: int
    generated_recommendations_count: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
