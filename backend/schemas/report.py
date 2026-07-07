from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ReportBase(BaseModel):
    title: str
    summary: Optional[str] = None
    report_type: str

class ReportCreate(ReportBase):
    pass

class GenerateReportRequest(BaseModel):
    title: str
    report_type: str

class ReportTypeInfo(BaseModel):
    key: str
    name: str
    description: str

class ReportTypeResponse(BaseModel):
    types: List[ReportTypeInfo]

class ReportSummaryResponse(BaseModel):
    id: int
    report_id: int
    title: str
    report_type: str
    generated_at: datetime
    executive_summary: Optional[str] = None

    class Config:
        from_attributes = True

class ReportListResponse(BaseModel):
    reports: List[ReportSummaryResponse]

class CrimeCategoryBreakdown(BaseModel):
    category: str
    count: int

class CrimeOverview(BaseModel):
    total_crimes: int
    top_categories: List[CrimeCategoryBreakdown]
    trend_direction: str

class HighRiskLocation(BaseModel):
    district: str
    crime_count: int
    risk_level: str

class PredictiveInsights(BaseModel):
    high_risk_locations: List[HighRiskLocation]
    hotspot_count: int
    risk_score_summary: Dict[str, Any]

class NetworkKeyEntity(BaseModel):
    id: str
    type: str
    label: str
    score: float

class NetworkInsights(BaseModel):
    total_networks: int
    largest_network_size: int
    key_entities: List[NetworkKeyEntity]

class ReportResponse(BaseModel):
    report_id: int
    report_type: str
    title: str
    generated_at: datetime
    executive_summary: str
    crime_overview: CrimeOverview
    predictive_insights: PredictiveInsights
    network_insights: NetworkInsights
    recommendations: List[Dict[str, Any]]
    alerts: List[Dict[str, Any]]
    dataset_name: Optional[str] = None
    model_version: Optional[str] = None
    prediction_accuracy: Optional[float] = None

    class Config:
        from_attributes = True
