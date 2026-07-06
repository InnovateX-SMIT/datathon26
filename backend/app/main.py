import os
import sys

# Ensure backend package can be imported from parent directory if run from inside backend
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import time
import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.core.config import settings
from backend.core.logging import logger
from backend.core.database import engine, Base

# Import all models to ensure they are registered on Metadata before we call create_all
from backend import models

def migrate_database_schema(db_engine):
    from sqlalchemy import text
    try:
        # We only apply SQLite-specific migration logic for alerts table mapping
        if db_engine.dialect.name != "sqlite":
            logger.info("Database dialect is not SQLite; skipping alerts table schema migration.")
            return

        with db_engine.begin() as conn:
            # 1. Scoping column migrations
            for table_name in ["crime_events", "criminals", "victims", "crime_participation"]:
                result = conn.execute(text(f"PRAGMA table_info({table_name})"))
                cols = {row[1] for row in result.fetchall()}
                if cols and "dataset_id" not in cols:
                    logger.info(f"Adding dataset_id column to {table_name} table...")
                    conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN dataset_id INTEGER REFERENCES datasets(id) ON DELETE CASCADE"))

            # 1b. Scoping datasets table migrations
            result = conn.execute(text("PRAGMA table_info(datasets)"))
            ds_cols = {row[1] for row in result.fetchall()}
            if ds_cols:
                if "column_count" not in ds_cols:
                    logger.info("Adding column_count column to datasets table...")
                    conn.execute(text("ALTER TABLE datasets ADD COLUMN column_count INTEGER DEFAULT 0"))
                if "upload_status" not in ds_cols:
                    logger.info("Adding upload_status column to datasets table...")
                    conn.execute(text("ALTER TABLE datasets ADD COLUMN upload_status VARCHAR(50) DEFAULT 'Completed'"))
                if "storage_path" not in ds_cols:
                    logger.info("Adding storage_path column to datasets table...")
                    conn.execute(text("ALTER TABLE datasets ADD COLUMN storage_path VARCHAR(500) NULL"))

            # 1c. Scoping dataset_configs table migrations
            conn.execute(text(
                "CREATE TABLE IF NOT EXISTS dataset_configs ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "max_active_datasets VARCHAR(20) DEFAULT '1'"
                ")"
            ))
            # Seed default config row if empty
            res_config = conn.execute(text("SELECT id FROM dataset_configs LIMIT 1")).fetchone()
            if not res_config:
                logger.info("Initializing dataset_configs with default row...")
                conn.execute(text("INSERT INTO dataset_configs (max_active_datasets) VALUES ('1')"))

            # 2. Ensure default dataset exists and map existing rows to it
            res = conn.execute(text("SELECT id FROM datasets WHERE name = 'System Seed' LIMIT 1")).fetchone()
            if not res:
                logger.info("Default System Seed dataset not found. Seeding it in registry...")
                conn.execute(text(
                    "INSERT INTO datasets (name, original_filename, display_name, description, source_type, status, is_active, row_count, file_size, created_at, updated_at) "
                    "VALUES ('System Seed', 'crime_events.csv', 'Synthetic 50K', 'System default seeded dataset', 'System Seed', 'Ready', 1, 50000, 5872123, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
                ))
                default_id = conn.execute(text("SELECT last_insert_rowid()")).scalar()
                logger.info(f"Default dataset registered with ID: {default_id}. Associating existing orphaned rows...")
                for table_name in ["crime_events", "criminals", "victims", "crime_participation"]:
                    conn.execute(text(f"UPDATE {table_name} SET dataset_id = {default_id} WHERE dataset_id IS NULL"))
            else:
                # Heal existing record if row_count/file_size are NULL
                conn.execute(text(
                    "UPDATE datasets SET row_count = 50000, file_size = 5872123 "
                    "WHERE name = 'System Seed' AND (row_count IS NULL OR file_size IS NULL)"
                ))

            # Ensure at least one dataset is active
            active_dataset = conn.execute(text("SELECT id FROM datasets WHERE is_active = 1 LIMIT 1")).fetchone()
            if not active_dataset:
                first_dataset = conn.execute(text("SELECT id FROM datasets LIMIT 1")).fetchone()
                if first_dataset:
                    logger.info(f"No active dataset found. Setting dataset ID {first_dataset[0]} as active.")
                    conn.execute(text(f"UPDATE datasets SET is_active = 1 WHERE id = {first_dataset[0]}"))

            # Check table info for alerts
            result = conn.execute(text("PRAGMA table_info(alerts)"))
            columns = {row[1] for row in result.fetchall()}
            
            if columns:
                # Columns to add if they are missing
                missing_cols = []
                if "title" not in columns:
                    missing_cols.append("ALTER TABLE alerts ADD COLUMN title VARCHAR(150) NOT NULL DEFAULT ''")
                if "description" not in columns:
                    missing_cols.append("ALTER TABLE alerts ADD COLUMN description VARCHAR(1000) NOT NULL DEFAULT ''")
                if "source" not in columns:
                    missing_cols.append("ALTER TABLE alerts ADD COLUMN source VARCHAR(100) NOT NULL DEFAULT 'prediction'")
                if "assigned_user_id" not in columns:
                    missing_cols.append("ALTER TABLE alerts ADD COLUMN assigned_user_id INTEGER NULL")
                if "metadata_payload" not in columns:
                    missing_cols.append("ALTER TABLE alerts ADD COLUMN metadata_payload VARCHAR(2000) NULL")
                    
                for sql in missing_cols:
                    logger.info(f"Running migration SQL: {sql}")
                    conn.execute(text(sql))

                if "updated_at" not in columns:
                    logger.info("Adding updated_at to alerts table...")
                    conn.execute(text("ALTER TABLE alerts ADD COLUMN updated_at DATETIME"))
                    conn.execute(text("UPDATE alerts SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL"))

                if missing_cols or "updated_at" not in columns:
                    logger.info("Database schema migration completed successfully.")
 
            # Handle recommendations table migration
            result = conn.execute(text("PRAGMA table_info(recommendations)"))
            rec_columns = {row[1] for row in result.fetchall()}
            if rec_columns and "updated_at" not in rec_columns:
                logger.info("Adding updated_at to recommendations table...")
                conn.execute(text("ALTER TABLE recommendations ADD COLUMN updated_at DATETIME"))
                conn.execute(text("UPDATE recommendations SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL"))

            # Handle reports table migration
            result = conn.execute(text("PRAGMA table_info(reports)"))
            rpt_cols = {row[1] for row in result.fetchall()}
            if rpt_cols and "data_payload" not in rpt_cols:
                conn.execute(text("ALTER TABLE reports ADD COLUMN data_payload TEXT NULL"))
                logger.info("Added missing 'data_payload' column to reports table.")

        logger.info("AuditLog table ensured via create_all.")
    except Exception as e:
        logger.error(f"Error during dynamic alerts table migration: {e}")

