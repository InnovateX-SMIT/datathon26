from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any

class DistrictCrime(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    district: str
    crime_count: int
    latitude: float
    longitude: float

class StationCrime(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    station: str
    crime_count: int
    latitude: float
    longitude: float

class HeatmapPoint(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    latitude: float
    longitude: float
    weight: int

class HotspotCluster(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    cluster_id: int
    crime_count: int
    latitude: float
    longitude: float
    first_incident_date: Optional[str] = None
    last_incident_date: Optional[str] = None
    peak_hour_window: Optional[str] = None
    temporal_category: Optional[str] = "Recurring Historical Cluster"
    hotspot_type: str = "Historical Descriptive Cluster"

class GeoMarkerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    crime_no: str
    crime_type: str
    police_station: str
    district: str
    crime_date: str
    status: str
    latitude: float
    longitude: float

class HourlyDataPoint(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    hour: int
    label: str
    count: int

class TimePeriodDistribution(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    morning: int = 0
    afternoon: int = 0
    evening: int = 0
    night: int = 0

class TimeOfDayResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    hourly: List[HourlyDataPoint]
    periods: TimePeriodDistribution
    category_by_time: List[Dict[str, Any]] = []
    peak_hour: Optional[str] = None
    peak_period: Optional[str] = None
    total_analyzed: int = 0

class GeoIntelligenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    districts: List[DistrictCrime]
    stations: List[StationCrime]
    heatmap: List[HeatmapPoint]
    hotspots: List[HotspotCluster]
    markers: List[GeoMarkerResponse]
    time_of_day: Optional[TimeOfDayResponse] = None
