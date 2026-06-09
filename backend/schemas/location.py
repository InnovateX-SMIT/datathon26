from datetime import datetime
from pydantic import BaseModel

class LocationBase(BaseModel):
    state: str = "Karnataka"
    district: str
    latitude: float | None = None
    longitude: float | None = None

class LocationCreate(LocationBase):
    pass

class LocationResponse(LocationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
