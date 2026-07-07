import json
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.core.logging import logger
from backend.core.dataset_resolver import DatasetResolver
from backend.models.dataset import Dataset
from backend.models.ml_model import MLModel
from backend.models.prediction import Prediction
from backend.models.recommendation import RecommendationHistory, Recommendation
from backend.models.alert import Alert
from backend.models.location import Location
from backend.models.crime import CrimeEvent
from backend.models.criminal import Criminal

from backend.services.analytics_service import AnalyticsService
from backend.services.prediction_service import PredictionService
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

        # 2. Refreshes dataset predictions
        prediction_svc = PredictionService(self.db)
        self._refresh_dataset_predictions(prediction_svc, active_ids)

        # 3. Regenerates Recommendations
        recs_svc = RecommendationService(self.db)
        recs = recs_svc.generate_dynamic_recommendations()

        # 4. Dynamically processes live Alerts
        alert_svc = AlertService(self.db)
        alerts = alert_svc.generate_alerts_from_intelligence()

        # 5. Get current active model info
        latest_model = self.db.query(MLModel).filter(
            MLModel.status == "Completed"
        ).order_by(MLModel.created_at.desc()).first()
        model_version = latest_model.version if latest_model else "Bundled Fallback"

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

    def _refresh_dataset_predictions(self, prediction_svc: PredictionService, active_ids: list[int]):
        """
        Runs batch inference across active dataset attributes to feed prediction tables.
        """
        # Query top districts in active datasets
        districts_counts = self.db.query(
            Location.district, func.count(CrimeEvent.id)
        ).join(
            Location, CrimeEvent.location_id == Location.id
        ).filter(
            CrimeEvent.dataset_id.in_(active_ids)
        ).group_by(Location.district).order_by(func.count(CrimeEvent.id).desc()).limit(5).all()

        for dist, cnt in districts_counts:
            try:
                # Predict Hotspot probability
                prediction_svc.predict_hotspot(
                    district=dist,
                    trend_metrics=float(cnt),
                    historical_crime_growth=1.15
                )
                # Predict Crime Risk rating
                prediction_svc.predict_crime_risk(
                    district=dist,
                    crime_category="Property",
                    historical_crime_count=int(cnt)
                )
            except Exception as e:
                logger.error(f"Error refreshing predictions for district {dist}: {e}")

        # Query top risk offenders
        criminals = self.db.query(Criminal).filter(
            Criminal.dataset_id.in_(active_ids)
        ).order_by(Criminal.risk_score.desc()).limit(5).all()

        for crim in criminals:
            try:
                prediction_svc.predict_repeat_offender(
                    age=float(crim.age or 30),
                    occupation=str(crim.occupation or "Unemployed"),
                    caste=str(crim.caste or "General"),
                    district="D1"
                )
            except Exception as e:
                logger.error(f"Error refreshing recidivism for offender {crim.name}: {e}")
