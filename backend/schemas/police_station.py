from datetime import datetime
from pydantic import BaseModel

class PoliceStationBase(BaseModel):
    station_name: str
    district: str
    beat: str | None = None
    location_id: int | None = None
    officer_count: int = 0
    vehicle_count: int = 0
    equipment_count: int = 0
    capacity: int = 0
    availability: str = "available"

class PoliceStationCreate(PoliceStationBase):
    pass

class PoliceStationResponse(PoliceStationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
