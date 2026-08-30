from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.core.logging import logger
from backend.api.auth.router import get_current_user
from backend.api.deps import get_session_id
from backend.schemas.analytics import (
    DashboardSummaryResponse,
    TrendDataPoint,
    CategoryDataPoint,
    DistrictDataPoint,
    RecentCrimeItem,
    SystemStatusResponse,
    OverviewResponse,
    TrendResponse,
    CategoryResponse,
    ComparisonResponse,
    DemographicsResponse,
    SociologicalRiskResponse,
    SocioEconomicCorrelationResponse,
)
from backend.services.analytics_service import AnalyticsService

router = APIRouter()

@router.get("/dashboard/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    session_id: str = Depends(get_session_id),
    current_user = Depends(get_current_user)
):
    try:
        service = AnalyticsService(db, session_id=session_id)
        return service.get_dashboard_summary()
    except Exception as e:
        logger.error(f"Error fetching dashboard summary: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/dashboard/trend", response_model=list[TrendDataPoint])
def get_crime_trend(
    days: int = Query(default=30, ge=7, le=365),
    db: Session = Depends(get_db),
    session_id: str = Depends(get_session_id),
    current_user = Depends(get_current_user)
):
    try:
        service = AnalyticsService(db, session_id=session_id)
        return service.get_crime_trend(days=days)
    except Exception as e:
        logger.error(f"Error fetching crime trend: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/dashboard/categories", response_model=list[CategoryDataPoint])
def get_category_breakdown(
    db: Session = Depends(get_db),
    session_id: str = Depends(get_session_id),
    current_user = Depends(get_current_user)
):
    try:
        service = AnalyticsService(db, session_id=session_id)
        return service.get_category_breakdown()
    except Exception as e:
        logger.error(f"Error fetching category breakdown: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/dashboard/districts", response_model=list[DistrictDataPoint])
def get_district_ranking(
    db: Session = Depends(get_db),
    session_id: str = Depends(get_session_id),
    current_user = Depends(get_current_user)
):
    try:
        service = AnalyticsService(db, session_id=session_id)
        return service.get_district_ranking()
    except Exception as e:
        logger.error(f"Error fetching district ranking: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/dashboard/recent-crimes", response_model=list[RecentCrimeItem])
def get_recent_crimes(
    db: Session = Depends(get_db),
    session_id: str = Depends(get_session_id),
    current_user = Depends(get_current_user)
):
    try:
        service = AnalyticsService(db, session_id=session_id)
        return service.get_recent_crimes()
    except Exception as e:
        logger.error(f"Error fetching recent crimes: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/dashboard/system-status", response_model=SystemStatusResponse)
def get_system_status(
    db: Session = Depends(get_db),
    session_id: str = Depends(get_session_id),
    current_user = Depends(get_current_user)
):
    try:
        service = AnalyticsService(db, session_id=session_id)
        return service.get_system_status()
    except Exception as e:
        logger.error(f"Error fetching system status: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/overview", response_model=OverviewResponse)
def get_overview_metrics(
    db: Session = Depends(get_db),
    session_id: str = Depends(get_session_id),
    current_user = Depends(get_current_user)
):
    try:
        service = AnalyticsService(db, session_id=session_id)
        return service.get_overview_metrics()
    except Exception as e:
        logger.error(f"Error fetching overview metrics: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/trends", response_model=list[TrendResponse])
def get_trends(
    granularity: str = Query(default="daily"),
    db: Session = Depends(get_db),
    session_id: str = Depends(get_session_id),
    current_user = Depends(get_current_user)
):
    if granularity not in ["daily", "weekly", "monthly", "yearly"]:
        raise HTTPException(status_code=400, detail="Invalid granularity. Allowed values: daily, weekly, monthly, yearly")
    try:
        service = AnalyticsService(db, session_id=session_id)
        if granularity == "daily":
            return service.get_daily_trends()
        elif granularity == "weekly":
            return service.get_weekly_trends()
        elif granularity == "monthly":
            return service.get_monthly_trends()
        elif granularity == "yearly":
            return service.get_yearly_trends()
    except Exception as e:
        logger.error(f"Error fetching temporal trends: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/categories", response_model=CategoryResponse)
def get_category_breakdown(
    db: Session = Depends(get_db),
    session_id: str = Depends(get_session_id),
    current_user = Depends(get_current_user)
):
    try:
        service = AnalyticsService(db, session_id=session_id)
        categories = service.get_category_distribution()
        subcategories = service.get_subcategory_distribution()
        return CategoryResponse(categories=categories, subcategories=subcategories)
    except Exception as e:
        logger.error(f"Error fetching category breakdown: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/comparison", response_model=ComparisonResponse)
def get_historical_comparison(
    db: Session = Depends(get_db),
    session_id: str = Depends(get_session_id),
    current_user = Depends(get_current_user)
):
    try:
        service = AnalyticsService(db, session_id=session_id)
        return service.get_historical_comparison()
    except Exception as e:
        logger.error(f"Error fetching historical comparison: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/demographics", response_model=DemographicsResponse)
def get_demographics(
    db: Session = Depends(get_db),
    session_id: str = Depends(get_session_id),
    current_user = Depends(get_current_user)
):
    try:
        service = AnalyticsService(db, session_id=session_id)
        return service.get_demographics()
    except Exception as e:
        logger.error(f"Error fetching demographics: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/sociological-risk", response_model=SociologicalRiskResponse)
def get_sociological_risk(
    db: Session = Depends(get_db),
    session_id: str = Depends(get_session_id),
    current_user = Depends(get_current_user)
):
    try:
        service = AnalyticsService(db, session_id=session_id)
        return service.get_sociological_risk()
    except Exception as e:
        logger.error(f"Error fetching sociological risk: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/socioeconomic-correlation", response_model=SocioEconomicCorrelationResponse)
def get_socioeconomic_correlation(
    db: Session = Depends(get_db),
    session_id: str = Depends(get_session_id),
    current_user = Depends(get_current_user)
):
    try:
        service = AnalyticsService(db, session_id=session_id)
        return service.get_socioeconomic_correlation()
    except Exception as e:
        logger.error(f"Error fetching socioeconomic correlation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


