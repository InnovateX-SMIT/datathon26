from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.models.crime import CrimeEvent
from backend.models.location import Location
from backend.models.police_station import PoliceStation
import datetime

class GeoService:
    def __init__(self, db: Session):
        self.db = db

    def _get_active_id(self) -> int:
        from backend.core.dataset_resolver import DatasetResolver
        return DatasetResolver(self.db).get_active_dataset_id()

    def get_district_crime_distribution(
        self,
        district: str = None,
        crime_type: str = None,
        start_date: datetime.date = None,
        end_date: datetime.date = None,
        dataset_id: int = None
    ) -> list[dict]:
        active_id = dataset_id or self._get_active_id()
        from analytics.geo_analysis.district_map import aggregate_district_crime
        
        query = self.db.query(
            Location.district,
            func.count(CrimeEvent.id).label("crime_count")
        ).join(
            Location, CrimeEvent.location_id == Location.id
        ).filter(
            CrimeEvent.dataset_id == active_id
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
        end_date: datetime.date = None,
        dataset_id: int = None
    ) -> list[dict]:
        active_id = dataset_id or self._get_active_id()
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
        ).filter(
            CrimeEvent.dataset_id == active_id
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
        end_date: datetime.date = None,
        dataset_id: int = None
    ) -> list[dict]:
        active_id = dataset_id or self._get_active_id()
        from analytics.geo_analysis.heatmap import generate_heatmap_json
        
        query = self.db.query(
            Location.latitude,
            Location.longitude,
            func.count(CrimeEvent.id).label("crime_count")
        ).join(
            Location, CrimeEvent.location_id == Location.id
        ).filter(
            CrimeEvent.dataset_id == active_id
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
        end_date: datetime.date = None,
        dataset_id: int = None
    ) -> list[dict]:
        active_id = dataset_id or self._get_active_id()
        from analytics.geo_analysis.hotspot import find_hotspots_dbscan
        
        query = self.db.query(
            Location.latitude,
            Location.longitude,
            func.count(CrimeEvent.id).label("crime_count")
        ).select_from(CrimeEvent).join(
            Location, CrimeEvent.location_id == Location.id
        ).filter(
            CrimeEvent.dataset_id == active_id
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
        
        coords = [(r[0], r[1], r[2]) for r in results if r[0] is not None and r[1] is not None]
        
        return find_hotspots_dbscan(coords, eps=0.1, min_samples=5)


    def get_geo_intelligence(
        self,
        district: str = None,
        crime_type: str = None,
        start_date: datetime.date = None,
        end_date: datetime.date = None
    ) -> dict:
        active_id = self._get_active_id()
        common_filters = {
            "district": district,
            "crime_type": crime_type,
            "start_date": start_date,
            "end_date": end_date,
            "dataset_id": active_id,
        }
        return {
            "districts": self.get_district_crime_distribution(**common_filters),
            "stations": self.get_station_crime_distribution(**common_filters),
            "heatmap": self.get_heatmap_points(**common_filters),
            "hotspots": self.get_hotspot_clusters(**common_filters),
        }

    # Maintain stubs for compatibility
    def compute_hotspots(self):
        return self.get_hotspot_clusters()

    def get_district_boundary(self, district_name: str):
        return {}