# Create tables in development
if settings.ENVIRONMENT == "development":
    logger.info("Recreating database tables in development environment...")
    Base.metadata.create_all(bind=engine)
    migrate_database_schema(engine)
    

def _warmup_network_cache():
    """Background thread: pre-builds all NetworkAnalyticsService caches at startup."""
    from backend.core.database import SessionLocal
    from backend.services.network_analytics_service import NetworkAnalyticsService
    db = SessionLocal()
    try:
        logger.info("Network cache warmup started...")
        svc = NetworkAnalyticsService(db)
        svc.get_graph()
        svc.get_centrality()
        svc.get_clusters()
        svc.get_repeat_associations()
        svc.get_location_intelligence()
        logger.info("Network cache warmup complete.")
    except Exception as e:
        logger.error(f"Network cache warmup failed: {e}", exc_info=True)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Only pre-warm on non-test environments
    if settings.ENVIRONMENT != "test":
        thread = threading.Thread(target=_warmup_network_cache, daemon=True)
        thread.start()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to allowed origins
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom performance log middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response: Response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"Request: {request.method} {request.url.path} - Status: {response.status_code} - Duration: {process_time:.4f}s")
    return response

# Custom Exception Handler
from backend.core.exceptions import NoActiveDatasetException

@app.exception_handler(NoActiveDatasetException)
async def no_active_dataset_exception_handler(request: Request, exc: NoActiveDatasetException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.message},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global error handler caught: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please contact system administrator."},
    )

# Health Check Route
@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "environment": settings.ENVIRONMENT,
        "service": settings.PROJECT_NAME
    }

# API routers
from backend.api.crimes.router import router as crimes_router
from backend.api.analytics.router import router as analytics_router
from backend.api.geo.router import router as geo_router
from backend.api.predictions.router import router as predictions_router
from backend.api.network.router import router as network_router
from backend.api.recommendations.router import router as recommendations_router
from backend.api.alerts.router import router as alerts_router
from backend.api.reports.router import router as reports_router
from backend.api.admin.router import router as admin_router

# Register routers with API Prefix
app.include_router(crimes_router, prefix=f"{settings.API_V1_STR}/crimes", tags=["Crimes"])
app.include_router(analytics_router, prefix=f"{settings.API_V1_STR}/analytics", tags=["Crime Analytics"])
app.include_router(geo_router, prefix=f"{settings.API_V1_STR}/geo", tags=["Geo Intelligence"])
app.include_router(predictions_router, prefix=f"{settings.API_V1_STR}/predictions", tags=["Predictive Intelligence"])
app.include_router(network_router, prefix=f"{settings.API_V1_STR}/network", tags=["Criminal Network Intelligence"])
app.include_router(recommendations_router, prefix=f"{settings.API_V1_STR}/recommendations", tags=["Decision Support Recommendations"])
app.include_router(alerts_router, prefix=f"{settings.API_V1_STR}/alerts", tags=["System & Patrol Alerts"])
app.include_router(reports_router, prefix=f"{settings.API_V1_STR}/reports", tags=["Executive Reports"])
app.include_router(admin_router, prefix=f"{settings.API_V1_STR}/admin", tags=["Admin Portal"])
