import json
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.core.logging import logger
from backend.core.dataset_resolver import DatasetResolver
from backend.models.dataset import Dataset
from backend.models.recommendation import RecommendationHistory, Recommendation
from backend.models.alert import Alert
from backend.models.location import Location
from backend.models.crime import CrimeEvent
from backend.models.criminal import Criminal

from backend.services.analytics_service import AnalyticsService
from backend.services.recommendation_service import RecommendationService
from backend.services.alert_service import AlertService

class SynchronizationService:
    def __init__(self, db: Session):
        self.db = db

    def synchronize_pipeline(self) -> dict:
        """
        Runs the end-to-end operational synchronization:
        1. Pre-warms analytics cache.
        2. Refreshes dataset-specific predictions (hotspots, risk, recidivism).
        3. Regenerates tactical recommendations.
        4. Dynamically processes live alerts.
        5. Logs the run details to recommendation_history.
        """
        active_ids = DatasetResolver(self.db).get_active_dataset_ids()
        if not active_ids:
            return {"status": "skipped", "reason": "No active dataset is selected."}

        # 1. Warm Analytics Cache
        analytics_svc = AnalyticsService(self.db)
        analytics_svc.get_dashboard_summary()

        # 3. Regenerates Recommendations
        recs_svc = RecommendationService(self.db)
        recs = recs_svc.generate_dynamic_recommendations()

        # 4. Dynamically processes live Alerts
        alert_svc = AlertService(self.db)
        alerts = alert_svc.generate_alerts_from_intelligence()

        # 5. Set default model version
        model_version = "Bundled Fallback"

        # 6. Log history record
        history = RecommendationHistory(
            dataset_ids=",".join(str(i) for i in active_ids),
            model_version=model_version,
            alert_count=len(alerts),
            generated_recommendations_count=len(recs),
            status="completed"
        )
        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)

        return {
            "status": "success",
            "active_dataset_ids": active_ids,
            "model_version": model_version,
            "recommendations_count": len(recs),
            "alerts_count": len(alerts),
            "history_id": history.id
        }


