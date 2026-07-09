from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Any
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

    def _get_active_ids(self) -> list[int]:
        from backend.core.dataset_resolver import DatasetResolver
        active_ids = DatasetResolver(self.db).get_active_dataset_ids()
        # Data compatibility validation
        from backend.models.dataset import Dataset
        for aid in active_ids:
            if aid is None:
                continue
            ds = self.db.query(Dataset).filter(Dataset.id == aid).first()
            if not ds or ds.status != "Ready":
                raise ValueError("One or more active datasets are not ready or are incompatible.")
        return active_ids

    def _get_schema_type(self) -> str:
        from backend.core.dataset_resolver import DatasetResolver
        return DatasetResolver(self.db).get_active_dataset_schema_type()

    def _get_cache_key(self, active_ids: list[int]) -> tuple:
        from backend.models.dataset import Dataset
        from sqlalchemy import func
        max_updated = self.db.query(func.max(Dataset.updated_at)).filter(
            Dataset.id.in_(active_ids)
        ).scalar()
        max_updated_str = max_updated.isoformat() if max_updated else "none"
        return (tuple(sorted(active_ids)), max_updated_str)

    def _check_cache(self, method_name: str, active_ids: list[int], *args, **kwargs) -> tuple[bool, Any, tuple]:
        from backend.core.analytics_cache import AnalyticsCache
        cache_key = self._get_cache_key(active_ids)
        full_key = (cache_key, args, tuple(sorted(kwargs.items())))
        cached_val = AnalyticsCache.get(method_name, full_key)
        if cached_val is not None:
            return True, cached_val, full_key
        return False, None, full_key

    def _set_cache(self, method_name: str, full_key: tuple, value: Any):
        from backend.core.analytics_cache import AnalyticsCache
        AnalyticsCache.set(method_name, full_key, value)

    def get_district_crime_distribution(
        self,
        district: str = None,
        crime_type: str = None,
        start_date: datetime.date = None,
        end_date: datetime.date = None,
        dataset_id: int = None
    ) -> list[dict]:
        active_ids = [dataset_id] if dataset_id else self._get_active_ids()
        
        args_tuple = (district, crime_type, start_date.isoformat() if start_date else None, end_date.isoformat() if end_date else None)
        is_cached, val, full_key = self._check_cache("get_district_crime_distribution", active_ids, *args_tuple)
        if is_cached:
            return val

        from analytics.geo_analysis.district_map import aggregate_district_crime
        schema_type = self._get_schema_type()

        if schema_type == "fir_normalized":
            from backend.models.fir_case import CaseMaster
            from backend.models.fir_geography import District
            from backend.models.fir_organization import Unit
            from backend.models.fir_law import CrimeSubHead

            query = self.db.query(
                District.name,
                func.count(CaseMaster.id).label("crime_count")
            ).select_from(CaseMaster).join(Unit, CaseMaster.PoliceStationID == Unit.id).join(District, Unit.DistrictID == District.id).filter(
                CaseMaster.dataset_id.in_(active_ids)
            )
            
            if district:
                query = query.filter(District.name == district)
            if crime_type:
                query = query.join(CrimeSubHead, CaseMaster.CrimeMinorHeadID == CrimeSubHead.id).filter(CrimeSubHead.CrimeHeadName == crime_type)
            if start_date:
                query = query.filter(CaseMaster.CrimeRegisteredDate >= start_date)
            if end_date:
                query = query.filter(CaseMaster.CrimeRegisteredDate <= end_date)
                
            results = query.group_by(District.name).all()
            records = [{"district": r[0], "crime_count": r[1]} for r in results if r[0] is not None]
        else:
            query = self.db.query(
                Location.district,
                func.count(CrimeEvent.id).label("crime_count")
            ).join(
                Location, CrimeEvent.location_id == Location.id
            ).filter(
                CrimeEvent.dataset_id.in_(active_ids)
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
        
        result = aggregate_district_crime(records)
        self._set_cache("get_district_crime_distribution", full_key, result)
        return result

    def get_station_crime_distribution(
        self,
        district: str = None,
        crime_type: str = None,
        start_date: datetime.date = None,
        end_date: datetime.date = None,
        dataset_id: int = None
    ) -> list[dict]:
        active_ids = [dataset_id] if dataset_id else self._get_active_ids()

        args_tuple = (district, crime_type, start_date.isoformat() if start_date else None, end_date.isoformat() if end_date else None)
        is_cached, val, full_key = self._check_cache("get_station_crime_distribution", active_ids, *args_tuple)
        if is_cached:
            return val

        from analytics.geo_analysis.station_map import aggregate_station_crime
        schema_type = self._get_schema_type()

        if schema_type == "fir_normalized":
            from backend.models.fir_case import CaseMaster
            from backend.models.fir_geography import District
            from backend.models.fir_organization import Unit
            from backend.models.fir_law import CrimeSubHead
            from backend.models.fir_case import Inv_OccuranceTime

            query = self.db.query(
                Unit.name,
                func.count(CaseMaster.id).label("crime_count"),
                func.avg(Inv_OccuranceTime.latitude),
                func.avg(Inv_OccuranceTime.longitude)
            ).select_from(CaseMaster).join(Unit, CaseMaster.PoliceStationID == Unit.id).join(District, Unit.DistrictID == District.id).join(
                Inv_OccuranceTime, Inv_OccuranceTime.CaseMasterID == CaseMaster.id
            ).filter(
                CaseMaster.dataset_id.in_(active_ids)
            )

            if district:
                query = query.filter(District.name == district)
            if crime_type:
                query = query.join(CrimeSubHead, CaseMaster.CrimeMinorHeadID == CrimeSubHead.id).filter(CrimeSubHead.CrimeHeadName == crime_type)
            if start_date:
                query = query.filter(CaseMaster.CrimeRegisteredDate >= start_date)
            if end_date:
                query = query.filter(CaseMaster.CrimeRegisteredDate <= end_date)
                
            results = query.group_by(Unit.name).all()
            records = [{
                "station": r[0],
                "crime_count": r[1],
                "latitude": float(r[2]) if r[2] is not None else 0.0,
                "longitude": float(r[3]) if r[3] is not None else 0.0
            } for r in results if r[0] is not None]
        else:
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
                CrimeEvent.dataset_id.in_(active_ids)
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
        
        result = aggregate_station_crime(records)
        self._set_cache("get_station_crime_distribution", full_key, result)
        return result

    def get_heatmap_points(
        self,
        district: str = None,
        crime_type: str = None,
        start_date: datetime.date = None,
        end_date: datetime.date = None,
        dataset_id: int = None
    ) -> list[dict]:
        active_ids = [dataset_id] if dataset_id else self._get_active_ids()

        args_tuple = (district, crime_type, start_date.isoformat() if start_date else None, end_date.isoformat() if end_date else None)
        is_cached, val, full_key = self._check_cache("get_heatmap_points", active_ids, *args_tuple)
        if is_cached:
            return val

        from analytics.geo_analysis.heatmap import generate_heatmap_json
        schema_type = self._get_schema_type()

        if schema_type == "fir_normalized":
            from backend.models.fir_case import CaseMaster
            from backend.models.fir_geography import District
            from backend.models.fir_organization import Unit
            from backend.models.fir_law import CrimeSubHead
            from backend.models.fir_case import Inv_OccuranceTime

            query = self.db.query(
                Inv_OccuranceTime.latitude,
                Inv_OccuranceTime.longitude,
                func.count(CaseMaster.id).label("crime_count")
            ).select_from(CaseMaster).join(Inv_OccuranceTime, Inv_OccuranceTime.CaseMasterID == CaseMaster.id).join(
                Unit, CaseMaster.PoliceStationID == Unit.id
            ).join(
                District, Unit.DistrictID == District.id
            ).filter(
                CaseMaster.dataset_id.in_(active_ids)
            )

            if district:
                query = query.filter(District.name == district)
            if crime_type:
                query = query.join(CrimeSubHead, CaseMaster.CrimeMinorHeadID == CrimeSubHead.id).filter(CrimeSubHead.CrimeHeadName == crime_type)
            if start_date:
                query = query.filter(CaseMaster.CrimeRegisteredDate >= start_date)
            if end_date:
                query = query.filter(CaseMaster.CrimeRegisteredDate <= end_date)

            results = query.group_by(Inv_OccuranceTime.latitude, Inv_OccuranceTime.longitude).all()
            records = [{
                "latitude": float(r[0]) if r[0] is not None else 0.0,
                "longitude": float(r[1]) if r[1] is not None else 0.0,
                "weight": r[2]
            } for r in results]
        else:
            query = self.db.query(
                Location.latitude,
                Location.longitude,
                func.count(CrimeEvent.id).label("crime_count")
            ).join(
                Location, CrimeEvent.location_id == Location.id
            ).filter(
                CrimeEvent.dataset_id.in_(active_ids)
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
        
        result = generate_heatmap_json(records)
        self._set_cache("get_heatmap_points", full_key, result)
        return result

    def get_hotspot_clusters(
        self,
        district: str = None,
        crime_type: str = None,
        start_date: datetime.date = None,
        end_date: datetime.date = None,
        dataset_id: int = None
    ) -> list[dict]:
        active_ids = [dataset_id] if dataset_id else self._get_active_ids()

        args_tuple = (district, crime_type, start_date.isoformat() if start_date else None, end_date.isoformat() if end_date else None)
        is_cached, val, full_key = self._check_cache("get_hotspot_clusters", active_ids, *args_tuple)
        if is_cached:
            return val

        from analytics.geo_analysis.hotspot import find_hotspots_dbscan
        schema_type = self._get_schema_type()

        if schema_type == "fir_normalized":
            from backend.models.fir_case import CaseMaster
            from backend.models.fir_geography import District
            from backend.models.fir_organization import Unit
            from backend.models.fir_law import CrimeSubHead
            from backend.models.fir_case import Inv_OccuranceTime

            query = self.db.query(
                Inv_OccuranceTime.latitude,
                Inv_OccuranceTime.longitude,
                func.count(CaseMaster.id).label("crime_count")
            ).select_from(CaseMaster).join(Inv_OccuranceTime, Inv_OccuranceTime.CaseMasterID == CaseMaster.id).join(
                Unit, CaseMaster.PoliceStationID == Unit.id
            ).join(
                District, Unit.DistrictID == District.id
            ).filter(
                CaseMaster.dataset_id.in_(active_ids)
            )

            if district:
                query = query.filter(District.name == district)
            if crime_type:
                query = query.join(CrimeSubHead, CaseMaster.CrimeMinorHeadID == CrimeSubHead.id).filter(CrimeSubHead.CrimeHeadName == crime_type)
            if start_date:
                query = query.filter(CaseMaster.CrimeRegisteredDate >= start_date)
            if end_date:
                query = query.filter(CaseMaster.CrimeRegisteredDate <= end_date)

            results = query.group_by(Inv_OccuranceTime.latitude, Inv_OccuranceTime.longitude).all()
            coords = [(float(r[0]), float(r[1]), r[2]) for r in results if r[0] is not None and r[1] is not None]
        else:
            query = self.db.query(
                Location.latitude,
                Location.longitude,
                func.count(CrimeEvent.id).label("crime_count")
            ).select_from(CrimeEvent).join(
                Location, CrimeEvent.location_id == Location.id
            ).filter(
                CrimeEvent.dataset_id.in_(active_ids)
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
        
        result = find_hotspots_dbscan(coords, eps=0.1, min_samples=5)
        self._set_cache("get_hotspot_clusters", full_key, result)
        return result

    def get_geo_intelligence(
        self,
        district: str = None,
        crime_type: str = None,
        start_date: datetime.date = None,
        end_date: datetime.date = None
    ) -> dict:
        active_ids = self._get_active_ids()
        
        args_tuple = (district, crime_type, start_date.isoformat() if start_date else None, end_date.isoformat() if end_date else None)
        is_cached, val, full_key = self._check_cache("get_geo_intelligence", active_ids, *args_tuple)
        if is_cached:
            return val

        common_filters = {
            "district": district,
            "crime_type": crime_type,
            "start_date": start_date,
            "end_date": end_date,
        }
        
        result = {
            "districts": self.get_district_crime_distribution(**common_filters),
            "stations": self.get_station_crime_distribution(**common_filters),
            "heatmap": self.get_heatmap_points(**common_filters),
            "hotspots": self.get_hotspot_clusters(**common_filters),
        }
        self._set_cache("get_geo_intelligence", full_key, result)
        return result

    def compute_hotspots(self):
        return self.get_hotspot_clusters()

    def get_district_boundary(self, district_name: str):
        return {}
