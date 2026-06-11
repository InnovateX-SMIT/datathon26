from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.models.crime import CrimeEvent
from backend.models.location import Location
from backend.models.police_station import PoliceStation
import datetime

class GeoService:
    def __init__(self, db: Session):
        self.db = db

    def get_district_crime_distribution(
        self,
        district: str = None,
        crime_type: str = None,
        start_date: datetime.date = None,
        end_date: datetime.date = None
    ) -> list[dict]:
        from analytics.geo_analysis.district_map import aggregate_district_crime
        
        query = self.db.query(
            Location.district,
            func.count(CrimeEvent.id).label("crime_count")
        ).join(
            Location, CrimeEvent.location_id == Location.id
        )
        
        if district:
            query = query.filter(Location.district == district)
        if crime_type:
            query = query.filter(CrimeEvent.crime_type == crime_type)
        if start_date:
            query = query.filter(CrimeEvent.crime_date >= start_date)
        if end_date:
            query = query.filter(CrimeEvent.crime_date <= end_date)
            
        results = query.group_by(Location.district).all()
        
        records = [{"district": r[0], "crime_count": r[1]} for r in results if r[0] is not None]
        return aggregate_district_crime(records)

    def get_station_crime_distribution(
        self,
        district: str = None,
        crime_type: str = None,
        start_date: datetime.date = None,
        end_date: datetime.date = None
    ) -> list[dict]:
        from analytics.geo_analysis.station_map import aggregate_station_crime
        
        query = self.db.query(
            PoliceStation.station_name,
            func.count(CrimeEvent.id).label("crime_count"),
            Location.latitude,
            Location.longitude
        ).join(
            PoliceStation, CrimeEvent.police_station_id == PoliceStation.id
        ).join(
            Location, PoliceStation.location_id == Location.id
        )
        
        if district:
            query = query.filter(Location.district == district)
        if crime_type:
            query = query.filter(CrimeEvent.crime_type == crime_type)
        if start_date:
            query = query.filter(CrimeEvent.crime_date >= start_date)
        if end_date:
            query = query.filter(CrimeEvent.crime_date <= end_date)
            
        results = query.group_by(PoliceStation.station_name, Location.latitude, Location.longitude).all()
        
        records = [{
            "station": r[0],
            "crime_count": r[1],
            "latitude": r[2] if r[2] is not None else 0.0,
            "longitude": r[3] if r[3] is not None else 0.0
        } for r in results if r[0] is not None]
        
        return aggregate_station_crime(records)

    def get_heatmap_points(
        self,
        district: str = None,
        crime_type: str = None,
        start_date: datetime.date = None,
        end_date: datetime.date = None
    ) -> list[dict]:
        from analytics.geo_analysis.heatmap import generate_heatmap_json
        
        query = self.db.query(
            Location.latitude,
            Location.longitude,
            func.count(CrimeEvent.id).label("crime_count")
        ).join(
            Location, CrimeEvent.location_id == Location.id
        )
        
        if district:
            query = query.filter(Location.district == district)
        if crime_type:
            query = query.filter(CrimeEvent.crime_type == crime_type)
        if start_date:
            query = query.filter(CrimeEvent.crime_date >= start_date)
        if end_date:
            query = query.filter(CrimeEvent.crime_date <= end_date)
            
        results = query.group_by(Location.latitude, Location.longitude).all()
        
        records = [{
            "latitude": r[0] if r[0] is not None else 0.0,
            "longitude": r[1] if r[1] is not None else 0.0,
            "weight": r[2]
        } for r in results]
        
        return generate_heatmap_json(records)

    def get_hotspot_clusters(
        self,
        district: str = None,
        crime_type: str = None,
        start_date: datetime.date = None,
        end_date: datetime.date = None
    ) -> list[dict]:
        from analytics.geo_analysis.hotspot import find_hotspots_dbscan
        
        query = self.db.query(
            Location.latitude,
            Location.longitude
        ).select_from(CrimeEvent).join(
            Location, CrimeEvent.location_id == Location.id
        )
        
        if district:
            query = query.filter(Location.district == district)
        if crime_type:
            query = query.filter(CrimeEvent.crime_type == crime_type)
        if start_date:
            query = query.filter(CrimeEvent.crime_date >= start_date)
        if end_date:
            query = query.filter(CrimeEvent.crime_date <= end_date)
            
        results = query.all()
        
        coords = [(r[0], r[1]) for r in results if r[0] is not None and r[1] is not None]
        
        return find_hotspots_dbscan(coords, eps=0.1, min_samples=5)

    # Maintain stubs for compatibility
    def compute_hotspots(self):
        return self.get_hotspot_clusters()

    def get_district_boundary(self, district_name: str):
        return {}
