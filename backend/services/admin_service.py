import os
import sys
import json
import importlib.metadata
from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.core.config import settings
from backend.core.logging import logger
from backend.repositories.admin_repository import AdminRepository


class AdminService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AdminRepository(db)
    def get_system_health(self, performed_by_user_id: int) -> Dict[str, Any]:
        # Step 1: Test DB connection
        db_status = "healthy"
        try:
            self.db.execute(text("SELECT 1"))
        except Exception as e:
            logger.error(f"DB health check failed: {e}")
            db_status = "unhealthy"

        # Step 2: Get dialect and masked URL
        try:
            from backend.core.database import engine as db_engine
            dialect = db_engine.dialect.name
        except Exception:
            dialect = "unknown"

        db_url = settings.DATABASE_URL
        # Mask everything after the scheme prefix
        if "://" in db_url:
            scheme = db_url.split("://")[0]
            url_masked = f"{scheme}:///***"
        else:
            url_masked = "***"

        # Step 3: Table counts
        tables = self.repo.get_table_record_counts()

        # Step 4: Python version
        pv = sys.version_info
        python_version = f"{pv.major}.{pv.minor}.{pv.micro}"

        # Step 5: FastAPI version
        try:
            fastapi_version = importlib.metadata.version("fastapi")
        except Exception:
            fastapi_version = "unknown"

        # Step 6: Audit log
        self.repo.create_audit_log(
            user_id=performed_by_user_id,
            action="SYSTEM_HEALTH_CHECKED",
            entity_type="system",
            details=json.dumps({"db_status": db_status})
        )

        return {
            "database": {
                "status": db_status,
                "dialect": dialect,
                "url_masked": url_masked
            },
            "tables": tables,
            "api": {
                "status": "operational",
                "version": "1.0.0",
                "environment": settings.ENVIRONMENT
            },
            "server": {
                "python_version": python_version,
                "fastapi_version": fastapi_version
            }
        }

    def get_model_status(self) -> Dict[str, Any]:
        expected_models = [
            {"name": "Crime Type Prediction",     "path": "ml/crime_prediction/model.pkl"},
            {"name": "Crime Risk Prediction",      "path": "ml/crime_prediction/risk_model.pkl"},
            {"name": "Hotspot Prediction",          "path": "ml/hotspot_prediction/model.pkl"},
            {"name": "Repeat Offender Prediction", "path": "ml/offender_prediction/model.pkl"},
        ]

        model_results = []
        for model in expected_models:
            path = model["path"]
            if os.path.exists(path):
                size_kb = round(os.path.getsize(path) / 1024, 2)
                model_results.append({
                    "name": model["name"],
                    "path": path,
                    "status": "loaded",
                    "size_kb": size_kb
                })
            else:
                model_results.append({
                    "name": model["name"],
                    "path": path,
                    "status": "missing",
                    "size_kb": None
                })

        return {
            "models": model_results,
            "checked_at": datetime.utcnow()
        }

    # ── Audit Logs ───────────────────────────────────────────────────────────

    def get_audit_logs(
        self,
        page: int = 1,
        page_size: int = 50,
        action_filter: Optional[str] = None,
        performed_by_user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        skip = (page - 1) * page_size
        logs = self.repo.get_audit_logs(skip, page_size, action_filter)
        total = self.repo.get_audit_log_count(action_filter)

        # Log only if performed by a user
        if performed_by_user_id is not None:
            self.repo.create_audit_log(
                user_id=performed_by_user_id,
                action="AUDIT_LOGS_VIEWED",
                entity_type="audit",
                details=json.dumps({"page": page, "page_size": page_size, "action_filter": action_filter})
            )

        return {
            "logs": logs,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    # ── Dataset Status ───────────────────────────────────────────────────────

    def get_dataset_status(self, performed_by_user_id: int) -> Dict[str, Any]:
        counts = self.repo.get_table_record_counts()

        tables_list = [{"table": name, "record_count": count} for name, count in counts.items()]
        total_records = sum(counts.values())

        self.repo.create_audit_log(
            user_id=performed_by_user_id,
            action="DATASET_STATUS_VIEWED",
            entity_type="dataset",
            details=json.dumps({"total_records": total_records})
        )

        return {
            "tables": tables_list,
            "total_records": total_records,
            "checked_at": datetime.utcnow()
        }

    def refresh_models(self, performed_by_user_id: int) -> dict:
        from backend.services.prediction_service import PredictionService
        # Clear the internal cache to force a reload from disk
        PredictionService._cached_models.clear()
        
        self.repo.create_audit_log(
            user_id=performed_by_user_id,
            action="MODELS_REFRESHED",
            entity_type="system",
            details="ML model cache cleared and scheduled for reload."
        )
        return {"status": "success", "message": "Models refreshed successfully"}

    def trigger_safe_reimport(self, performed_by_user_id: int) -> dict:
        from sqlalchemy import text
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from database.seed import seed_locations, seed_police_stations, seed_crimes
        
        try:
            # Safely truncate only the data tables, preserving users and history
            self.db.execute(text("DELETE FROM crime_events"))
            self.db.execute(text("DELETE FROM police_stations"))
            self.db.execute(text("DELETE FROM locations"))
            self.db.commit()
            
            # Re-seed
            seed_locations(self.db)
            seed_police_stations(self.db)
            seed_crimes(self.db)
            
            self.repo.create_audit_log(
                user_id=performed_by_user_id,
                action="DATASET_REIMPORTED",
                entity_type="dataset",
                details="Safely truncated and re-seeded crime and location data."
            )
            return {"status": "success", "message": "Data re-imported successfully"}
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to re-import data: {str(e)}")
