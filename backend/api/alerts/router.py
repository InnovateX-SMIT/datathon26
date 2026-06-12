from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from backend.core.database import get_db
from backend.core.logging import logger
from backend.api.auth.router import get_current_user
from backend.schemas.alert import (
    AlertResponse,
    AlertStatusUpdate,
    AlertSummaryResponse
)
from backend.services.alert_service import AlertService

router = APIRouter()

@router.get("/", response_model=List[AlertResponse])
def get_alerts(
    severity: Optional[str] = Query(None, description="Filter by severity (CRITICAL, HIGH, MEDIUM, LOW)"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (NEW, ACKNOWLEDGED, IN_PROGRESS, RESOLVED, DISMISSED)"),
    source: Optional[str] = Query(None, description="Filter by source (prediction, network, decision_support, geo)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> Any:
    """
    Retrieves operational alerts based on status, severity, or source filters.
    """
    try:
        service = AlertService(db)
        return service.get_alerts(
            severity=severity,
            status=status_filter,
            source=source,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        logger.error(f"Error in get_alerts: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error occurred while listing alerts"
        )

@router.get("/summary", response_model=AlertSummaryResponse)
def get_alerts_summary(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> Any:
    """
    Aggregates stats for the alert metrics panel.
    """
    try:
        service = AlertService(db)
        return service.get_summary()
    except Exception as e:
        logger.error(f"Error in get_alerts_summary: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error occurred while computing alerts summary"
        )

@router.get("/{id}", response_model=AlertResponse)
def get_alert_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> Any:
    """
    Retrieves a single alert's details.
    """
    try:
        service = AlertService(db)
        alert = service.get_alert_by_id(alert_id=id)
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Alert with ID {id} not found."
            )
        return alert
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error in get_alert_by_id: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error occurred while fetching alert details"
        )

@router.post("/generate", response_model=List[AlertResponse])
def generate_alerts(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> Any:
    """
    Triggers the rules engine to check for new alerts across predictions and network models.
    """
    try:
        service = AlertService(db)
        return service.generate_alerts_from_intelligence()
    except Exception as e:
        logger.error(f"Error in generate_alerts: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error occurred while generating alerts"
        )

@router.put("/{id}/status", response_model=AlertResponse)
def update_alert_status(
    id: int,
    payload: AlertStatusUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> Any:
    """
    Updates the lifecycle status of an alert. Sets assigned user ID if status is set to IN_PROGRESS.
    """
    try:
        service = AlertService(db)
        
        # Determine current user ID securely (handles dictionary mocks and SQLAlchemy User ORMs)
        user_id = None
        if current_user:
            if isinstance(current_user, dict):
                user_id = current_user.get("id")
            else:
                user_id = getattr(current_user, "id", None)

        # Override user assignment if provided in payload
        assigned_id = payload.assigned_user_id if payload.assigned_user_id is not None else user_id

        # We only assign user if we acknowledge or start investigation
        # Let's set assignment on IN_PROGRESS or ACKNOWLEDGED if desired
        assign_user = assigned_id if payload.status in ["IN_PROGRESS", "ACKNOWLEDGED"] else None

        alert = service.update_alert_status(
            alert_id=id,
            status_str=payload.status,
            assigned_user_id=assign_user
        )
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Alert with ID {id} not found."
            )
        return alert
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error in update_alert_status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error occurred while updating alert status"
        )
