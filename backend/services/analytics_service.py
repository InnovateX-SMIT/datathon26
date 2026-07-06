from datetime import date, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session
from backend.models.crime import CrimeEvent
from backend.models.criminal import Criminal
from backend.models.location import Location

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def _get_active_id(self) -> int:
        from backend.core.dataset_resolver import DatasetResolver
        return DatasetResolver(self.db).get_active_dataset_id()

    def get_dashboard_summary(self) -> dict:
        active_id = self._get_active_id()
        total_crimes = self.db.query(CrimeEvent).filter(CrimeEvent.dataset_id == active_id).count()
        total_victims = self.db.query(func.coalesce(func.sum(CrimeEvent.victim_count), 0)).filter(CrimeEvent.dataset_id == active_id).scalar()
        total_accused = self.db.query(func.coalesce(func.sum(CrimeEvent.accused_count), 0)).filter(CrimeEvent.dataset_id == active_id).scalar()
        active_cases = self.db.query(CrimeEvent).filter(
            CrimeEvent.dataset_id == active_id,
            CrimeEvent.status.in_(["reported", "under_investigation"])
        ).count()
        high_risk_criminals = self.db.query(Criminal).filter(
            Criminal.dataset_id == active_id,
            Criminal.risk_score >= 7.0
        ).count()
        total_criminals = self.db.query(Criminal).filter(Criminal.dataset_id == active_id).count()

        return {
            "total_crimes": total_crimes,
            "total_victims": total_victims,
            "total_accused": total_accused,
            "active_cases": active_cases,
            "high_risk_criminals": high_risk_criminals,
            "total_criminals": total_criminals,
        }

    def get_crime_trend(self, days: int = 30) -> list[dict]:
        active_id = self._get_active_id()
        max_date = self.db.query(func.max(CrimeEvent.crime_date)).filter(CrimeEvent.dataset_id == active_id).scalar()
        anchor_date = max_date if max_date is not None else date.today()
        start_date = anchor_date - timedelta(days=days)
        results = self.db.query(
            CrimeEvent.crime_date,
            func.count(CrimeEvent.id)
        ).filter(
            CrimeEvent.dataset_id == active_id,
            CrimeEvent.crime_date >= start_date
        ).group_by(
            CrimeEvent.crime_date
        ).order_by(
            CrimeEvent.crime_date.asc()
        ).all()

        return [{"date": r[0].isoformat(), "count": r[1]} for r in results if r[0] is not None]

    def get_category_breakdown(self) -> list[dict]:
        active_id = self._get_active_id()
        results = self.db.query(
            CrimeEvent.crime_category,
            func.count(CrimeEvent.id)
        ).filter(
            CrimeEvent.dataset_id == active_id
        ).group_by(
            CrimeEvent.crime_category
        ).order_by(
            func.count(CrimeEvent.id).desc()
        ).limit(9).all()

        return [{"category": r[0], "count": r[1]} for r in results if r[0] is not None]

    def get_district_ranking(self) -> list[dict]:
        active_id = self._get_active_id()
        results = self.db.query(
            Location.district,
            func.count(CrimeEvent.id)
        ).join(
            Location,
            CrimeEvent.location_id == Location.id
        ).filter(
            CrimeEvent.dataset_id == active_id
        ).group_by(
            Location.district
        ).order_by(
            func.count(CrimeEvent.id).desc()
        ).limit(10).all()

        return [{"district": r[0], "count": r[1]} for r in results if r[0] is not None]

    def get_recent_crimes(self, limit: int = 10) -> list[dict]:
        active_id = self._get_active_id()
        results = self.db.query(
            CrimeEvent,
            Location.district
        ).outerjoin(
            Location,
            CrimeEvent.location_id == Location.id
        ).filter(
            CrimeEvent.dataset_id == active_id
        ).order_by(
            CrimeEvent.created_at.desc()
        ).limit(limit).all()

        recent_crimes = []
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
        return recent_crimes

    def get_system_status(self) -> dict:
        active_id = self._get_active_id()
        total_records = self.db.query(CrimeEvent).filter(CrimeEvent.dataset_id == active_id).count()
        if total_records == 0:
            return {
                "database_status": "online",
                "total_records": 0,
                "last_updated": "N/A",
                "data_coverage_days": 0,
            }

        max_created_at = self.db.query(func.max(CrimeEvent.created_at)).filter(CrimeEvent.dataset_id == active_id).scalar()
        last_updated = max_created_at.isoformat() if max_created_at else "N/A"

        min_crime_date = self.db.query(func.min(CrimeEvent.crime_date)).filter(CrimeEvent.dataset_id == active_id).scalar()
        max_crime_date = self.db.query(func.max(CrimeEvent.crime_date)).filter(CrimeEvent.dataset_id == active_id).scalar()

        if min_crime_date and max_crime_date:
            data_coverage_days = (max_crime_date - min_crime_date).days
        else:
            data_coverage_days = 0

        return {
            "database_status": "online",
            "total_records": total_records,
            "last_updated": last_updated,
            "data_coverage_days": data_coverage_days,
        }

    def get_overview_metrics(self) -> dict:
        active_id = self._get_active_id()
        total_crimes = self.db.query(func.count(CrimeEvent.id)).filter(CrimeEvent.dataset_id == active_id).scalar() or 0
        total_victims = self.db.query(func.coalesce(func.sum(CrimeEvent.victim_count), 0)).filter(CrimeEvent.dataset_id == active_id).scalar() or 0
        total_accused = self.db.query(func.coalesce(func.sum(CrimeEvent.accused_count), 0)).filter(CrimeEvent.dataset_id == active_id).scalar() or 0
        return {
            "total_crimes": total_crimes,
            "total_victims": total_victims,
            "total_accused": total_accused
        }

    def get_daily_trends(self) -> list[dict]:
        active_id = self._get_active_id()
        from analytics.temporal_analysis.daily import analyze_daily_trends
        results = self.db.query(
            CrimeEvent.crime_date,
            func.count(CrimeEvent.id)
        ).filter(
            CrimeEvent.dataset_id == active_id,
            CrimeEvent.crime_date.isnot(None)
        ).group_by(
            CrimeEvent.crime_date
        ).order_by(
            CrimeEvent.crime_date.asc()
        ).all()
        
        records = [{"period": r[0].isoformat() if hasattr(r[0], 'isoformat') else str(r[0]), "count": r[1]} for r in results]
        return analyze_daily_trends(records)

    def get_weekly_trends(self) -> list[dict]:
        active_id = self._get_active_id()
        from analytics.temporal_analysis.weekly import analyze_weekly_trends
        if self.db.bind.dialect.name == "postgresql":
            expr = func.date_trunc('week', CrimeEvent.crime_date)
        else:
            expr = func.date(CrimeEvent.crime_date, 'weekday 1', '-7 days')
            
        results = self.db.query(
            expr,
            func.count(CrimeEvent.id)
        ).filter(
            CrimeEvent.dataset_id == active_id,
            CrimeEvent.crime_date.isnot(None)
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
            
        return analyze_weekly_trends(records)

    def get_monthly_trends(self) -> list[dict]:
        active_id = self._get_active_id()
        from analytics.temporal_analysis.monthly import analyze_monthly_trends
        if self.db.bind.dialect.name == "postgresql":
            expr = func.to_char(CrimeEvent.crime_date, 'YYYY-MM')
        else:
            expr = func.strftime('%Y-%m', CrimeEvent.crime_date)
            
        results = self.db.query(
            expr,
            func.count(CrimeEvent.id)
        ).filter(
            CrimeEvent.dataset_id == active_id,
            CrimeEvent.crime_date.isnot(None)
        ).group_by(
            expr
        ).order_by(
            expr.asc()
        ).all()
        
        records = [{"period": str(r[0]), "count": r[1]} for r in results]
        return analyze_monthly_trends(records)

    def get_yearly_trends(self) -> list[dict]:
        active_id = self._get_active_id()
        from analytics.temporal_analysis.yearly import analyze_yearly_trends
        if self.db.bind.dialect.name == "postgresql":
            expr = func.to_char(CrimeEvent.crime_date, 'YYYY')
        else:
            expr = func.strftime('%Y', CrimeEvent.crime_date)
            
        results = self.db.query(
            expr,
            func.count(CrimeEvent.id)
        ).filter(
            CrimeEvent.dataset_id == active_id,
            CrimeEvent.crime_date.isnot(None)
        ).group_by(
            expr
        ).order_by(
            expr.asc()
        ).all()
        
        records = [{"period": str(r[0]), "count": r[1]} for r in results]
        return analyze_yearly_trends(records)

    def get_category_distribution(self) -> list[dict]:
        active_id = self._get_active_id()
        from analytics.crime_analysis.category_analysis import process_category_distribution
        results = self.db.query(
            CrimeEvent.crime_category,
            func.count(CrimeEvent.id)
        ).filter(
            CrimeEvent.dataset_id == active_id,
            CrimeEvent.crime_category.isnot(None)
        ).group_by(
            CrimeEvent.crime_category
        ).all()
        
        records = [{"name": r[0], "count": r[1]} for r in results]
        return process_category_distribution(records)

    def get_subcategory_distribution(self) -> list[dict]:
        active_id = self._get_active_id()
        from analytics.crime_analysis.category_analysis import process_subcategory_distribution
        results = self.db.query(
            CrimeEvent.crime_subcategory,
            func.count(CrimeEvent.id)
        ).filter(
            CrimeEvent.dataset_id == active_id,
            CrimeEvent.crime_subcategory.isnot(None)
        ).group_by(
            CrimeEvent.crime_subcategory
        ).all()
        
        records = [{"name": r[0], "count": r[1]} for r in results]
        return process_subcategory_distribution(records)

    def get_historical_comparison(self) -> dict:
        active_id = self._get_active_id()
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
        
        current_month_count = self.db.query(func.count(CrimeEvent.id)).filter(
            CrimeEvent.dataset_id == active_id,
            CrimeEvent.crime_date >= current_month_start,
            CrimeEvent.crime_date <= current_month_end
        ).scalar() or 0
        
        previous_month_count = self.db.query(func.count(CrimeEvent.id)).filter(
            CrimeEvent.dataset_id == active_id,
            CrimeEvent.crime_date >= previous_month_start,
            CrimeEvent.crime_date <= previous_month_end
        ).scalar() or 0
        
        current_year_count = self.db.query(func.count(CrimeEvent.id)).filter(
            CrimeEvent.dataset_id == active_id,
            CrimeEvent.crime_date >= current_year_start,
            CrimeEvent.crime_date <= current_year_end
        ).scalar() or 0
        
        previous_year_count = self.db.query(func.count(CrimeEvent.id)).filter(
            CrimeEvent.dataset_id == active_id,
            CrimeEvent.crime_date >= previous_year_start,
            CrimeEvent.crime_date <= previous_year_end
        ).scalar() or 0
        
        month_change = calculate_percentage_change(current_month_count, previous_month_count)
        year_change = calculate_percentage_change(current_year_count, previous_year_count)
        
        return {
            "current_month": current_month_count,
            "previous_month": previous_month_count,
            "month_change_percent": month_change,
            "current_year": current_year_count,
            "previous_year": previous_year_count,
            "year_change_percent": year_change
        }
