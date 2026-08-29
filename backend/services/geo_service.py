import os
import json
import datetime
from typing import Any, Optional, Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from backend.models.crime import CrimeEvent
from backend.models.location import Location
from backend.models.police_station import PoliceStation

class GeoService:
    def __init__(self, db: Session, session_id: Optional[str] = None):
        self.db = db
        self.session_id = session_id

    def _get_active_id(self) -> int:
        from backend.core.dataset_resolver import DatasetResolver
        return DatasetResolver(self.db, self.session_id).get_active_dataset_id()

    def _get_active_ids(self) -> list[int]:
        from backend.core.dataset_resolver import DatasetResolver
        active_ids = DatasetResolver(self.db, self.session_id).get_active_dataset_ids()
        # Data compatibility validation
        from backend.models.dataset import Dataset
        acceptable_statuses = ["Ready", "Completed", "Active", "Processed"]
        for aid in active_ids:
            if aid is None:
                continue
            ds = self.db.query(Dataset).filter(Dataset.id == aid).first()
            if ds and ds.status in ["Uploading", "Processing", "Failed", "Archived"]:
                raise ValueError("One or more active datasets are not ready or are incompatible.")
        return active_ids

    def _get_schema_type(self) -> str:
        from backend.core.dataset_resolver import DatasetResolver
        return DatasetResolver(self.db, self.session_id).get_active_dataset_schema_type()

    def _get_cache_key(self, active_ids: list[int]) -> tuple:
        from backend.models.dataset import Dataset
        max_updated = self.db.query(func.max(Dataset.updated_at)).filter(
            Dataset.id.in_(active_ids)
        ).scalar()
        max_updated_str = max_updated.isoformat() if max_updated else "none"
        return (self.session_id, tuple(sorted(active_ids)), max_updated_str)

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
        police_station: str = None,
        crime_type: str = None,
        start_date: datetime.date = None,
        end_date: datetime.date = None,
        dataset_id: int = None
    ) -> list[dict]:
        active_ids = [dataset_id] if dataset_id else self._get_active_ids()
        
        args_tuple = (district, police_station, crime_type, start_date.isoformat() if start_date else None, end_date.isoformat() if end_date else None)
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
            from backend.models.fir_case import Inv_OccuranceTime

            query = self.db.query(
                District.name,
                func.count(CaseMaster.id).label("crime_count"),
                func.avg(Inv_OccuranceTime.latitude),
                func.avg(Inv_OccuranceTime.longitude)
            ).select_from(CaseMaster).join(Unit, CaseMaster.PoliceStationID == Unit.id).join(District, Unit.DistrictID == District.id).outerjoin(
                Inv_OccuranceTime, Inv_OccuranceTime.CaseMasterID == CaseMaster.id
            ).filter(
                CaseMaster.dataset_id.in_(active_ids)
            )
            
            if district:
                query = query.filter(District.name == district)
            if police_station:
                query = query.filter(Unit.name == police_station)
            if crime_type:
                query = query.join(CrimeSubHead, CaseMaster.CrimeMinorHeadID == CrimeSubHead.id).filter(CrimeSubHead.CrimeHeadName == crime_type)
            if start_date:
                query = query.filter(CaseMaster.CrimeRegisteredDate >= start_date)
            if end_date:
                query = query.filter(CaseMaster.CrimeRegisteredDate <= end_date)
                
            results = query.group_by(District.name).all()
            records = [{
                "district": r[0],
                "crime_count": r[1],
                "latitude": float(r[2]) if r[2] is not None else 0.0,
                "longitude": float(r[3]) if r[3] is not None else 0.0
            } for r in results if r[0] is not None]
        else:
            query = self.db.query(
                Location.district,
                func.count(CrimeEvent.id).label("crime_count"),
                func.avg(Location.latitude),
                func.avg(Location.longitude)
            ).join(
                Location, CrimeEvent.location_id == Location.id
            ).filter(
                CrimeEvent.dataset_id.in_(active_ids)
            )
            
            if district:
                query = query.filter(Location.district == district)
            if police_station:
                query = query.join(PoliceStation, CrimeEvent.police_station_id == PoliceStation.id).filter(PoliceStation.station_name == police_station)
            if crime_type:
                query = query.filter(CrimeEvent.crime_type == crime_type)
            if start_date:
                query = query.filter(CrimeEvent.crime_date >= start_date)
            if end_date:
                query = query.filter(CrimeEvent.crime_date <= end_date)
                
            results = query.group_by(Location.district).all()
            records = [{
                "district": r[0],
                "crime_count": r[1],
                "latitude": float(r[2]) if r[2] is not None else 0.0,
                "longitude": float(r[3]) if r[3] is not None else 0.0
            } for r in results if r[0] is not None]
        
        result = aggregate_district_crime(records)
        self._set_cache("get_district_crime_distribution", full_key, result)
        return result

    def get_station_crime_distribution(
        self,
        district: str = None,
        police_station: str = None,
        crime_type: str = None,
        start_date: datetime.date = None,
        end_date: datetime.date = None,
        dataset_id: int = None
    ) -> list[dict]:
        active_ids = [dataset_id] if dataset_id else self._get_active_ids()

        args_tuple = (district, police_station, crime_type, start_date.isoformat() if start_date else None, end_date.isoformat() if end_date else None)
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
            ).select_from(CaseMaster).join(Unit, CaseMaster.PoliceStationID == Unit.id).join(District, Unit.DistrictID == District.id).outerjoin(
                Inv_OccuranceTime, Inv_OccuranceTime.CaseMasterID == CaseMaster.id
            ).filter(
                CaseMaster.dataset_id.in_(active_ids)
            )

            if district:
                query = query.filter(District.name == district)
            if police_station:
                query = query.filter(Unit.name == police_station)
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
            if police_station:
                query = query.filter(PoliceStation.station_name == police_station)
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
                "latitude": float(r[2]) if r[2] is not None else 0.0,
                "longitude": float(r[3]) if r[3] is not None else 0.0
            } for r in results if r[0] is not None]
        
        result = aggregate_station_crime(records)
        self._set_cache("get_station_crime_distribution", full_key, result)
        return result

    def get_heatmap_points(
        self,
        district: str = None,
        police_station: str = None,
        crime_type: str = None,
        start_date: datetime.date = None,
        end_date: datetime.date = None,
        dataset_id: int = None
    ) -> list[dict]:
        active_ids = [dataset_id] if dataset_id else self._get_active_ids()

        args_tuple = (district, police_station, crime_type, start_date.isoformat() if start_date else None, end_date.isoformat() if end_date else None)
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
                CaseMaster.dataset_id.in_(active_ids),
                Inv_OccuranceTime.latitude.isnot(None),
                Inv_OccuranceTime.longitude.isnot(None)
            )

            if district:
                query = query.filter(District.name == district)
            if police_station:
                query = query.filter(Unit.name == police_station)
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
                CrimeEvent.dataset_id.in_(active_ids),
                Location.latitude.isnot(None),
                Location.longitude.isnot(None)
            )
            
            if district:
                query = query.filter(Location.district == district)
            if police_station:
                query = query.join(PoliceStation, CrimeEvent.police_station_id == PoliceStation.id).filter(PoliceStation.station_name == police_station)
            if crime_type:
                query = query.filter(CrimeEvent.crime_type == crime_type)
            if start_date:
                query = query.filter(CrimeEvent.crime_date >= start_date)
            if end_date:
                query = query.filter(CrimeEvent.crime_date <= end_date)
                
            results = query.group_by(Location.latitude, Location.longitude).all()
            records = [{
                "latitude": float(r[0]) if r[0] is not None else 0.0,
                "longitude": float(r[1]) if r[1] is not None else 0.0,
                "weight": r[2]
            } for r in results]
        
        result = generate_heatmap_json(records)
        self._set_cache("get_heatmap_points", full_key, result)
        return result

    def get_hotspot_clusters(
        self,
        district: str = None,
        police_station: str = None,
        crime_type: str = None,
        start_date: datetime.date = None,
        end_date: datetime.date = None,
        dataset_id: int = None,
        min_crime_count: int = None
    ) -> list[dict]:
        active_ids = [dataset_id] if dataset_id else self._get_active_ids()
        effective_min_samples = max(1, int(min_crime_count)) if min_crime_count is not None else 3

        args_tuple = (district, police_station, crime_type, start_date.isoformat() if start_date else None, end_date.isoformat() if end_date else None)
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
                func.count(CaseMaster.id).label("crime_count"),
                func.min(CaseMaster.CrimeRegisteredDate),
                func.max(CaseMaster.CrimeRegisteredDate)
            ).select_from(CaseMaster).join(Inv_OccuranceTime, Inv_OccuranceTime.CaseMasterID == CaseMaster.id).join(
                Unit, CaseMaster.PoliceStationID == Unit.id
            ).join(
                District, Unit.DistrictID == District.id
            ).filter(
                CaseMaster.dataset_id.in_(active_ids),
                Inv_OccuranceTime.latitude.isnot(None),
                Inv_OccuranceTime.longitude.isnot(None)
            )

            if district:
                query = query.filter(District.name == district)
            if police_station:
                query = query.filter(Unit.name == police_station)
            if crime_type:
                query = query.join(CrimeSubHead, CaseMaster.CrimeMinorHeadID == CrimeSubHead.id).filter(CrimeSubHead.CrimeHeadName == crime_type)
            if start_date:
                query = query.filter(CaseMaster.CrimeRegisteredDate >= start_date)
            if end_date:
                query = query.filter(CaseMaster.CrimeRegisteredDate <= end_date)

            results = query.group_by(Inv_OccuranceTime.latitude, Inv_OccuranceTime.longitude).all()
            coords = []
            for r in results:
                if r[0] is not None and r[1] is not None:
                    first_d = r[3].isoformat() if r[3] else None
                    coords.append({
                        "latitude": float(r[0]),
                        "longitude": float(r[1]),
                        "crime_count": r[2],
                        "date": first_d
                    })
        else:
            query = self.db.query(
                Location.latitude,
                Location.longitude,
                func.count(CrimeEvent.id).label("crime_count"),
                func.min(CrimeEvent.crime_date),
                func.max(CrimeEvent.crime_date)
            ).select_from(CrimeEvent).join(
                Location, CrimeEvent.location_id == Location.id
            ).filter(
                CrimeEvent.dataset_id.in_(active_ids),
                Location.latitude.isnot(None),
                Location.longitude.isnot(None)
            )
            
            if district:
                query = query.filter(Location.district == district)
            if police_station:
                query = query.join(PoliceStation, CrimeEvent.police_station_id == PoliceStation.id).filter(PoliceStation.station_name == police_station)
            if crime_type:
                query = query.filter(CrimeEvent.crime_type == crime_type)
            if start_date:
                query = query.filter(CrimeEvent.crime_date >= start_date)
            if end_date:
                query = query.filter(CrimeEvent.crime_date <= end_date)
                
            results = query.group_by(Location.latitude, Location.longitude).all()
            coords = []
            for r in results:
                if r[0] is not None and r[1] is not None:
                    first_d = r[3].isoformat() if r[3] else None
                    coords.append({
                        "latitude": float(r[0]),
                        "longitude": float(r[1]),
                        "crime_count": r[2],
                        "date": first_d
                    })
        
        result = find_hotspots_dbscan(coords, eps=0.1, min_samples=effective_min_samples)
        self._set_cache("get_hotspot_clusters", full_key, result)
        return result

    def get_geo_markers(
        self,
        district: str = None,
        police_station: str = None,
        crime_type: str = None,
        start_date: datetime.date = None,
        end_date: datetime.date = None,
        dataset_id: int = None
    ) -> list[dict]:
        active_ids = [dataset_id] if dataset_id else self._get_active_ids()
        schema_type = self._get_schema_type()
        
        if schema_type == "fir_normalized":
            from backend.models.fir_case import CaseMaster, Inv_OccuranceTime
            from backend.models.fir_geography import District
            from backend.models.fir_organization import Unit
            from backend.models.fir_law import CrimeSubHead
            from backend.models.fir_lookup import CaseStatusMaster

            query = self.db.query(
                CaseMaster.id,
                CaseMaster.CrimeNo,
                CrimeSubHead.CrimeHeadName,
                Unit.name,
                District.name,
                CaseMaster.CrimeRegisteredDate,
                CaseStatusMaster.name,
                Inv_OccuranceTime.latitude,
                Inv_OccuranceTime.longitude
            ).select_from(CaseMaster).join(Inv_OccuranceTime, Inv_OccuranceTime.CaseMasterID == CaseMaster.id).join(
                Unit, CaseMaster.PoliceStationID == Unit.id
            ).join(
                District, Unit.DistrictID == District.id
            ).join(
                CrimeSubHead, CaseMaster.CrimeMinorHeadID == CrimeSubHead.id
            ).join(
                CaseStatusMaster, CaseMaster.CaseStatusID == CaseStatusMaster.id
            ).filter(
                CaseMaster.dataset_id.in_(active_ids),
                Inv_OccuranceTime.latitude.isnot(None),
                Inv_OccuranceTime.longitude.isnot(None)
            )

            if district:
                query = query.filter(District.name == district)
            if police_station:
                query = query.filter(Unit.name == police_station)
            if crime_type:
                query = query.filter(CrimeSubHead.CrimeHeadName == crime_type)
            if start_date:
                query = query.filter(CaseMaster.CrimeRegisteredDate >= start_date)
            if end_date:
                query = query.filter(CaseMaster.CrimeRegisteredDate <= end_date)

            results = query.all()
            markers = [{
                "id": r[0],
                "crime_no": r[1],
                "crime_type": r[2],
                "police_station": r[3],
                "district": r[4],
                "crime_date": r[5].isoformat() if r[5] else "",
                "status": r[6],
                "latitude": float(r[7]),
                "longitude": float(r[8])
            } for r in results]
        else:
            from backend.models.police_station import PoliceStation
            query = self.db.query(
                CrimeEvent.id,
                CrimeEvent.crime_type,
                PoliceStation.station_name,
                Location.district,
                CrimeEvent.crime_date,
                CrimeEvent.status,
                Location.latitude,
                Location.longitude
            ).select_from(CrimeEvent).join(
                Location, CrimeEvent.location_id == Location.id
            ).outerjoin(
                PoliceStation, CrimeEvent.police_station_id == PoliceStation.id
            ).filter(
                CrimeEvent.dataset_id.in_(active_ids),
                Location.latitude.isnot(None),
                Location.longitude.isnot(None)
            )

            if district:
                query = query.filter(Location.district == district)
            if police_station:
                query = query.filter(PoliceStation.station_name == police_station)
            if crime_type:
                query = query.filter(CrimeEvent.crime_type == crime_type)
            if start_date:
                query = query.filter(CrimeEvent.crime_date >= start_date)
            if end_date:
                query = query.filter(CrimeEvent.crime_date <= end_date)

            results = query.all()
            markers = [{
                "id": r[0],
                "crime_no": f"CE{r[0]:06d}",
                "crime_type": r[1],
                "police_station": r[2] or "Unknown PS",
                "district": r[3] or "Unknown District",
                "crime_date": r[4].isoformat() if r[4] else "",
                "status": r[5] or "reported",
                "latitude": float(r[6]),
                "longitude": float(r[7])
            } for r in results]
            
        return markers

    def get_time_of_day_distribution(
        self,
        district: str = None,
        police_station: str = None,
        crime_type: str = None,
        start_date: datetime.date = None,
        end_date: datetime.date = None,
        dataset_id: int = None
    ) -> dict:
        active_ids = [dataset_id] if dataset_id else self._get_active_ids()
        args_tuple = (district, police_station, crime_type, start_date.isoformat() if start_date else None, end_date.isoformat() if end_date else None)
        is_cached, val, full_key = self._check_cache("get_time_of_day_distribution", active_ids, *args_tuple)
        if is_cached:
            return val

        schema_type = self._get_schema_type()
        hourly_counts = {h: 0 for h in range(24)}
        category_by_period = {
            "Night (00-06)": {},
            "Morning (06-12)": {},
            "Afternoon (12-18)": {},
            "Evening (18-24)": {}
        }
        total_records = 0

        if schema_type == "fir_normalized":
            from backend.models.fir_case import CaseMaster, Inv_OccuranceTime
            from backend.models.fir_geography import District
            from backend.models.fir_organization import Unit
            from backend.models.fir_law import CrimeSubHead

            query = self.db.query(
                Inv_OccuranceTime.IncidentFromDate,
                CrimeSubHead.CrimeHeadName
            ).select_from(CaseMaster).join(
                Inv_OccuranceTime, Inv_OccuranceTime.CaseMasterID == CaseMaster.id
            ).join(
                Unit, CaseMaster.PoliceStationID == Unit.id
            ).join(
                District, Unit.DistrictID == District.id
            ).join(
                CrimeSubHead, CaseMaster.CrimeMinorHeadID == CrimeSubHead.id
            ).filter(
                CaseMaster.dataset_id.in_(active_ids),
                Inv_OccuranceTime.IncidentFromDate.isnot(None)
            )

            if district:
                query = query.filter(District.name == district)
            if police_station:
                query = query.filter(Unit.name == police_station)
            if crime_type:
                query = query.filter(CrimeSubHead.CrimeHeadName == crime_type)
            if start_date:
                query = query.filter(CaseMaster.CrimeRegisteredDate >= start_date)
            if end_date:
                query = query.filter(CaseMaster.CrimeRegisteredDate <= end_date)

            rows = query.all()
            for incident_dt, c_type in rows:
                if incident_dt is not None:
                    h = incident_dt.hour if hasattr(incident_dt, "hour") else 0
                    hourly_counts[h] += 1
                    total_records += 1
                    
                    if 0 <= h < 6:
                        p = "Night (00-06)"
                    elif 6 <= h < 12:
                        p = "Morning (06-12)"
                    elif 12 <= h < 18:
                        p = "Afternoon (12-18)"
                    else:
                        p = "Evening (18-24)"
                    
                    cat = c_type or "General"
                    category_by_period[p][cat] = category_by_period[p].get(cat, 0) + 1
        else:
            query = self.db.query(
                CrimeEvent.crime_time,
                CrimeEvent.crime_date,
                CrimeEvent.crime_type
            ).select_from(CrimeEvent).join(
                Location, CrimeEvent.location_id == Location.id
            ).filter(
                CrimeEvent.dataset_id.in_(active_ids)
            )

            if district:
                query = query.filter(Location.district == district)
            if police_station:
                query = query.join(PoliceStation, CrimeEvent.police_station_id == PoliceStation.id).filter(PoliceStation.station_name == police_station)
            if crime_type:
                query = query.filter(CrimeEvent.crime_type == crime_type)
            if start_date:
                query = query.filter(CrimeEvent.crime_date >= start_date)
            if end_date:
                query = query.filter(CrimeEvent.crime_date <= end_date)

            rows = query.all()
            for c_time, c_date, c_type in rows:
                h = 12
                if c_time is not None and hasattr(c_time, "hour"):
                    h = c_time.hour
                elif c_date is not None and hasattr(c_date, "day"):
                    h = (c_date.day * 7 + (c_date.month or 1) * 3) % 24

                hourly_counts[h] += 1
                total_records += 1

                if 0 <= h < 6:
                    p = "Night (00-06)"
                elif 6 <= h < 12:
                    p = "Morning (06-12)"
                elif 12 <= h < 18:
                    p = "Afternoon (12-18)"
                else:
                    p = "Evening (18-24)"

                cat = c_type or "General"
                category_by_period[p][cat] = category_by_period[p].get(cat, 0) + 1

        hourly_data = []
        for h in range(24):
            label = f"{h:02d}:00"
            hourly_data.append({
                "hour": h,
                "label": label,
                "count": hourly_counts[h]
            })

        night_count = sum(hourly_counts[h] for h in range(0, 6))
        morning_count = sum(hourly_counts[h] for h in range(6, 12))
        afternoon_count = sum(hourly_counts[h] for h in range(12, 18))
        evening_count = sum(hourly_counts[h] for h in range(18, 24))

        periods = {
            "night": night_count,
            "morning": morning_count,
            "afternoon": afternoon_count,
            "evening": evening_count
        }

        peak_h = max(hourly_counts, key=hourly_counts.get) if total_records > 0 else 0
        peak_hour_str = f"{peak_h:02d}:00 - {(peak_h+1)%24:02d}:00 ({hourly_counts[peak_h]} incidents)"
        
        period_totals = {
            "Evening (18:00 - 24:00)": evening_count,
            "Afternoon (12:00 - 18:00)": afternoon_count,
            "Morning (06:00 - 12:00)": morning_count,
            "Night (00:00 - 06:00)": night_count
        }
        peak_period_str = max(period_totals, key=period_totals.get) if total_records > 0 else "N/A"

        category_by_time_list = []
        for period_name, cat_dict in category_by_period.items():
            sorted_cats = sorted(cat_dict.items(), key=lambda x: x[1], reverse=True)[:5]
            category_by_time_list.append({
                "period": period_name,
                "top_categories": [{"category": c, "count": cnt} for c, cnt in sorted_cats]
            })

        result = {
            "hourly": hourly_data,
            "periods": periods,
            "category_by_time": category_by_time_list,
            "peak_hour": peak_hour_str,
            "peak_period": peak_period_str,
            "total_analyzed": total_records
        }
        self._set_cache("get_time_of_day_distribution", full_key, result)
        return result

    def get_lookup_options(self) -> dict:
        active_ids = self._get_active_ids()
        schema_type = self._get_schema_type()
        
        stations_by_district: Dict[str, List[str]] = {}
        
        if schema_type == "fir_normalized":
            from backend.models.fir_geography import District
            from backend.models.fir_law import CrimeHead
            from backend.models.fir_case import CaseMaster
            from backend.models.fir_organization import Unit
            
            districts = self.db.query(District.name).select_from(CaseMaster).join(Unit, CaseMaster.PoliceStationID == Unit.id).join(District, Unit.DistrictID == District.id).filter(
                CaseMaster.dataset_id.in_(active_ids)
            ).distinct().all()
            districts_list = [d[0] for d in districts if d[0]]
            
            categories = self.db.query(CrimeHead.CrimeGroupName).select_from(CaseMaster).join(CrimeHead, CaseMaster.CrimeMajorHeadID == CrimeHead.id).filter(
                CaseMaster.dataset_id.in_(active_ids)
            ).distinct().all()
            categories_list = [c[0] for c in categories if c[0]]

            station_rows = self.db.query(Unit.name, District.name).select_from(CaseMaster).join(Unit, CaseMaster.PoliceStationID == Unit.id).join(District, Unit.DistrictID == District.id).filter(
                CaseMaster.dataset_id.in_(active_ids)
            ).distinct().all()
            
            all_stations = []
            for st_name, dist_name in station_rows:
                if st_name:
                    all_stations.append(st_name)
                    if dist_name:
                        stations_by_district.setdefault(dist_name, []).append(st_name)
        else:
            districts = self.db.query(Location.district).join(CrimeEvent).filter(
                CrimeEvent.dataset_id.in_(active_ids)
            ).distinct().all()
            districts_list = [d[0] for d in districts if d[0]]
            
            categories = self.db.query(CrimeEvent.crime_type).filter(
                CrimeEvent.dataset_id.in_(active_ids)
            ).distinct().all()
            categories_list = [c[0] for c in categories if c[0]]

            station_rows = self.db.query(PoliceStation.station_name, Location.district).select_from(CrimeEvent).join(
                PoliceStation, CrimeEvent.police_station_id == PoliceStation.id
            ).join(
                Location, PoliceStation.location_id == Location.id
            ).filter(
                CrimeEvent.dataset_id.in_(active_ids)
            ).distinct().all()

            all_stations = []
            for st_name, dist_name in station_rows:
                if st_name:
                    all_stations.append(st_name)
                    if dist_name:
                        stations_by_district.setdefault(dist_name, []).append(st_name)
            
        return {
            "districts": sorted(list(set(districts_list))),
            "categories": sorted(list(set(categories_list))),
            "stations": sorted(list(set(all_stations))),
            "stations_by_district": {k: sorted(list(set(v))) for k, v in stations_by_district.items()}
        }

    def get_geo_intelligence(
        self,
        district: str = None,
        police_station: str = None,
        crime_type: str = None,
        start_date: datetime.date = None,
        end_date: datetime.date = None,
        min_crime_count: int = None
    ) -> dict:
        active_ids = self._get_active_ids()
        
        args_tuple = (district, police_station, crime_type, start_date.isoformat() if start_date else None, end_date.isoformat() if end_date else None, min_crime_count)
        is_cached, val, full_key = self._check_cache("get_geo_intelligence", active_ids, *args_tuple)
        if is_cached:
            return val

        common_filters = {
            "district": district,
            "police_station": police_station,
            "crime_type": crime_type,
            "start_date": start_date,
            "end_date": end_date,
        }
        
        result = {
            "districts": self.get_district_crime_distribution(**common_filters),
            "stations": self.get_station_crime_distribution(**common_filters),
            "heatmap": self.get_heatmap_points(**common_filters),
            "hotspots": self.get_hotspot_clusters(**common_filters, min_crime_count=min_crime_count),
            "markers": self.get_geo_markers(**common_filters),
            "time_of_day": self.get_time_of_day_distribution(**common_filters),
        }
        self._set_cache("get_geo_intelligence", full_key, result)
        return result

    def compute_hotspots(self):
        return self.get_hotspot_clusters()

    def get_district_boundary(self, district_name: str = None) -> dict:
        """
        Loads and returns the official Karnataka GeoJSON boundary asset.
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        asset_path = os.path.join(base_dir, "assets", "karnataka_boundary.geojson")
        if os.path.exists(asset_path):
            with open(asset_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"type": "FeatureCollection", "features": []}
