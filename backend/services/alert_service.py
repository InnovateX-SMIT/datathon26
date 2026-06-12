import json
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List, Optional, Dict, Any

from backend.models.alert import Alert
from backend.models.prediction import Prediction
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
        # 1. PREDICTIVE ALERTS
        # ==========================================
        preds = self.db.query(Prediction).options(
            joinedload(Prediction.crime_event).joinedload(CrimeEvent.location)
        ).order_by(Prediction.generated_at.desc()).limit(50).all()

        for p in preds:
            # Hotspot prediction alerts
            if p.prediction_type == "hotspot":
                prob = p.confidence_score
                district = "Unknown"
                if p.crime_event and p.crime_event.location:
                    district = p.crime_event.location.district

                if prob >= 0.70:
                    severity = "CRITICAL" if prob >= 0.85 else "HIGH"
                    stage_alert(
                        title="Critical Hotspot Warning" if severity == "CRITICAL" else "Emerging Hotspot Alert",
                        description=f"Emerging crime hotspot predicted in {district} with probability {prob * 100:.1f}%.",
                        severity=severity,
                        source="prediction",
                        crime_event_id=p.crime_event_id,
                        metadata={"probability": prob, "district": district}
                    )

            # Repeat offender recidivism alerts
            elif p.prediction_type == "repeat-offender":
                prob = p.confidence_score
                if prob >= 0.70:
                    stage_alert(
                        title="High Recidivism Alert",
                        description=f"High risk of offender recidivism flagged by predictions engine ({prob * 100:.1f}% probability).",
                        severity="HIGH",
                        source="prediction",
                        crime_event_id=p.crime_event_id,
                        metadata={"recidivism_probability": prob}
                    )

            # High crime risk score alerts
            elif p.prediction_type == "crime-risk":
                score = p.confidence_score  # score normalized from 0 to 1
                if score >= 0.75:
                    stage_alert(
                        title="Elevated District Crime Risk",
                        description=f"Predictions engine flags elevated crime risk index of {score * 100:.1f} in recent runs.",
                        severity="HIGH",
                        source="prediction",
                        crime_event_id=p.crime_event_id,
                        metadata={"risk_score": score}
                    )

        # ==========================================
        # 2. NETWORK ALERTS
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
        # Unresolved high priority recommendations
        unresolved_recs = self.db.query(Recommendation).filter(
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
        # High crime density concentration alerts
        geo_results = self.db.query(
            Location.district, func.count(CrimeEvent.id).label("crime_count")
        ).join(
            Location, CrimeEvent.location_id == Location.id
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
