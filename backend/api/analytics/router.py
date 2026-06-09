from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.core.logging import logger
from backend.api.auth.router import get_current_user
from backend.schemas.analytics import (
    DashboardSummaryResponse,
    TrendDataPoint,
    CategoryDataPoint,
    DistrictDataPoint,
    RecentCrimeItem,
    SystemStatusResponse,
)
from backend.services.analytics_service import AnalyticsService

router = APIRouter()

@router.get("/dashboard/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        service = AnalyticsService(db)
        return service.get_dashboard_summary()
    except Exception as e:
        logger.error(f"Error fetching dashboard summary: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/dashboard/trend", response_model=list[TrendDataPoint])
def get_crime_trend(
    days: int = Query(default=30, ge=7, le=365),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        service = AnalyticsService(db)
        return service.get_crime_trend(days=days)
    except Exception as e:
        logger.error(f"Error fetching crime trend: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/dashboard/categories", response_model=list[CategoryDataPoint])
def get_category_breakdown(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        service = AnalyticsService(db)
        return service.get_category_breakdown()
    except Exception as e:
        logger.error(f"Error fetching category breakdown: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/dashboard/districts", response_model=list[DistrictDataPoint])
def get_district_ranking(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        service = AnalyticsService(db)
        return service.get_district_ranking()
    except Exception as e:
        logger.error(f"Error fetching district ranking: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/dashboard/recent-crimes", response_model=list[RecentCrimeItem])
def get_recent_crimes(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        service = AnalyticsService(db)
        return service.get_recent_crimes()
    except Exception as e:
        logger.error(f"Error fetching recent crimes: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/dashboard/system-status", response_model=SystemStatusResponse)
def get_system_status(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        service = AnalyticsService(db)
        return service.get_system_status()
    except Exception as e:
        logger.error(f"Error fetching system status: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
