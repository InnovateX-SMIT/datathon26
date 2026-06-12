from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime
from backend.models.alert import Alert
from backend.schemas.alert import AlertCreate
from typing import Optional, List, Dict, Any

class AlertRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_alert(self, alert: AlertCreate) -> Alert:
        db_alert = Alert(
            crime_event_id=alert.crime_event_id,
            title=alert.title,
            description=alert.description,
            severity=alert.severity,
            source=alert.source,
            status=alert.status,
            assigned_user_id=alert.assigned_user_id,
            metadata_payload=alert.metadata_payload
        )
        self.db.add(db_alert)
        self.db.commit()
        self.db.refresh(db_alert)
        return db_alert

    def create_alerts_bulk(self, alerts: List[AlertCreate]) -> List[Alert]:
        db_alerts = []
        for alert in alerts:
            db_alert = Alert(
                crime_event_id=alert.crime_event_id,
                title=alert.title,
                description=alert.description,
                severity=alert.severity,
                source=alert.source,
                status=alert.status,
                assigned_user_id=alert.assigned_user_id,
                metadata_payload=alert.metadata_payload
            )
            self.db.add(db_alert)
            db_alerts.append(db_alert)
        self.db.commit()
        for db_alert in db_alerts:
            self.db.refresh(db_alert)
        return db_alerts

    def get_alerts(
        self,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        source: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Alert]:
        query = self.db.query(Alert)
        if severity:
            query = query.filter(Alert.severity == severity)
        if status:
            query = query.filter(Alert.status == status)
        if source:
            query = query.filter(Alert.source == source)
        return query.order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()

    def get_alert_by_id(self, alert_id: int) -> Optional[Alert]:
        return self.db.query(Alert).filter(Alert.id == alert_id).first()

    def update_alert_status(
        self,
        alert_id: int,
        status: str,
        assigned_user_id: Optional[int] = None
    ) -> Optional[Alert]:
        db_alert = self.get_alert_by_id(alert_id)
        if db_alert:
            db_alert.status = status
            if assigned_user_id is not None:
                db_alert.assigned_user_id = assigned_user_id
            self.db.commit()
            self.db.refresh(db_alert)
        return db_alert

    def check_alert_exists(self, title: str, description: str, active_statuses: List[str]) -> bool:
        """
        Check if an alert with identical parameters is already active (to prevent spam).
        """
        count = self.db.query(Alert).filter(
            Alert.title == title,
            Alert.description == description,
            Alert.status.in_(active_statuses)
        ).count()
        return count > 0

    def get_alert_summary_statistics(self) -> Dict[str, Any]:
        """
        Aggregates summary counts and distributions for the stats panel and Recharts.
        """
        # Active alerts: NEW, ACKNOWLEDGED, IN_PROGRESS
        total_active = self.db.query(Alert).filter(
            Alert.status.in_(["NEW", "ACKNOWLEDGED", "IN_PROGRESS"])
        ).count()

        # Critical alerts (severity = CRITICAL)
        critical_count = self.db.query(Alert).filter(
            Alert.severity == "CRITICAL",
            Alert.status.in_(["NEW", "ACKNOWLEDGED", "IN_PROGRESS"])
        ).count()

        # Resolved alerts
        resolved_count = self.db.query(Alert).filter(
            Alert.status == "RESOLVED"
        ).count()

        # Alerts created today (start of day till now)
        today_start = datetime.combine(date.today(), datetime.min.time())
        today_count = self.db.query(Alert).filter(
            Alert.created_at >= today_start
        ).count()

        # Breakdown by Source
        source_results = self.db.query(
            Alert.source, func.count(Alert.id)
        ).group_by(Alert.source).all()
        by_source = [{"source": r[0], "count": r[1]} for r in source_results]

        # Breakdown by Severity
        severity_results = self.db.query(
            Alert.severity, func.count(Alert.id)
        ).group_by(Alert.severity).all()
        by_severity = [{"severity": r[0], "count": r[1]} for r in severity_results]

        return {
            "total_active": total_active,
            "critical_count": critical_count,
            "resolved_count": resolved_count,
            "today_count": today_count,
            "by_source": by_source,
            "by_severity": by_severity
        }
