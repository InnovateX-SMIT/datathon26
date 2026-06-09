from datetime import datetime
from pydantic import BaseModel

class AlertBase(BaseModel):
    crime_event_id: int | None = None
    alert_type: str
    severity: str = "medium"
    message: str
    status: str = "unread"

class AlertCreate(AlertBase):
    pass

class AlertResponse(AlertBase):
    id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
