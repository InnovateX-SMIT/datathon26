import os
import sys

# Ensure backend package can be imported from parent directory if run from inside backend
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import time
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.core.config import settings
from backend.core.logging import logger
from backend.core.database import engine, Base

# Import all models to ensure they are registered on Metadata before we call create_all
from backend import models

# Create tables in development
if settings.ENVIRONMENT == "development":
    logger.info("Recreating database tables in development environment...")
    Base.metadata.create_all(bind=engine)
    
    # Seeding database with default accounts
    from backend.core.database import SessionLocal
    from backend.models.user import User, UserRole
    from backend.core.security import get_password_hash
    
    db = SessionLocal()
    try:
        default_users = [
            {
                "email": "admin@police.gov.in",
                "name": "Platform Admin",
                "password": "admin123",
                "role": UserRole.ADMIN,
            },
            {
                "email": "sp@police.gov.in",
                "name": "Superintendent Patil",
                "password": "sp123",
                "role": UserRole.SUPERINTENDENT,
            },
            {
                "email": "officer@police.gov.in",
                "name": "Officer Sharma",
                "password": "officer123",
                "role": UserRole.OFFICER,
            },
        ]
        for u_data in default_users:
            user = db.query(User).filter(User.email == u_data["email"]).first()
            if not user:
                logger.info(f"Seeding default user: {u_data['email']}")
                db.add(User(
                    email=u_data["email"],
                    name=u_data["name"],
                    password_hash=get_password_hash(u_data["password"]),
                    role=u_data["role"],
                    status="active"
                ))
        db.commit()
        logger.info("Database seeding completed.")
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to allowed origins
    allow_credentials=True,
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

# Mock/Placeholder Routers setup
# Let's import the routes we will create next
from backend.api.auth.router import router as auth_router
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
app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(crimes_router, prefix=f"{settings.API_V1_STR}/crimes", tags=["Crimes"])
app.include_router(analytics_router, prefix=f"{settings.API_V1_STR}/analytics", tags=["Crime Analytics"])
app.include_router(geo_router, prefix=f"{settings.API_V1_STR}/geo", tags=["Geo Intelligence"])
app.include_router(predictions_router, prefix=f"{settings.API_V1_STR}/predictions", tags=["Predictive Intelligence"])
app.include_router(network_router, prefix=f"{settings.API_V1_STR}/network", tags=["Criminal Network Intelligence"])
app.include_router(recommendations_router, prefix=f"{settings.API_V1_STR}/recommendations", tags=["Decision Support Recommendations"])
app.include_router(alerts_router, prefix=f"{settings.API_V1_STR}/alerts", tags=["System & Patrol Alerts"])
app.include_router(reports_router, prefix=f"{settings.API_V1_STR}/reports", tags=["Executive Reports"])
app.include_router(admin_router, prefix=f"{settings.API_V1_STR}/admin", tags=["Admin Portal"])
