from datetime import datetime
from pydantic import BaseModel

class ReportBase(BaseModel):
    title: str
    summary: str | None = None
    report_type: str

class ReportCreate(ReportBase):
    pass

class ReportResponse(ReportBase):
    id: int
    generated_at: datetime

    model_config = {
        "from_attributes": True
    }
