from datetime import datetime
from pydantic import BaseModel

class VictimBase(BaseModel):
    crime_event_id: int
    gender: str | None = None
    age: float | None = None
    occupation: str | None = None
    location_id: int | None = None

class VictimCreate(VictimBase):
    pass

class VictimResponse(VictimBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
