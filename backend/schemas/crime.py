from datetime import datetime, date, time
from pydantic import BaseModel

class CrimeEventBase(BaseModel):
    crime_type: str
    crime_category: str
    crime_subcategory: str | None = None
    description: str | None = None
    severity: float = 1.0
    status: str = "reported"
    crime_date: date
    crime_time: time | None = None
    location_id: int | None = None
    police_station_id: int | None = None
    victim_count: int = 0
    accused_count: int = 0

class CrimeEventCreate(CrimeEventBase):
    pass

class CrimeEventResponse(CrimeEventBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
