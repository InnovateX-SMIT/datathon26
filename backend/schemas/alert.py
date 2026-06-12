from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List, Dict

class AlertBase(BaseModel):
    crime_event_id: Optional[int] = None
    title: str
    description: str
    severity: str = "medium"                      # CRITICAL, HIGH, MEDIUM, LOW
    source: str                                   # prediction, network, decision_support, geo
    status: str = "NEW"                           # NEW, ACKNOWLEDGED, IN_PROGRESS, RESOLVED, DISMISSED
    assigned_user_id: Optional[int] = None
    metadata_payload: Optional[str] = None

class AlertCreate(AlertBase):
    pass

class AlertResponse(AlertBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class AlertStatusUpdate(BaseModel):
    status: str
    assigned_user_id: Optional[int] = None

class AlertSourceStats(BaseModel):
    source: str
    count: int

class AlertSeverityStats(BaseModel):
    severity: str
    count: int

class AlertSummaryResponse(BaseModel):
    total_active: int
    critical_count: int
    resolved_count: int
    today_count: int
    by_source: List[AlertSourceStats]
    by_severity: List[AlertSeverityStats]
