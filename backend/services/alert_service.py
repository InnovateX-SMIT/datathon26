import json
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from datetime import date, timedelta
from typing import List, Optional, Dict, Any

from backend.models.alert import Alert
from backend.models.recommendation import Recommendation, ResourceAllocation
from backend.models.crime import CrimeEvent
from backend.models.location import Location
from backend.repositories.alert_repository import AlertRepository
from backend.schemas.alert import AlertCreate
from backend.services.network_analytics_service import NetworkAnalyticsService

class AlertService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AlertRepository(db)

    def generate_alerts_from_intelligence(self) -> List[Alert]:
        """
        Runs the platform operational rules engine to convert predictions, networks,
        geo-stats, and pending recommendations into real-time alerts.
        """
        from backend.core.dataset_resolver import DatasetResolver
        active_id = DatasetResolver(self.db).get_active_dataset_id()
        schema_type = DatasetResolver(self.db).get_active_dataset_schema_type()
        
        alerts_to_create = []
        seen_identifiers = set()
        active_statuses = ["NEW", "ACKNOWLEDGED", "IN_PROGRESS"]

        # Helper to safely stage alerts
        def stage_alert(title: str, description: str, severity: str, source: str, crime_event_id: Optional[int] = None, metadata: Optional[dict] = None):
            # Form unique key for in-memory deduplication
            key = (title, description)
            if key in seen_identifiers:
                return

            seen_identifiers.add(key)

            # Check database for active duplicates
            if not self.repo.check_alert_exists(title, description, active_statuses):
                alerts_to_create.append(AlertCreate(
                    crime_event_id=crime_event_id,
                    title=title,
                    description=description,
                    severity=severity,
                    source=source,
                    status="NEW",
                    metadata_payload=json.dumps(metadata) if metadata else None
                ))

        # ==========================================
        # 1. NETWORK ALERTS
        # ==========================================
        try:
            net_service = NetworkAnalyticsService(self.db)
            
            # Centrality Bridge discovery
            centrality = net_service.get_centrality(limit=5)
            for item in centrality.get("betweenness", []):
                if item["type"] == "criminal" and item["score"] >= 0.15:
                    stage_alert(
                        title="Criminal Network Bridge Identified",
                        description=f"Key bridge offender discovered: {item['label']} (Betweenness Centrality: {item['score']:.2f}).",
                        severity="HIGH",
                        source="network",
                        metadata={"suspect_id": item["id"], "score": item["score"]}
                    )

            # Cluster Gang discovery
            clusters = net_service.get_clusters()
            for cluster in clusters:
                if cluster["criminal_count"] >= 3 and cluster["size"] >= 5:
                    stage_alert(
                        title="Active Crime Cluster Detected",
                        description=f"Interconnected gang {cluster['cluster_id']} identified with {cluster['criminal_count']} co-offenders across {cluster['crime_count']} crimes.",
                        severity="CRITICAL",
                        source="network",
                        metadata={"cluster_id": cluster["cluster_id"], "size": cluster["size"]}
                    )
        except Exception:
            pass

        # ==========================================
        # 3. DECISION SUPPORT ALERTS
        # ==========================================
        if schema_type == "fir_normalized":
            unresolved_recs = self.db.query(Recommendation).filter(
                Recommendation.status == "pending",
                Recommendation.priority == "high"
            ).limit(10).all()
        else:
            unresolved_recs = self.db.query(Recommendation).outerjoin(CrimeEvent).filter(
                (CrimeEvent.dataset_id == active_id) | (Recommendation.crime_event_id.is_(None)),
                Recommendation.status == "pending",
                Recommendation.priority == "high"
            ).limit(10).all()

        for rec in unresolved_recs:
            stage_alert(
                title="Pending High Priority Action",
                description=f"Unresolved critical recommendation: {rec.recommendation_text}",
                severity="HIGH",
                source="decision_support",
                crime_event_id=rec.crime_event_id,
                metadata={"recommendation_id": rec.id}
            )

        # Personnel shortage / resource imbalance alerts
        allocations = self.db.query(ResourceAllocation).order_by(ResourceAllocation.created_at.desc()).limit(5).all()
        for alloc in allocations:
            try:
                solved_data = json.loads(alloc.solved_allocation)
                for beat in solved_data:
                    # If beat normalized severity is very high (> 40%), but total staff assigned is low (< 5 officers)
                    severity = beat.get("normalized_severity", 0.0)
                    total_staff = beat.get("asi_allocated", 0) + beat.get("chc_allocated", 0) + beat.get("cpc_allocated", 0)
                    if severity >= 0.40 and total_staff < 5:
                        stage_alert(
                            title="Resource Allocation Staffing Deficit",
                            description=f"Shortage in district '{alloc.district}': Beat '{beat.get('beat_name')}' has severity {severity * 100:.1f}% but only {total_staff} staff allocated.",
                            severity="HIGH",
                            source="decision_support",
                            metadata={"district": alloc.district, "beat_name": beat.get("beat_name"), "severity": severity}
                        )
            except Exception:
                pass

        # ==========================================
        # 4. GEO ALERTS
        # ==========================================
        # High crime density concentration alerts — restricted to last 30 days to avoid
        # stale historical counts permanently triggering alerts
        if schema_type == "fir_normalized":
            from backend.models.fir_case import CaseMaster
            from backend.models.fir_geography import District
            from backend.models.fir_organization import Unit
            
            max_date = self.db.query(func.max(CaseMaster.CrimeRegisteredDate)).filter(CaseMaster.dataset_id == active_id).scalar()
            anchor_date = max_date if max_date is not None else date.today()
            thirty_days_ago = anchor_date - timedelta(days=30)

            geo_results = self.db.query(
                District.name, func.count(CaseMaster.id).label("crime_count")
            ).select_from(CaseMaster).join(Unit, CaseMaster.PoliceStationID == Unit.id).join(District, Unit.DistrictID == District.id).filter(
                CaseMaster.dataset_id == active_id,
                CaseMaster.CrimeRegisteredDate >= thirty_days_ago
            ).group_by(District.name).all()
        else:
            max_date = self.db.query(func.max(CrimeEvent.crime_date)).filter(CrimeEvent.dataset_id == active_id).scalar()
            anchor_date = max_date if max_date is not None else date.today()
            thirty_days_ago = anchor_date - timedelta(days=30)

            geo_results = self.db.query(
                Location.district, func.count(CrimeEvent.id).label("crime_count")
            ).join(
                Location, CrimeEvent.location_id == Location.id
            ).filter(
                CrimeEvent.dataset_id == active_id,
                CrimeEvent.crime_date >= thirty_days_ago
            ).group_by(Location.district).all()

        for dist_name, count in geo_results:
            if count >= 150:
                severity = "CRITICAL" if count >= 300 else "HIGH"
                stage_alert(
                    title="Critical Crime Concentration Area" if severity == "CRITICAL" else "Elevated Crime Concentration Area",
                    description=f"District '{dist_name}' has mapped high density concentration of {count} crime cases.",
                    severity=severity,
                    source="geo",
                    metadata={"district": dist_name, "crime_count": count}
                )

        # Bulk write all newly staged alerts
        if alerts_to_create:
            return self.repo.create_alerts_bulk(alerts_to_create)
        return []

    def get_alerts(self, severity: Optional[str] = None, status: Optional[str] = None, source: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[Alert]:
        return self.repo.get_alerts(severity=severity, status=status, source=source, skip=skip, limit=limit)

    def get_alert_by_id(self, alert_id: int) -> Optional[Alert]:
        return self.repo.get_alert_by_id(alert_id)

    def update_alert_status(self, alert_id: int, status_str: str, assigned_user_id: Optional[int] = None) -> Optional[Alert]:
        return self.repo.update_alert_status(alert_id, status=status_str, assigned_user_id=assigned_user_id)

    def get_summary(self) -> Dict[str, Any]:
        return self.repo.get_alert_summary_statistics()
