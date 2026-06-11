from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

# Base schemas
class PredictionBase(BaseModel):
    crime_event_id: Optional[int] = None
    prediction_type: str
    prediction_value: str
    confidence_score: float = 1.0

class PredictionCreate(PredictionBase):
    pass

class PredictionResponse(PredictionBase):
    id: int
    generated_at: datetime

    model_config = {
        "from_attributes": True
    }

# Health Check schema
class HealthData(BaseModel):
    status: str
    models_loaded: Dict[str, bool]

class PredictionHealthResponse(BaseModel):
    success: bool = True
    data: HealthData

# Repeat Offender schemas
class RepeatOffenderRequest(BaseModel):
    age: float = Field(..., ge=0, le=120)
    occupation: str
    caste: str
    district: str

class RepeatOffenderData(BaseModel):
    probability: float
    risk_level: str

class RepeatOffenderResponse(BaseModel):
    success: bool = True
    data: RepeatOffenderData

# Crime Risk schemas
class CrimeRiskRequest(BaseModel):
    district: str
    crime_category: str
    historical_crime_count: int = Field(..., ge=0)

class CrimeRiskData(BaseModel):
    risk_score: float
    risk_level: str

class CrimeRiskResponse(BaseModel):
    success: bool = True
    data: CrimeRiskData

# Crime Type schemas
class CrimeTypeRequest(BaseModel):
    district: str
    month: int = Field(..., ge=1, le=12)
    hour: int = Field(..., ge=0, le=23)
    day_of_week: int = Field(..., ge=0, le=6)
    historical_crime_count: int = Field(..., ge=0)

class CrimeTypeData(BaseModel):
    crime_type: str
    confidence: float

class CrimeTypeResponse(BaseModel):
    success: bool = True
    data: CrimeTypeData

# Emerging Hotspot schemas
class HotspotRequest(BaseModel):
    district: str
    trend_metrics: float
    historical_crime_growth: float = Field(..., ge=0)

class HotspotData(BaseModel):
    hotspot_probability: float
    trend: str

class HotspotResponse(BaseModel):
    success: bool = True
    data: HotspotData

# Explainability schemas
class ExplainRequest(BaseModel):
    prediction_type: str  # repeat-offender, crime-risk, crime-type, hotspot
    features: Dict[str, Any]

class SHAPFeatureImpact(BaseModel):
    feature: str
    impact: float

class ExplainResponse(BaseModel):
    success: bool = True
    data: List[SHAPFeatureImpact]
