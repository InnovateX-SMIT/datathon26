from datetime import date, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session
from backend.models.crime import CrimeEvent
from backend.models.criminal import Criminal
from backend.models.location import Location

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_dashboard_summary(self) -> dict:
        total_crimes = self.db.query(CrimeEvent).count()
        total_victims = self.db.query(func.coalesce(func.sum(CrimeEvent.victim_count), 0)).scalar()
        total_accused = self.db.query(func.coalesce(func.sum(CrimeEvent.accused_count), 0)).scalar()
        active_cases = self.db.query(CrimeEvent).filter(
            CrimeEvent.status.in_(["reported", "under_investigation"])
        ).count()
        high_risk_criminals = self.db.query(Criminal).filter(
            Criminal.risk_score >= 7.0
        ).count()
        total_criminals = self.db.query(Criminal).count()

        return {
            "total_crimes": total_crimes,
            "total_victims": total_victims,
            "total_accused": total_accused,
            "active_cases": active_cases,
            "high_risk_criminals": high_risk_criminals,
            "total_criminals": total_criminals,
        }

    def get_crime_trend(self, days: int = 30) -> list[dict]:
        start_date = date.today() - timedelta(days=days)
        results = self.db.query(
            CrimeEvent.crime_date,
            func.count(CrimeEvent.id)
        ).filter(
            CrimeEvent.crime_date >= start_date
        ).group_by(
            CrimeEvent.crime_date
        ).order_by(
            CrimeEvent.crime_date.asc()
        ).all()

        return [{"date": r[0].isoformat(), "count": r[1]} for r in results if r[0] is not None]

    def get_category_breakdown(self) -> list[dict]:
        results = self.db.query(
            CrimeEvent.crime_category,
            func.count(CrimeEvent.id)
        ).group_by(
            CrimeEvent.crime_category
        ).order_by(
            func.count(CrimeEvent.id).desc()
        ).limit(9).all()

        return [{"category": r[0], "count": r[1]} for r in results if r[0] is not None]

    def get_district_ranking(self) -> list[dict]:
        results = self.db.query(
            Location.district,
            func.count(CrimeEvent.id)
        ).join(
            Location,
            CrimeEvent.location_id == Location.id
        ).group_by(
            Location.district
        ).order_by(
            func.count(CrimeEvent.id).desc()
        ).limit(10).all()

        return [{"district": r[0], "count": r[1]} for r in results if r[0] is not None]

    def get_recent_crimes(self, limit: int = 10) -> list[dict]:
        results = self.db.query(
            CrimeEvent,
            Location.district
        ).outerjoin(
            Location,
            CrimeEvent.location_id == Location.id
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
        total_records = self.db.query(CrimeEvent).count()
        if total_records == 0:
            return {
                "database_status": "online",
                "total_records": 0,
                "last_updated": "N/A",
                "data_coverage_days": 0,
            }

        max_created_at = self.db.query(func.max(CrimeEvent.created_at)).scalar()
        last_updated = max_created_at.isoformat() if max_created_at else "N/A"

        min_crime_date = self.db.query(func.min(CrimeEvent.crime_date)).scalar()
        max_crime_date = self.db.query(func.max(CrimeEvent.crime_date)).scalar()

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
