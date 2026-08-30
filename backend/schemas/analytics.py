from pydantic import BaseModel

class DashboardSummaryResponse(BaseModel):
    total_crimes: int
    total_victims: int
    total_accused: int
    active_cases: int
    high_risk_criminals: int
    total_criminals: int
    crime_resolution_rate: float
    average_severity: float
    districts_count: int
    stations_count: int

class TrendDataPoint(BaseModel):
    date: str       # "YYYY-MM-DD"
    count: int

class CategoryDataPoint(BaseModel):
    category: str
    count: int

class DistrictDataPoint(BaseModel):
    district: str
    count: int

class RecentCrimeItem(BaseModel):
    id: int
    crime_type: str
    crime_category: str
    district: str
    severity: float
    status: str
    crime_date: str   # "YYYY-MM-DD"
    victim_count: int
    accused_count: int

class SystemStatusResponse(BaseModel):
    database_status: str
    total_records: int
    last_updated: str
    data_coverage_days: int

class OverviewResponse(BaseModel):
    total_crimes: int
    total_victims: int
    total_accused: int

class TrendResponse(BaseModel):
    period: str
    count: int

class CategoryItem(BaseModel):
    name: str
    count: int

class CategoryResponse(BaseModel):
    categories: list[CategoryItem]
    subcategories: list[CategoryItem]

class ComparisonResponse(BaseModel):
    current_month: int
    previous_month: int
    month_change_percent: float
    current_year: int
    previous_year: int
    year_change_percent: float


# Phase 7: Sociological Intelligence & Correlation Analysis Schemas

class DemographicItem(BaseModel):
    category: str
    count: int

class AgeVsCrimeItem(BaseModel):
    age_group: str
    crime_category: str
    count: int

class GenderVsCrimeItem(BaseModel):
    gender: str
    crime_category: str
    count: int

class DistrictDemographicItem(BaseModel):
    district: str
    average_offender_age: float
    predominant_gender: str
    predominant_crime_category: str
    count: int

class DemographicsResponse(BaseModel):
    offender_age_distribution: list[DemographicItem]
    offender_gender_distribution: list[DemographicItem]
    victim_age_distribution: list[DemographicItem]
    victim_gender_distribution: list[DemographicItem]
    age_vs_crime: list[AgeVsCrimeItem]
    gender_vs_crime: list[GenderVsCrimeItem]
    district_demographics: list[DistrictDemographicItem]
    data_limitations: list[str]

class RiskCorrelationItem(BaseModel):
    group: str
    average_risk: float

class CorrelationMetric(BaseModel):
    variables: str
    correlation_type: str
    correlation_coefficient: float
    sample_size: int
    geographic_level: str
    time_period: str
    interpretation: str

class SociologicalRiskResponse(BaseModel):
    age_group_risk: list[RiskCorrelationItem]
    gender_risk: list[RiskCorrelationItem]
    district_risk: list[RiskCorrelationItem]
    repeat_involvement_risk: list[RiskCorrelationItem]
    correlations: list[CorrelationMetric]

class SocioEconomicCorrelationResponse(BaseModel):
    data_available: bool
    error_message: str


