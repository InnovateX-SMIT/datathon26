from pydantic import BaseModel

class DashboardSummaryResponse(BaseModel):
    total_crimes: int
    total_victims: int
    total_accused: int
    active_cases: int
    high_risk_criminals: int
    total_criminals: int

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

