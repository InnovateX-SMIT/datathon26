from datetime import datetime
from pydantic import BaseModel

class CriminalBase(BaseModel):
    name: str
    gender: str | None = None
    age: float | None = None
    occupation: str | None = None
    caste: str | None = None
    risk_score: float = 0.0
    status: str = "accused"

class CriminalCreate(CriminalBase):
    pass

class CriminalResponse(CriminalBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
