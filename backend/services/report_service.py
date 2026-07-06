import json
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any, Optional
from datetime import datetime

from backend.models.report import Report
from backend.models.crime import CrimeEvent
from backend.models.criminal import Criminal
from backend.models.prediction import Prediction
from backend.repositories.report_repository import ReportRepository

from backend.services.analytics_service import AnalyticsService
from backend.services.prediction_service import PredictionService
from backend.services.network_analytics_service import NetworkAnalyticsService
from backend.services.recommendation_service import RecommendationService
from backend.services.alert_service import AlertService

REPORT_TYPES = {
    "district_intelligence": {
        "key": "district_intelligence",
        "name": "District Intelligence Report",
        "description": "Consolidates district-wide crime counts, localized hotspots, and operational staffing indicators."
    },
    "crime_trend": {
        "key": "crime_trend",
        "name": "Crime Trend Report",
        "description": "Analyzes historical temporal comparison charts and category distribution trends."
    },
    "risk_assessment": {
        "key": "risk_assessment",
        "name": "Risk Assessment Report",
        "description": "Assesses criminal recidivism probabilities and emerging crime hotspot risks."
    },
    "network_intelligence": {
        "key": "network_intelligence",
        "name": "Network Intelligence Report",
        "description": "Details co-offending gang clusters, centralities, and key criminal network influencers."
    },
    "executive_summary": {
        "key": "executive_summary",
        "name": "Executive Summary Report",
        "description": "High-level summary compiling critical alerts, major recommendations, and general statistics."
    }
}

