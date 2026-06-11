from pydantic import BaseModel

class DistrictCrime(BaseModel):
    district: str
    crime_count: int

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
