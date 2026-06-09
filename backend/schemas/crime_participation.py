from datetime import datetime
from pydantic import BaseModel

class CrimeParticipationBase(BaseModel):
    crime_event_id: int
    criminal_id: int
    role: str = "accused"

class CrimeParticipationCreate(CrimeParticipationBase):
    pass

class CrimeParticipationResponse(CrimeParticipationBase):
    id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
