from pydantic import BaseModel
from typing import List

class DistrictCrime(BaseModel):
    district: str
    crime_count: int
    latitude: float
    longitude: float

    class Config:
        from_attributes = True

class StationCrime(BaseModel):
    station: str
    crime_count: int
    latitude: float
    longitude: float

    class Config:
        from_attributes = True

class HeatmapPoint(BaseModel):
    latitude: float
    longitude: float
    weight: int

    class Config:
        from_attributes = True

class HotspotCluster(BaseModel):
    cluster_id: int
    crime_count: int
    latitude: float
    longitude: float

    class Config:
        from_attributes = True

class GeoMarkerResponse(BaseModel):
    id: int
    crime_no: str
    crime_type: str
    police_station: str
    district: str
    crime_date: str
    status: str
    latitude: float
    longitude: float

    class Config:
        from_attributes = True

class GeoIntelligenceResponse(BaseModel):
    districts: List[DistrictCrime]
    stations: List[StationCrime]
    heatmap: List[HeatmapPoint]
    hotspots: List[HotspotCluster]
    markers: List[GeoMarkerResponse]