class ReportService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ReportRepository(db)
        self.analytics_service = AnalyticsService(db)
        self.prediction_service = PredictionService(db)
        self.network_analytics_service = NetworkAnalyticsService(db)
        self.recommendation_service = RecommendationService(db)
        self.alert_service = AlertService(db)

    def get_supported_types(self) -> List[Dict[str, str]]:
        return list(REPORT_TYPES.values())

    def retrieve_generated_reports(self) -> List[Report]:
        return self.repo.get_reports()

    def get_report_by_id(self, report_id: int) -> Optional[Dict[str, Any]]:
        db_report = self.repo.get_report_by_id(report_id)
        if not db_report:
            return None
        # Fast path: return cached payload if available
        if db_report.data_payload:
            try:
                data = json.loads(db_report.data_payload)
                data["report_id"] = db_report.id
                data["generated_at"] = db_report.generated_at
                return data
            except (json.JSONDecodeError, TypeError):
                pass
        # Slow path: re-assemble (only for legacy reports without payload)
        return self._assemble_report_response(db_report)

    def trigger_report_generation(self, title: str, report_type: str) -> Dict[str, Any]:
        if report_type not in REPORT_TYPES:
            raise ValueError(f"Unsupported report type: {report_type}")

        # Assemble the aggregated metrics first
        overview = self._get_crime_overview()
        predictions = self._get_predictive_insights()
        networks = self._get_network_insights()
        recs = self._get_recommendations()
        alerts = self._get_alerts()

        # Generate contextual summary
        summary_text = self._generate_executive_summary(
            report_type, overview, predictions, networks, recs, alerts
        )

        # Assemble the full response dict before persisting
        assembled = self._assemble_report_response(
            type('_TmpReport', (), {
                'id': None, 'report_type': report_type,
                'title': title, 'generated_at': None, 'summary': summary_text
            })(),
            overview, predictions, networks, recs, alerts
        )

        # Persist report metadata initially without payload
        db_report = self.repo.create_report(
            title=title,
            report_type=report_type,
            summary=summary_text,
            data_payload=None
        )

        # Fill dynamic DB-generated values
        assembled["report_id"] = db_report.id
        assembled["generated_at"] = db_report.generated_at

        # Serialize assembled payload for fast-path cache
        try:
            payload_json = json.dumps(assembled, default=str)
        except (TypeError, ValueError):
            payload_json = None

        # Save the serialized JSON with IDs
        db_report.data_payload = payload_json
        self.db.commit()

        return assembled

    def _assemble_report_response(
        self,
        db_report: Report,
        overview: Optional[Dict[str, Any]] = None,
        predictions: Optional[Dict[str, Any]] = None,
        networks: Optional[Dict[str, Any]] = None,
        recs: Optional[List[Dict[str, Any]]] = None,
        alerts: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        
        # Gather live aggregations if not already provided
        if overview is None:
            overview = self._get_crime_overview()
        if predictions is None:
            predictions = self._get_predictive_insights()
        if networks is None:
            networks = self._get_network_insights()
        if recs is None:
            recs = self._get_recommendations()
        if alerts is None:
            alerts = self._get_alerts()

        return {
            "report_id": db_report.id,
            "report_type": db_report.report_type,
            "title": db_report.title,
            "generated_at": db_report.generated_at,
            "executive_summary": db_report.summary or "No summary generated for this report.",
            "crime_overview": overview,
            "predictive_insights": predictions,
            "network_insights": networks,
            "recommendations": recs,
            "alerts": alerts
        }

    def _get_crime_overview(self) -> Dict[str, Any]:
        total_crimes = self.db.query(CrimeEvent).count()
        
        categories_raw = self.analytics_service.get_category_breakdown()
        top_categories = []
        for r in categories_raw:
            top_categories.append({
                "category": r["category"],
                "count": r["count"]
            })

        # Calculate trend direction
        trend_direction = "STABLE"
        try:
            comparison = self.analytics_service.get_historical_comparison()
            pct = comparison.get("month_change_percent", 0.0)
            if pct > 5.0:
                trend_direction = "UP"
            elif pct < -5.0:
                trend_direction = "DOWN"
        except Exception:
            pass

        return {
            "total_crimes": total_crimes,
            "top_categories": top_categories,
            "trend_direction": trend_direction
        }

    def _get_predictive_insights(self) -> Dict[str, Any]:
        # High risk locations (top districts with highest counts)
        high_risk_locations = []
        try:
            rankings = self.analytics_service.get_district_ranking()
            for r in rankings[:5]:
                cnt = r["count"]
                risk = "MEDIUM"
                if cnt >= 300:
                    risk = "CRITICAL"
                elif cnt >= 150:
                    risk = "HIGH"
                
                high_risk_locations.append({
                    "district": r["district"],
                    "crime_count": cnt,
                    "risk_level": risk
                })
        except Exception:
            pass

        # Hotspot count based on recent active hotspot predictions
        hotspot_count = self.db.query(Prediction).filter(
            Prediction.prediction_type == "hotspot",
            Prediction.confidence_score >= 0.70
        ).count()

        # Risk score summary statistics
        avg_score_raw = self.db.query(func.avg(Criminal.risk_score)).scalar()
        avg_score = round(float(avg_score_raw), 2) if avg_score_raw is not None else 0.0
        high_risk_criminals = self.db.query(Criminal).filter(Criminal.risk_score >= 7.0).count()

        return {
            "high_risk_locations": high_risk_locations,
            "hotspot_count": hotspot_count,
            "risk_score_summary": {
                "average_criminal_risk": avg_score,
                "high_risk_criminals_count": high_risk_criminals,
                "total_criminals_tracked": self.db.query(Criminal).count()
            }
        }

    def _get_network_insights(self) -> Dict[str, Any]:
        total_networks = 0
        largest_network_size = 0
        try:
            clusters = self.network_analytics_service.get_clusters()
            total_networks = len(clusters)
            if clusters:
                largest_network_size = max(c["size"] for c in clusters)
        except Exception:
            pass

        key_entities = []
        try:
            centrality = self.network_analytics_service.get_centrality(limit=5)
            # Fetch from betweenness rank
            for entity in centrality.get("betweenness", [])[:5]:
                key_entities.append({
                    "id": entity["id"],
                    "type": entity["type"],
                    "label": entity["label"],
                    "score": round(float(entity["score"]), 4)
                })
        except Exception:
            pass

        return {
            "total_networks": total_networks,
            "largest_network_size": largest_network_size,
            "key_entities": key_entities
        }

    def _get_recommendations(self) -> List[Dict[str, Any]]:
        recommendations_list = []
        try:
            recs = self.recommendation_service.get_recommendations(status="pending")
            if not recs:
                # generate defaults/live recommendations to avoid empty structures
                recs = self.recommendation_service.generate_dynamic_recommendations()
            
            for r in recs[:10]:
                recommendations_list.append({
                    "id": r.id,
                    "priority": r.priority,
                    "recommendation_text": r.recommendation_text,
                    "reason": r.reason,
                    "status": r.status
                })
        except Exception:
            pass
        return recommendations_list

    def _get_alerts(self) -> List[Dict[str, Any]]:
        alerts_list = []
        try:
            alerts = self.alert_service.get_alerts(status="NEW")
            if not alerts:
                # generate alerts
                alerts = self.alert_service.generate_alerts_from_intelligence()
            
            for a in alerts[:10]:
                alerts_list.append({
                    "id": a.id,
                    "title": a.title,
                    "description": a.description,
                    "severity": a.severity,
                    "source": a.source,
                    "status": a.status
                })
        except Exception:
            pass
        return alerts_list

    def _generate_executive_summary(
        self,
        report_type: str,
        overview: Dict[str, Any],
        predictions: Dict[str, Any],
        networks: Dict[str, Any],
        recs: List[Dict[str, Any]],
        alerts: List[Dict[str, Any]]
    ) -> str:
        total_crimes = overview["total_crimes"]
        top_cats_str = ", ".join([c["category"] for c in overview["top_categories"][:3]]) or "None"
        trend_direction = overview["trend_direction"]
        
        hotspot_count = predictions["hotspot_count"]
        avg_risk = predictions["risk_score_summary"]["average_criminal_risk"]
        high_risk_count = predictions["risk_score_summary"]["high_risk_criminals_count"]
        high_risk_districts = ", ".join([l["district"] for l in predictions["high_risk_locations"][:3]]) or "None"

        total_networks = networks["total_networks"]
        largest_network_size = networks["largest_network_size"]
        top_entities_str = ", ".join([e["label"] for e in networks["key_entities"][:2]]) or "None"

        rec_count = len(recs)
        alert_count = len(alerts)

        if report_type == "district_intelligence":
            return (
                f"District Intelligence Briefing: This report compiles tactical intelligence across all beats and police limits. "
                f"A total of {total_crimes} crimes are currently recorded. The highest incidence is in the {high_risk_districts} districts, "
                f"which are flagged with high concentration levels. Network analytics identified {total_networks} distinct co-offending components, "
                f"with the largest group containing {largest_network_size} linked suspects. Operational recommendations outline immediate patrols "
                f"in forecasted hotspot areas."
            )
        elif report_type == "crime_trend":
            return (
                f"Crime Trend Analysis Dossier: Statistical trends indicate a {trend_direction.lower()} trend in active incident logging. "
                f"Top categories are dominated by: {top_cats_str}. Historical comparisons indicate that resource adjustments may be "
                f"necessary to counter emerging patterns. A total of {hotspot_count} emerging hotspots are currently flagged, highlighting "
                f"areas of high crime density concentration."
            )
        elif report_type == "risk_assessment":
            return (
                f"Risk Assessment and Recidivism Report: This intelligence report details community risk profiles and individual "
                f"repeat-offender predictions. Average criminal risk index stands at {avg_risk}/10, with {high_risk_count} entities "
                f"flagged with critical recidivism risk (>= 7.0). Spot predictions identified {hotspot_count} emerging high-probability "
                f"hotspots, necessitating immediate preventative check-ins."
            )
        elif report_type == "network_intelligence":
            return (
                f"Criminal Network Intelligence Brief: Relational network analysis has mapped {total_networks} distinct co-offending associations. "
                f"Centrality mapping highlighted key entities, including {top_entities_str}, acting as critical bridges/brokers between "
                f"disparate gang elements. Disruption of these key entities is recommended to break down the network structure."
            )
        else: # executive_summary
            return (
                f"Executive Summary Briefing: A comprehensive overview of current public safety and criminal intelligence. "
                f"Key parameters indicate a total of {total_crimes} events, {hotspot_count} emerging hotspots, and {total_networks} criminal networks. "
                f"We recommend immediate execution of the {rec_count} strategic recommendations and monitoring the {alert_count} active critical/high alerts."
            )
