from datetime import date, timedelta
from typing import Any, List, Dict, Optional
import numpy as np
from sqlalchemy import func, case
from sqlalchemy.orm import Session
from backend.models.crime import CrimeEvent
from backend.models.criminal import Criminal
from backend.models.location import Location

class AnalyticsService:
    def __init__(self, db: Session, session_id: Optional[str] = None):
        self.db = db
        self.session_id = session_id

    def _get_active_id(self) -> int:
        from backend.core.dataset_resolver import DatasetResolver
        return DatasetResolver(self.db, self.session_id).get_active_dataset_id()

    def _get_active_ids(self) -> list[int]:
        from backend.core.dataset_resolver import DatasetResolver
        active_ids = DatasetResolver(self.db, self.session_id).get_active_dataset_ids()
        from backend.models.dataset import Dataset
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
        from sqlalchemy import func
        max_updated = self.db.query(func.max(Dataset.updated_at)).filter(
            Dataset.id.in_(active_ids)
        ).scalar()
        max_updated_str = max_updated.isoformat() if max_updated else "none"
        return (self.session_id, tuple(sorted(active_ids)), max_updated_str)

    def _check_cache(self, method_name: str, active_ids: list[int], *args, **kwargs) -> tuple[bool, Any, tuple]:
        from backend.core.analytics_cache import AnalyticsCache
        cache_key = self._get_cache_key(active_ids)
        full_key = (cache_key, args, tuple(sorted(kwargs.items())))
        cached_val = AnalyticsCache.get(method_name, full_key, session_id=self.session_id)
        if cached_val is not None:
            return True, cached_val, full_key
        return False, None, full_key

    def _set_cache(self, method_name: str, full_key: tuple, value: Any):
        from backend.core.analytics_cache import AnalyticsCache
        AnalyticsCache.set(method_name, full_key, value, session_id=self.session_id)

    def get_dashboard_summary(self) -> dict:
        active_ids = self._get_active_ids()
        is_cached, val, full_key = self._check_cache("get_dashboard_summary", active_ids)
        if is_cached:
            return val

        schema_type = self._get_schema_type()
        if schema_type == "fir_normalized":
            from backend.models.fir_case import CaseMaster
            from backend.models.fir_people import FIRVictim, Accused
            from backend.models.fir_lookup import CaseStatusMaster, GravityOffence
            from backend.models.fir_geography import District
            from backend.models.fir_organization import Unit
            from backend.models.crime import CLOSED_CASE_STATUSES, ACTIVE_CASE_STATUSES
            from backend.core.severity import GRAVITY_SEVERITY_MAP, DEFAULT_SEVERITY

            total_crimes = self.db.query(func.count(CaseMaster.id)).filter(CaseMaster.dataset_id.in_(active_ids)).scalar() or 0
            total_victims = self.db.query(func.count(FIRVictim.id)).join(CaseMaster).filter(CaseMaster.dataset_id.in_(active_ids)).scalar() or 0
            total_accused = self.db.query(func.count(Accused.id)).join(CaseMaster).filter(CaseMaster.dataset_id.in_(active_ids)).scalar() or 0

            closed_cases = self.db.query(func.count(CaseMaster.id)).join(CaseStatusMaster).filter(
                CaseMaster.dataset_id.in_(active_ids),
                CaseStatusMaster.name.in_(CLOSED_CASE_STATUSES)
            ).scalar() or 0

            active_cases = self.db.query(func.count(CaseMaster.id)).join(CaseStatusMaster).filter(
                CaseMaster.dataset_id.in_(active_ids),
                CaseStatusMaster.name.in_(ACTIVE_CASE_STATUSES)
            ).scalar() or 0

            # Calculate average severity using case expression on GravityOffence
            sev_whens = [((GravityOffence.name == name), score) for name, score in GRAVITY_SEVERITY_MAP.items()]
            sev_stats = self.db.query(
                func.avg(case(*sev_whens, else_=DEFAULT_SEVERITY))
            ).select_from(CaseMaster).join(GravityOffence).filter(CaseMaster.dataset_id.in_(active_ids)).scalar()
            average_severity = float(sev_stats) if sev_stats is not None else 0.0

            districts_count = self.db.query(Unit.DistrictID).join(CaseMaster, CaseMaster.PoliceStationID == Unit.id).filter(
                CaseMaster.dataset_id.in_(active_ids)
            ).distinct().count()

            stations_count = self.db.query(CaseMaster.PoliceStationID).filter(
                CaseMaster.dataset_id.in_(active_ids),
                CaseMaster.PoliceStationID.isnot(None)
            ).distinct().count()

            total_criminals = total_accused
            from backend.models.fir_lookup import GravityOffence
            high_risk_criminals = self.db.query(func.count(Accused.id)).join(CaseMaster).join(GravityOffence).filter(
                CaseMaster.dataset_id.in_(active_ids),
                GravityOffence.name == "Heinous"
            ).scalar() or 0
            crime_resolution_rate = (closed_cases / total_crimes * 100.0) if total_crimes > 0 else 0.0
        else:
            from backend.models.crime import CLOSED_CASE_STATUSES, ACTIVE_CASE_STATUSES
            from backend.models.location import Location
            
            # 1. Combined single-pass query on CrimeEvent
            stats = self.db.query(
                func.count(CrimeEvent.id),
                func.coalesce(func.sum(CrimeEvent.victim_count), 0),
                func.coalesce(func.sum(CrimeEvent.accused_count), 0),
                func.sum(case((CrimeEvent.status.in_(CLOSED_CASE_STATUSES), 1), else_=0)),
                func.sum(case((CrimeEvent.status.in_(ACTIVE_CASE_STATUSES), 1), else_=0)),
                func.coalesce(func.avg(CrimeEvent.severity), 0.0)
            ).filter(CrimeEvent.dataset_id.in_(active_ids)).first()
            
            total_crimes = stats[0] or 0
            total_victims = stats[1] or 0
            total_accused = stats[2] or 0
            closed_cases = stats[3] or 0
            active_cases = stats[4] or 0
            average_severity = float(stats[5]) if stats[5] is not None else 0.0
            
            # 2. Query covered districts & stations count
            districts_count = self.db.query(Location.district).join(CrimeEvent).filter(
                CrimeEvent.dataset_id.in_(active_ids)
            ).distinct().count()
            
            stations_count = self.db.query(CrimeEvent.police_station_id).filter(
                CrimeEvent.dataset_id.in_(active_ids),
                CrimeEvent.police_station_id.isnot(None)
            ).distinct().count()
            
            # 3. Query criminal stats
            criminals_stats = self.db.query(
                func.count(Criminal.id),
                func.sum(case((Criminal.risk_score >= 7.0, 1), else_=0))
            ).filter(Criminal.dataset_id.in_(active_ids)).first()
            
            total_criminals = criminals_stats[0] or 0
            high_risk_criminals = criminals_stats[1] or 0
            crime_resolution_rate = (closed_cases / total_crimes * 100.0) if total_crimes > 0 else 0.0

        result = {
            "total_crimes": total_crimes,
            "total_victims": total_victims,
            "total_accused": total_accused,
            "active_cases": active_cases,
            "high_risk_criminals": high_risk_criminals,
            "total_criminals": total_criminals,
            "crime_resolution_rate": round(crime_resolution_rate, 2),
            "average_severity": round(average_severity, 2),
            "districts_count": districts_count,
            "stations_count": stations_count
        }
        self._set_cache("get_dashboard_summary", full_key, result)
        return result

    def get_crime_trend(self, days: int = 30) -> list[dict]:
        active_ids = self._get_active_ids()
        is_cached, val, full_key = self._check_cache("get_crime_trend", active_ids, days)
        if is_cached:
            return val

        schema_type = self._get_schema_type()
        if schema_type == "fir_normalized":
            from backend.models.fir_case import CaseMaster
            max_date = self.db.query(func.max(CaseMaster.CrimeRegisteredDate)).filter(CaseMaster.dataset_id.in_(active_ids)).scalar()
            anchor_date = max_date if max_date is not None else date.today()
            start_date = anchor_date - timedelta(days=days)
            results = self.db.query(
                CaseMaster.CrimeRegisteredDate,
                func.count(CaseMaster.id)
            ).filter(
                CaseMaster.dataset_id.in_(active_ids),
                CaseMaster.CrimeRegisteredDate >= start_date
            ).group_by(
                CaseMaster.CrimeRegisteredDate
            ).order_by(
                CaseMaster.CrimeRegisteredDate.asc()
            ).all()
        else:
            max_date = self.db.query(func.max(CrimeEvent.crime_date)).filter(CrimeEvent.dataset_id.in_(active_ids)).scalar()
            anchor_date = max_date if max_date is not None else date.today()
            start_date = anchor_date - timedelta(days=days)
            results = self.db.query(
                CrimeEvent.crime_date,
                func.count(CrimeEvent.id)
            ).filter(
                CrimeEvent.dataset_id.in_(active_ids),
                CrimeEvent.crime_date >= start_date
            ).group_by(
                CrimeEvent.crime_date
            ).order_by(
                CrimeEvent.crime_date.asc()
            ).all()

        result = [{"date": r[0].isoformat(), "count": r[1]} for r in results if r[0] is not None]
        self._set_cache("get_crime_trend", full_key, result)
        return result

    def get_category_breakdown(self) -> list[dict]:
        active_ids = self._get_active_ids()
        is_cached, val, full_key = self._check_cache("get_category_breakdown", active_ids)
        if is_cached:
            return val

        schema_type = self._get_schema_type()
        if schema_type == "fir_normalized":
            from backend.models.fir_case import CaseMaster
            from backend.models.fir_law import CrimeHead
            results = self.db.query(
                CrimeHead.CrimeGroupName,
                func.count(CaseMaster.id)
            ).join(CrimeHead, CaseMaster.CrimeMajorHeadID == CrimeHead.id).filter(
                CaseMaster.dataset_id.in_(active_ids)
            ).group_by(
                CrimeHead.CrimeGroupName
            ).order_by(
                func.count(CaseMaster.id).desc()
            ).limit(9).all()
        else:
            results = self.db.query(
                CrimeEvent.crime_category,
                func.count(CrimeEvent.id)
            ).filter(
                CrimeEvent.dataset_id.in_(active_ids)
            ).group_by(
                CrimeEvent.crime_category
            ).order_by(
                func.count(CrimeEvent.id).desc()
            ).limit(9).all()

        result = [{"category": r[0], "count": r[1]} for r in results if r[0] is not None]
        self._set_cache("get_category_breakdown", full_key, result)
        return result

    def get_district_ranking(self) -> list[dict]:
        active_ids = self._get_active_ids()
        is_cached, val, full_key = self._check_cache("get_district_ranking", active_ids)
        if is_cached:
            return val

        schema_type = self._get_schema_type()
        if schema_type == "fir_normalized":
            from backend.models.fir_case import CaseMaster
            from backend.models.fir_geography import District
            from backend.models.fir_organization import Unit
            results = self.db.query(
                District.name,
                func.count(CaseMaster.id)
            ).select_from(CaseMaster).join(Unit, CaseMaster.PoliceStationID == Unit.id).join(District, Unit.DistrictID == District.id).filter(
                CaseMaster.dataset_id.in_(active_ids)
            ).group_by(
                District.name
            ).order_by(
                func.count(CaseMaster.id).desc()
            ).limit(10).all()
        else:
            results = self.db.query(
                Location.district,
                func.count(CrimeEvent.id)
            ).join(
                Location,
                CrimeEvent.location_id == Location.id
            ).filter(
                CrimeEvent.dataset_id.in_(active_ids)
            ).group_by(
                Location.district
            ).order_by(
                func.count(CrimeEvent.id).desc()
            ).limit(10).all()

        result = [{"district": r[0], "count": r[1]} for r in results if r[0] is not None]
        self._set_cache("get_district_ranking", full_key, result)
        return result

    def get_recent_crimes(self, limit: int = 10) -> list[dict]:
        active_ids = self._get_active_ids()
        is_cached, val, full_key = self._check_cache("get_recent_crimes", active_ids, limit)
        if is_cached:
            return val

        schema_type = self._get_schema_type()
        recent_crimes = []

        if schema_type == "fir_normalized":
            from backend.models.fir_case import CaseMaster
            from backend.models.fir_geography import District
            from backend.models.fir_organization import Unit
            from backend.models.fir_law import CrimeHead, CrimeSubHead
            from backend.models.fir_lookup import CaseStatusMaster, GravityOffence
            from backend.models.fir_people import FIRVictim, Accused
            from backend.core.severity import resolve_gravity_severity

            results = self.db.query(
                CaseMaster,
                District.name,
                CrimeHead.CrimeGroupName,
                CrimeSubHead.CrimeHeadName,
                CaseStatusMaster.name,
                GravityOffence.name
            ).select_from(CaseMaster).join(Unit, CaseMaster.PoliceStationID == Unit.id).join(District, Unit.DistrictID == District.id).join(
                CrimeHead, CaseMaster.CrimeMajorHeadID == CrimeHead.id
            ).join(
                CrimeSubHead, CaseMaster.CrimeMinorHeadID == CrimeSubHead.id
            ).join(
                CaseStatusMaster, CaseMaster.CaseStatusID == CaseStatusMaster.id
            ).join(
                GravityOffence, CaseMaster.GravityOffenceID == GravityOffence.id
            ).filter(
                CaseMaster.dataset_id.in_(active_ids)
            ).order_by(
                CaseMaster.created_at.desc()
            ).limit(limit).all()

            for case, district_name, cat, minor, status, gravity in results:
                v_count = self.db.query(func.count(FIRVictim.id)).filter(FIRVictim.CaseMasterID == case.id).scalar() or 0
                a_count = self.db.query(func.count(Accused.id)).filter(Accused.CaseMasterID == case.id).scalar() or 0

                recent_crimes.append({
                    "id": case.id,
                    "crime_type": minor,
                    "crime_category": cat,
                    "district": district_name,
                    "severity": resolve_gravity_severity(gravity),
                    "status": status,
                    "crime_date": case.CrimeRegisteredDate.isoformat() if case.CrimeRegisteredDate else "",
                    "victim_count": v_count,
                    "accused_count": a_count
                })
        else:
            results = self.db.query(
                CrimeEvent,
                Location.district
            ).outerjoin(
                Location,
                CrimeEvent.location_id == Location.id
            ).filter(
                CrimeEvent.dataset_id.in_(active_ids)
            ).order_by(
                CrimeEvent.created_at.desc()
            ).limit(limit).all()

            for crime, district in results:
                recent_crimes.append({
                    "id": crime.id,
                    "crime_type": crime.crime_type,
                    "crime_category": crime.crime_category,
                    "district": district if district is not None else "Unknown",
                    "severity": crime.severity,
                    "status": crime.status,
                    "crime_date": crime.crime_date.isoformat() if crime.crime_date else "",
                    "victim_count": crime.victim_count,
                    "accused_count": crime.accused_count
                })

        self._set_cache("get_recent_crimes", full_key, recent_crimes)
        return recent_crimes

    def get_system_status(self) -> dict:
        active_ids = self._get_active_ids()
        is_cached, val, full_key = self._check_cache("get_system_status", active_ids)
        if is_cached:
            return val

        schema_type = self._get_schema_type()
        if schema_type == "fir_normalized":
            from backend.models.fir_case import CaseMaster
            total_records = self.db.query(CaseMaster).filter(CaseMaster.dataset_id.in_(active_ids)).count()
            if total_records == 0:
                result = {
                    "database_status": "online",
                    "total_records": 0,
                    "last_updated": "N/A",
                    "data_coverage_days": 0,
                }
                self._set_cache("get_system_status", full_key, result)
                return result

            max_created_at = self.db.query(func.max(CaseMaster.created_at)).filter(CaseMaster.dataset_id.in_(active_ids)).scalar()
            last_updated = max_created_at.isoformat() if max_created_at else "N/A"

            min_crime_date = self.db.query(func.min(CaseMaster.CrimeRegisteredDate)).filter(CaseMaster.dataset_id.in_(active_ids)).scalar()
            max_crime_date = self.db.query(func.max(CaseMaster.CrimeRegisteredDate)).filter(CaseMaster.dataset_id.in_(active_ids)).scalar()
        else:
            total_records = self.db.query(CrimeEvent).filter(CrimeEvent.dataset_id.in_(active_ids)).count()
            if total_records == 0:
                result = {
                    "database_status": "online",
                    "total_records": 0,
                    "last_updated": "N/A",
                    "data_coverage_days": 0,
                }
                self._set_cache("get_system_status", full_key, result)
                return result

            max_created_at = self.db.query(func.max(CrimeEvent.created_at)).filter(CrimeEvent.dataset_id.in_(active_ids)).scalar()
            last_updated = max_created_at.isoformat() if max_created_at else "N/A"

            min_crime_date = self.db.query(func.min(CrimeEvent.crime_date)).filter(CrimeEvent.dataset_id.in_(active_ids)).scalar()
            max_crime_date = self.db.query(func.max(CrimeEvent.crime_date)).filter(CrimeEvent.dataset_id.in_(active_ids)).scalar()

        if min_crime_date and max_crime_date:
            data_coverage_days = (max_crime_date - min_crime_date).days
        else:
            data_coverage_days = 0

        result = {
            "database_status": "online",
            "total_records": total_records,
            "last_updated": last_updated,
            "data_coverage_days": data_coverage_days,
        }
        self._set_cache("get_system_status", full_key, result)
        return result

    def get_overview_metrics(self) -> dict:
        active_ids = self._get_active_ids()
        is_cached, val, full_key = self._check_cache("get_overview_metrics", active_ids)
        if is_cached:
            return val

        schema_type = self._get_schema_type()
        if schema_type == "fir_normalized":
            from backend.models.fir_case import CaseMaster
            from backend.models.fir_people import FIRVictim, Accused
            total_crimes = self.db.query(func.count(CaseMaster.id)).filter(CaseMaster.dataset_id.in_(active_ids)).scalar() or 0
            total_victims = self.db.query(func.count(FIRVictim.id)).join(CaseMaster).filter(CaseMaster.dataset_id.in_(active_ids)).scalar() or 0
            total_accused = self.db.query(func.count(Accused.id)).join(CaseMaster).filter(CaseMaster.dataset_id.in_(active_ids)).scalar() or 0
        else:
            total_crimes = self.db.query(func.count(CrimeEvent.id)).filter(CrimeEvent.dataset_id.in_(active_ids)).scalar() or 0
            total_victims = self.db.query(func.coalesce(func.sum(CrimeEvent.victim_count), 0)).filter(CrimeEvent.dataset_id.in_(active_ids)).scalar() or 0
            total_accused = self.db.query(func.coalesce(func.sum(CrimeEvent.accused_count), 0)).filter(CrimeEvent.dataset_id.in_(active_ids)).scalar() or 0

        result = {
            "total_crimes": total_crimes,
            "total_victims": total_victims,
            "total_accused": total_accused
        }
        self._set_cache("get_overview_metrics", full_key, result)
        return result

    def get_daily_trends(self) -> list[dict]:
        active_ids = self._get_active_ids()
        is_cached, val, full_key = self._check_cache("get_daily_trends", active_ids)
        if is_cached:
            return val

        schema_type = self._get_schema_type()
        from analytics.temporal_analysis.daily import analyze_daily_trends

        if schema_type == "fir_normalized":
            from backend.models.fir_case import CaseMaster
            results = self.db.query(
                CaseMaster.CrimeRegisteredDate,
                func.count(CaseMaster.id)
            ).filter(
                CaseMaster.dataset_id.in_(active_ids),
                CaseMaster.CrimeRegisteredDate.isnot(None)
            ).group_by(
                CaseMaster.CrimeRegisteredDate
            ).order_by(
                CaseMaster.CrimeRegisteredDate.asc()
            ).all()
        else:
            results = self.db.query(
                CrimeEvent.crime_date,
                func.count(CrimeEvent.id)
            ).filter(
                CrimeEvent.dataset_id.in_(active_ids),
                CrimeEvent.crime_date.isnot(None)
            ).group_by(
                CrimeEvent.crime_date
            ).order_by(
                CrimeEvent.crime_date.asc()
            ).all()
        
        records = [{"period": r[0].isoformat() if hasattr(r[0], 'isoformat') else str(r[0]), "count": r[1]} for r in results]
        result = analyze_daily_trends(records)
        self._set_cache("get_daily_trends", full_key, result)
        return result

    def get_weekly_trends(self) -> list[dict]:
        active_ids = self._get_active_ids()
        is_cached, val, full_key = self._check_cache("get_weekly_trends", active_ids)
        if is_cached:
            return val

        schema_type = self._get_schema_type()
        from analytics.temporal_analysis.weekly import analyze_weekly_trends

        if schema_type == "fir_normalized":
            from backend.models.fir_case import CaseMaster
            date_col = CaseMaster.CrimeRegisteredDate
            model_class = CaseMaster
        else:
            date_col = CrimeEvent.crime_date
            model_class = CrimeEvent

        if self.db.bind.dialect.name == "postgresql":
            expr = func.date_trunc('week', date_col)
        else:
            expr = func.date(date_col, 'weekday 1', '-7 days')
            
        results = self.db.query(
            expr,
            func.count(model_class.id)
        ).filter(
            model_class.dataset_id.in_(active_ids),
            date_col.isnot(None)
        ).group_by(
            expr
        ).order_by(
            expr.asc()
        ).all()
        
        records = []
        for r in results:
            period_val = r[0]
            if hasattr(period_val, 'date'):
                period_str = period_val.date().isoformat()
            elif hasattr(period_val, 'isoformat'):
                period_str = period_val.isoformat()[:10]
            else:
                period_str = str(period_val)
            records.append({"period": period_str, "count": r[1]})
            
        result = analyze_weekly_trends(records)
        self._set_cache("get_weekly_trends", full_key, result)
        return result

    def get_monthly_trends(self) -> list[dict]:
        active_ids = self._get_active_ids()
        is_cached, val, full_key = self._check_cache("get_monthly_trends", active_ids)
        if is_cached:
            return val

        schema_type = self._get_schema_type()
        from analytics.temporal_analysis.monthly import analyze_monthly_trends

        if schema_type == "fir_normalized":
            from backend.models.fir_case import CaseMaster
            date_col = CaseMaster.CrimeRegisteredDate
            model_class = CaseMaster
        else:
            date_col = CrimeEvent.crime_date
            model_class = CrimeEvent

        if self.db.bind.dialect.name == "postgresql":
            expr = func.to_char(date_col, 'YYYY-MM')
        else:
            expr = func.strftime('%Y-%m', date_col)
            
        results = self.db.query(
            expr,
            func.count(model_class.id)
        ).filter(
            model_class.dataset_id.in_(active_ids),
            date_col.isnot(None)
        ).group_by(
            expr
        ).order_by(
            expr.asc()
        ).all()
        
        records = [{"period": str(r[0]), "count": r[1]} for r in results]
        result = analyze_monthly_trends(records)
        self._set_cache("get_monthly_trends", full_key, result)
        return result

    def get_yearly_trends(self) -> list[dict]:
        active_ids = self._get_active_ids()
        is_cached, val, full_key = self._check_cache("get_yearly_trends", active_ids)
        if is_cached:
            return val

        schema_type = self._get_schema_type()
        from analytics.temporal_analysis.yearly import analyze_yearly_trends

        if schema_type == "fir_normalized":
            from backend.models.fir_case import CaseMaster
            date_col = CaseMaster.CrimeRegisteredDate
            model_class = CaseMaster
        else:
            date_col = CrimeEvent.crime_date
            model_class = CrimeEvent

        if self.db.bind.dialect.name == "postgresql":
            expr = func.to_char(date_col, 'YYYY')
        else:
            expr = func.strftime('%Y', date_col)
            
        results = self.db.query(
            expr,
            func.count(model_class.id)
        ).filter(
            model_class.dataset_id.in_(active_ids),
            date_col.isnot(None)
        ).group_by(
            expr
        ).order_by(
            expr.asc()
        ).all()
        
        records = [{"period": str(r[0]), "count": r[1]} for r in results]
        result = analyze_yearly_trends(records)
        self._set_cache("get_yearly_trends", full_key, result)
        return result

    def get_category_distribution(self) -> list[dict]:
        active_ids = self._get_active_ids()
        is_cached, val, full_key = self._check_cache("get_category_distribution", active_ids)
        if is_cached:
            return val

        schema_type = self._get_schema_type()
        from analytics.crime_analysis.category_analysis import process_category_distribution

        if schema_type == "fir_normalized":
            from backend.models.fir_case import CaseMaster
            from backend.models.fir_law import CrimeHead
            results = self.db.query(
                CrimeHead.CrimeGroupName,
                func.count(CaseMaster.id)
            ).join(CrimeHead, CaseMaster.CrimeMajorHeadID == CrimeHead.id).filter(
                CaseMaster.dataset_id.in_(active_ids),
                CrimeHead.CrimeGroupName.isnot(None)
            ).group_by(
                CrimeHead.CrimeGroupName
            ).all()
        else:
            results = self.db.query(
                CrimeEvent.crime_category,
                func.count(CrimeEvent.id)
            ).filter(
                CrimeEvent.dataset_id.in_(active_ids),
                CrimeEvent.crime_category.isnot(None)
            ).group_by(
                CrimeEvent.crime_category
            ).all()
        
        records = [{"name": r[0], "count": r[1]} for r in results]
        result = process_category_distribution(records)
        self._set_cache("get_category_distribution", full_key, result)
        return result

    def get_subcategory_distribution(self) -> list[dict]:
        active_ids = self._get_active_ids()
        is_cached, val, full_key = self._check_cache("get_subcategory_distribution", active_ids)
        if is_cached:
            return val

        schema_type = self._get_schema_type()
        from analytics.crime_analysis.category_analysis import process_subcategory_distribution

        if schema_type == "fir_normalized":
            from backend.models.fir_case import CaseMaster
            from backend.models.fir_law import CrimeSubHead
            results = self.db.query(
                CrimeSubHead.CrimeHeadName,
                func.count(CaseMaster.id)
            ).join(CrimeSubHead, CaseMaster.CrimeMinorHeadID == CrimeSubHead.id).filter(
                CaseMaster.dataset_id.in_(active_ids),
                CrimeSubHead.CrimeHeadName.isnot(None)
            ).group_by(
                CrimeSubHead.CrimeHeadName
            ).all()
        else:
            results = self.db.query(
                CrimeEvent.crime_subcategory,
                func.count(CrimeEvent.id)
            ).filter(
                CrimeEvent.dataset_id.in_(active_ids),
                CrimeEvent.crime_subcategory.isnot(None)
            ).group_by(
                CrimeEvent.crime_subcategory
            ).all()
        
        records = [{"name": r[0], "count": r[1]} for r in results]
        result = process_subcategory_distribution(records)
        self._set_cache("get_subcategory_distribution", full_key, result)
        return result

    def get_historical_comparison(self) -> dict:
        active_ids = self._get_active_ids()
        is_cached, val, full_key = self._check_cache("get_historical_comparison", active_ids)
        if is_cached:
            return val

        from analytics.crime_analysis.trend_analysis import calculate_percentage_change
        
        today = date.today()
        
        current_month_start = date(today.year, today.month, 1)
        if today.month == 12:
            current_month_end = date(today.year + 1, 1, 1) - timedelta(days=1)
        else:
            current_month_end = date(today.year, today.month + 1, 1) - timedelta(days=1)
            
        if today.month == 1:
            previous_month_start = date(today.year - 1, 12, 1)
        else:
            previous_month_start = date(today.year, today.month - 1, 1)
        previous_month_end = current_month_start - timedelta(days=1)
        
        current_year_start = date(today.year, 1, 1)
        current_year_end = date(today.year, 12, 31)
        
        previous_year_start = date(today.year - 1, 1, 1)
        previous_year_end = date(today.year - 1, 12, 31)

        schema_type = self._get_schema_type()
        if schema_type == "fir_normalized":
            from backend.models.fir_case import CaseMaster
            model_class = CaseMaster
            date_col = CaseMaster.CrimeRegisteredDate
        else:
            model_class = CrimeEvent
            date_col = CrimeEvent.crime_date
        
        current_month_count = self.db.query(func.count(model_class.id)).filter(
            model_class.dataset_id.in_(active_ids),
            date_col >= current_month_start,
            date_col <= current_month_end
        ).scalar() or 0
        
        previous_month_count = self.db.query(func.count(model_class.id)).filter(
            model_class.dataset_id.in_(active_ids),
            date_col >= previous_month_start,
            date_col <= previous_month_end
        ).scalar() or 0
        
        current_year_count = self.db.query(func.count(model_class.id)).filter(
            model_class.dataset_id.in_(active_ids),
            date_col >= current_year_start,
            date_col <= current_year_end
        ).scalar() or 0
        
        previous_year_count = self.db.query(func.count(model_class.id)).filter(
            model_class.dataset_id.in_(active_ids),
            date_col >= previous_year_start,
            date_col <= previous_year_end
        ).scalar() or 0
        
        month_change = calculate_percentage_change(current_month_count, previous_month_count)
        year_change = calculate_percentage_change(current_year_count, previous_year_count)
        
        result = {
            "current_month": current_month_count,
            "previous_month": previous_month_count,
            "month_change_percent": month_change,
            "current_year": current_year_count,
            "previous_year": previous_year_count,
            "year_change_percent": year_change
        }
        self._set_cache("get_historical_comparison", full_key, result)
        return result

    def get_demographics(self) -> dict:
        import pandas as pd
        active_ids = self._get_active_ids()
        is_cached, val, full_key = self._check_cache("get_demographics", active_ids)
        if is_cached:
            return val

        schema_type = self._get_schema_type()
        
        if schema_type == "fir_normalized":
            offender_query = f"""
            SELECT a.AgeYear as age, gm.GenderName as gender, ch.CrimeGroupName as category, d.DistrictName as district
            FROM accused a
            JOIN case_master cm ON a.CaseMasterID = cm.CaseMasterID
            LEFT JOIN unit u ON cm.PoliceStationID = u.UnitID
            LEFT JOIN district d ON u.DistrictID = d.DistrictID
            LEFT JOIN gender_master gm ON a.GenderID = gm.GenderID
            LEFT JOIN crime_head ch ON cm.CrimeMajorHeadID = ch.CrimeHeadID
            WHERE cm.dataset_id IN ({','.join(map(str, active_ids))})
            """
            
            victim_query = f"""
            SELECT v.AgeYear as age, gm.GenderName as gender, ch.CrimeGroupName as category, d.DistrictName as district
            FROM victim v
            JOIN case_master cm ON v.CaseMasterID = cm.CaseMasterID
            LEFT JOIN unit u ON cm.PoliceStationID = u.UnitID
            LEFT JOIN district d ON u.DistrictID = d.DistrictID
            LEFT JOIN gender_master gm ON v.GenderID = gm.GenderID
            LEFT JOIN crime_head ch ON cm.CrimeMajorHeadID = ch.CrimeHeadID
            WHERE cm.dataset_id IN ({','.join(map(str, active_ids))})
            """
        else:
            offender_query = f"""
            SELECT c.age, c.gender, ce.crime_category as category, l.district
            FROM criminals c
            LEFT JOIN crime_participation cp ON c.id = cp.criminal_id
            LEFT JOIN crime_events ce ON cp.crime_event_id = ce.id
            LEFT JOIN locations l ON ce.location_id = l.id
            WHERE c.dataset_id IN ({','.join(map(str, active_ids))})
            """
            
            victim_query = f"""
            SELECT v.age, v.gender, ce.crime_category as category, l.district
            FROM victims v
            LEFT JOIN crime_events ce ON v.crime_event_id = ce.id
            LEFT JOIN locations l ON ce.location_id = l.id
            WHERE v.dataset_id IN ({','.join(map(str, active_ids))})
            """

        df_offenders = pd.read_sql_query(offender_query, self.db.bind)
        df_victims = pd.read_sql_query(victim_query, self.db.bind)

        def get_age_dist(df):
            if df.empty or 'age' not in df.columns:
                return []
            df_clean = df.dropna(subset=['age']).copy()
            df_clean['age'] = pd.to_numeric(df_clean['age'], errors='coerce')
            df_clean = df_clean[df_clean['age'] > 0]
            if df_clean.empty:
                return []
            
            bins = [0, 18, 25, 35, 50, 65, 120]
            labels = ['Under 18', '18-25', '26-35', '36-50', '51-65', 'Over 65']
            df_clean['age_group'] = pd.cut(df_clean['age'], bins=bins, labels=labels)
            counts = df_clean['age_group'].value_counts()
            return [{"category": str(k), "count": int(v)} for k, v in counts.items()]

        def get_gender_dist(df):
            if df.empty or 'gender' not in df.columns:
                return []
            df_clean = df.dropna(subset=['gender']).copy()
            df_clean['gender'] = df_clean['gender'].str.strip().str.capitalize()
            counts = df_clean['gender'].value_counts()
            return [{"category": str(k), "count": int(v)} for k, v in counts.items()]

        age_vs_crime = []
        if not df_offenders.empty and 'age' in df_offenders.columns and 'category' in df_offenders.columns:
            df_c = df_offenders.dropna(subset=['age', 'category']).copy()
            df_c['age'] = pd.to_numeric(df_c['age'], errors='coerce')
            df_c = df_c[df_c['age'] > 0]
            if not df_c.empty:
                bins = [0, 18, 25, 35, 50, 65, 120]
                labels = ['Under 18', '18-25', '26-35', '36-50', '51-65', 'Over 65']
                df_c['age_group'] = pd.cut(df_c['age'], bins=bins, labels=labels)
                grp = df_c.groupby(['age_group', 'category'], observed=False).size().reset_index(name='count')
                age_vs_crime = [{"age_group": str(r['age_group']), "crime_category": str(r['category']), "count": int(r['count'])} for _, r in grp.iterrows() if r['count'] > 0]

        gender_vs_crime = []
        if not df_offenders.empty and 'gender' in df_offenders.columns and 'category' in df_offenders.columns:
            df_g = df_offenders.dropna(subset=['gender', 'category']).copy()
            df_g['gender'] = df_g['gender'].str.strip().str.capitalize()
            if not df_g.empty:
                grp = df_g.groupby(['gender', 'category']).size().reset_index(name='count')
                gender_vs_crime = [{"gender": str(r['gender']), "crime_category": str(r['category']), "count": int(r['count'])} for _, r in grp.iterrows() if r['count'] > 0]

        district_demographics = []
        if not df_offenders.empty and 'district' in df_offenders.columns:
            df_d = df_offenders.dropna(subset=['district']).copy()
            if not df_d.empty:
                for dist, group in df_d.groupby('district'):
                    ages = pd.to_numeric(group['age'], errors='coerce').dropna()
                    avg_age = float(ages.mean()) if not ages.empty else 0.0
                    genders = group['gender'].dropna()
                    pred_gender = str(genders.mode().iloc[0]).capitalize() if not genders.empty else "Unknown"
                    cats = group['category'].dropna()
                    pred_cat = str(cats.mode().iloc[0]) if not cats.empty else "Unknown"
                    district_demographics.append({
                        "district": str(dist),
                        "average_offender_age": round(avg_age, 2),
                        "predominant_gender": pred_gender,
                        "predominant_crime_category": pred_cat,
                        "count": int(len(group))
                    })
                district_demographics = sorted(district_demographics, key=lambda x: x['count'], reverse=True)[:15]

        result = {
            "offender_age_distribution": get_age_dist(df_offenders),
            "offender_gender_distribution": get_gender_dist(df_offenders),
            "victim_age_distribution": get_age_dist(df_victims),
            "victim_gender_distribution": get_gender_dist(df_victims),
            "age_vs_crime": age_vs_crime,
            "gender_vs_crime": gender_vs_crime,
            "district_demographics": district_demographics,
            "data_limitations": [
                "DATA NOT RELIABLE: Caste fields are 100% NULL in database and excluded from sociological analysis.",
                "DATA NOT RELIABLE: Occupation fields are 100% NULL in database and excluded from sociological analysis."
            ]
        }
        self._set_cache("get_demographics", full_key, result)
        return result

    def get_sociological_risk(self) -> dict:
        import pandas as pd
        active_ids = self._get_active_ids()
        is_cached, val, full_key = self._check_cache("get_sociological_risk", active_ids)
        if is_cached:
            return val

        schema_type = self._get_schema_type()
        
        if schema_type == "fir_normalized":
            query = f"""
            SELECT a.AgeYear as age, gm.GenderName as gender, d.DistrictName as district,
                   cm.GravityOffenceID, cm.CrimeRegisteredDate, iot.IncidentFromDate, a.PersonID as person_key
            FROM accused a
            JOIN case_master cm ON a.CaseMasterID = cm.CaseMasterID
            LEFT JOIN inv_occurance_time iot ON cm.CaseMasterID = iot.CaseMasterID
            LEFT JOIN unit u ON cm.PoliceStationID = u.UnitID
            LEFT JOIN district d ON u.DistrictID = d.DistrictID
            LEFT JOIN gender_master gm ON a.GenderID = gm.GenderID
            WHERE cm.dataset_id IN ({','.join(map(str, active_ids))})
            """
            df = pd.read_sql_query(query, self.db.bind)
            if not df.empty:
                df['event_dt'] = pd.to_datetime(df['IncidentFromDate'], errors='coerce').fillna(pd.to_datetime(df['CrimeRegisteredDate'], errors='coerce'))
                df['hour'] = df['event_dt'].dt.hour.fillna(12)
                df['day_of_week'] = df['event_dt'].dt.dayofweek.fillna(0)
                df['is_weekend'] = df['day_of_week'].apply(lambda x: 1 if x in [5, 6] else 0)
                df['is_night_time'] = df['hour'].apply(lambda x: 1 if (x >= 22 or x < 6) else 0)
                df['gravity_offence_id'] = pd.to_numeric(df['GravityOffenceID'], errors='coerce').fillna(1)
                
                base_score = 0.20
                df['risk_score'] = base_score + df['is_night_time'] * 0.25 + (df['gravity_offence_id'] >= 2) * 0.35 + df['is_weekend'] * 0.10
                df['risk_score'] = df['risk_score'].clip(0.05, 0.98).round(4)
                df['person_key'] = df['person_key'].fillna('')
                if (df['person_key'] == '').all():
                    df['person_key'] = df['age'].astype(str) + "_" + df['gender'].astype(str)
        else:
            query = f"""
            SELECT c.age, c.gender, l.district, ce.severity, ce.crime_date, ce.crime_time, cp.criminal_id as person_key
            FROM criminals c
            LEFT JOIN crime_participation cp ON c.id = cp.criminal_id
            LEFT JOIN crime_events ce ON cp.crime_event_id = ce.id
            LEFT JOIN locations l ON ce.location_id = l.id
            WHERE c.dataset_id IN ({','.join(map(str, active_ids))})
            """
            df = pd.read_sql_query(query, self.db.bind)
            if not df.empty:
                df['crime_date'] = pd.to_datetime(df['crime_date'], errors='coerce')
                df['day_of_week'] = df['crime_date'].dt.dayofweek.fillna(0)
                df['is_weekend'] = df['day_of_week'].apply(lambda x: 1 if x in [5, 6] else 0)
                
                def get_hour(t_str):
                    if not t_str: return 12
                    try:
                        return pd.to_datetime(t_str, format='%H:%M:%S').hour
                    except:
                        try:
                            return pd.to_datetime(t_str).hour
                        except:
                            return 12
                
                df['hour'] = df['crime_time'].apply(get_hour)
                df['is_night_time'] = df['hour'].apply(lambda x: 1 if (x >= 22 or x < 6) else 0)
                df['severity'] = pd.to_numeric(df['severity'], errors='coerce').fillna(1.0)
                
                base_score = 0.20
                df['risk_score'] = base_score + df['is_night_time'] * 0.25 + (df['severity'] >= 7.0) * 0.35 + df['is_weekend'] * 0.10
                df['risk_score'] = df['risk_score'].clip(0.05, 0.98).round(4)
                df['person_key'] = df['person_key'].fillna(df.index.to_series())

        if df.empty:
            return {
                "age_group_risk": [],
                "gender_risk": [],
                "district_risk": [],
                "repeat_involvement_risk": [],
                "correlations": []
            }

        df['age'] = pd.to_numeric(df['age'], errors='coerce')
        df_valid_age = df[df['age'] > 0].copy()
        
        age_group_risk = []
        if not df_valid_age.empty:
            bins = [0, 18, 25, 35, 50, 65, 120]
            labels = ['Under 18', '18-25', '26-35', '36-50', '51-65', 'Over 65']
            df_valid_age['age_group'] = pd.cut(df_valid_age['age'], bins=bins, labels=labels)
            grp = df_valid_age.groupby('age_group', observed=False)['risk_score'].mean().reset_index()
            age_group_risk = [{"group": str(r['age_group']), "average_risk": round(float(r['risk_score']), 4)} for _, r in grp.iterrows() if pd.notna(r['risk_score'])]

        gender_risk = []
        df_gender = df.dropna(subset=['gender']).copy()
        df_gender['gender'] = df_gender['gender'].str.strip().str.capitalize()
        if not df_gender.empty:
            grp = df_gender.groupby('gender')['risk_score'].mean().reset_index()
            gender_risk = [{"group": str(r['gender']), "average_risk": round(float(r['risk_score']), 4)} for _, r in grp.iterrows()]

        district_risk = []
        df_dist = df.dropna(subset=['district']).copy()
        if not df_dist.empty:
            grp = df_dist.groupby('district')['risk_score'].mean().reset_index()
            district_risk = [{"group": str(r['district']), "average_risk": round(float(r['risk_score']), 4)} for _, r in grp.iterrows()]
            district_risk = sorted(district_risk, key=lambda x: x['average_risk'], reverse=True)[:15]

        person_counts = df['person_key'].value_counts()
        df['involvements'] = df['person_key'].map(person_counts)
        df['repeat_offender'] = df['involvements'].apply(lambda x: "Repeat Offender" if x > 1 else "First-time Offender")
        
        grp = df.groupby('repeat_offender')['risk_score'].mean().reset_index()
        repeat_involvement_risk = [{"group": str(r['repeat_offender']), "average_risk": round(float(r['risk_score']), 4)} for _, r in grp.iterrows()]

        correlations = []
        df_corr = df.dropna(subset=['age', 'risk_score']).copy()
        if len(df_corr) > 5:
            p_val = float(df_corr['age'].corr(df_corr['risk_score'], method='pearson'))
            s_val = float(df_corr['age'].corr(df_corr['risk_score'], method='spearman'))
            
            p_val = 0.0 if np.isnan(p_val) else p_val
            s_val = 0.0 if np.isnan(s_val) else s_val
            
            min_date = df_corr['event_dt'].min() if 'event_dt' in df_corr.columns else df_corr['crime_date'].min()
            max_date = df_corr['event_dt'].max() if 'event_dt' in df_corr.columns else df_corr['crime_date'].max()
            time_period_str = f"{min_date.date()} to {max_date.date()}" if pd.notna(min_date) and pd.notna(max_date) else "Unknown"

            correlations.append({
                "variables": "Offender Age vs Calculated Model Risk",
                "correlation_type": "Pearson Correlation",
                "correlation_coefficient": round(p_val, 4),
                "sample_size": int(len(df_corr)),
                "geographic_level": "District level aggregates",
                "time_period": time_period_str,
                "interpretation": f"A Pearson coefficient of {round(p_val, 4)} indicates a {'positive' if p_val > 0 else 'negative'} linear association between offender age and risk score."
            })
            
            correlations.append({
                "variables": "Offender Age vs Calculated Model Risk",
                "correlation_type": "Spearman Rank Correlation",
                "correlation_coefficient": round(s_val, 4),
                "sample_size": int(len(df_corr)),
                "geographic_level": "District level aggregates",
                "time_period": time_period_str,
                "interpretation": f"A Spearman rank coefficient of {round(s_val, 4)} indicates a {'positive' if s_val > 0 else 'negative'} monotonic relationship between offender age and risk score ranking."
            })

        result = {
            "age_group_risk": age_group_risk,
            "gender_risk": gender_risk,
            "district_risk": district_risk,
            "repeat_involvement_risk": repeat_involvement_risk,
            "correlations": correlations
        }
        self._set_cache("get_sociological_risk", full_key, result)
        return result

    def get_socioeconomic_correlation(self) -> dict:
        return {
            "data_available": False,
            "error_message": "DATA LIMITATION: Required socio-economic dataset is unavailable."
        }

