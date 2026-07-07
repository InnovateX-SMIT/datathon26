from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from backend.core.database import get_db
from backend.core.logging import logger
from backend.api.auth.router import get_current_user
from backend.schemas.recommendation import (
    AllocationPayload,
    AllocationResponse,
    ResourceAllocationResponse,
    RecommendationResponse,
    RecommendationStatusUpdate
)
from backend.services.recommendation_service import RecommendationService

router = APIRouter()

@router.post("/solve", response_model=AllocationResponse)
def run_allocation_solver(
    payload: AllocationPayload,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> Any:
    """
    Solves resource allocation optimization for a district and logs the run in history.
    """
    try:
        service = RecommendationService(db)
        allocations = service.run_resource_optimization(
            district=payload.district,
            sanctioned_asi=payload.sanctioned_asi,
            sanctioned_chc=payload.sanctioned_chc,
            sanctioned_cpc=payload.sanctioned_cpc
        )
        if not allocations:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No police stations found in district {payload.district}."
            )
        return AllocationResponse(
            status="success",
            district=payload.district,
            solved_allocation=allocations
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error in run_allocation_solver: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error occurred while running the resource optimization solver"
        )

@router.get("/resource-allocation", response_model=List[ResourceAllocationResponse])
def get_resource_allocations_history(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> Any:
    """
    Retrieves the logs of previous resource allocation runs.
    """
    try:
        service = RecommendationService(db)
        return service.fetch_allocations_logs()
    except Exception as e:
        logger.error(f"Error in get_resource_allocations_history: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error occurred while retrieving resource allocation logs"
        )

@router.get("/", response_model=List[RecommendationResponse])
def get_recommendations(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (pending, resolved, dismissed)"),
    priority_filter: Optional[str] = Query(None, alias="priority", description="Filter by priority (high, medium, low)"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> Any:
    """
    Lists prioritized decision support actions / recommendations.
    """
    try:
        service = RecommendationService(db)
        return service.get_recommendations(status=status_filter, priority=priority_filter)
    except Exception as e:
        logger.error(f"Error in get_recommendations: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error occurred while retrieving recommendations"
        )

@router.post("/generate", response_model=List[RecommendationResponse])
def generate_recommendations(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> Any:
    """
    Triggers refresh of dynamic recommendations from latest intelligence data.
    """
    try:
        service = RecommendationService(db)
        recs = service.generate_dynamic_recommendations()
        
        from backend.repositories.admin_repository import AdminRepository
        admin_repo = AdminRepository(db)
        admin_repo.create_audit_log(
            user_id=current_user.id if current_user and not isinstance(current_user, dict) else (current_user.get("id") if isinstance(current_user, dict) else None),
            action="RECOMMENDATION_GENERATED",
            details=f"Generated {len(recs)} dynamic recommendations"
        )
        
        return recs
    except Exception as e:
        logger.error(f"Error in generate_recommendations: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error occurred while generating dynamic recommendations"
        )

@router.put("/{id}", response_model=RecommendationResponse)
def update_recommendation_status(
    id: int,
    payload: RecommendationStatusUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> Any:
    """
    Updates status of a recommendation (Acknowledge/Resolve/Dismiss).
    """
    try:
        service = RecommendationService(db)
        rec = service.update_recommendation_status(recommendation_id=id, status=payload.status)
        if not rec:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recommendation with ID {id} not found."
            )
            
        from backend.repositories.admin_repository import AdminRepository
        admin_repo = AdminRepository(db)
        admin_repo.create_audit_log(
            user_id=current_user.id if current_user and not isinstance(current_user, dict) else (current_user.get("id") if isinstance(current_user, dict) else None),
            action="RECOMMENDATION_STATUS_CHANGED",
            entity_type="recommendation",
            entity_id=id,
            details=f"Recommendation {id} status changed to {payload.status}"
        )
        
        return rec
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error in update_recommendation_status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error occurred while updating recommendation status"
        )

from backend.schemas.recommendation import RecommendationHistoryResponse

@router.get("/history", response_model=List[RecommendationHistoryResponse])
def get_recommendation_history_endpoint(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> Any:
    """
    Retrieves the pipeline synchronization history.
    """
    try:
        service = RecommendationService(db)
        return service.get_recommendation_history()
    except Exception as e:
        logger.error(f"Error in get_recommendation_history_endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error occurred while fetching recommendation history logs"
        )

@router.post("/sync", status_code=status.HTTP_200_OK)
def trigger_synchronization(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> Any:
    """
    Triggers end-to-end synchronization pipeline (Warming, Batch Predictions, Recommendations, Alerts).
    """
    try:
        from backend.services.synchronization_service import SynchronizationService
        service = SynchronizationService(db)
        res = service.synchronize_pipeline()
        
        from backend.repositories.admin_repository import AdminRepository
        admin_repo = AdminRepository(db)
        admin_repo.create_audit_log(
            user_id=current_user.id if current_user and not isinstance(current_user, dict) else (current_user.get("id") if isinstance(current_user, dict) else None),
            action="PIPELINE_SYNCHRONIZED",
            details=f"Synchronized intelligence pipeline (Recs: {res.get('recommendations_count', 0)}, Alerts: {res.get('alerts_count', 0)})"
        )
        return res
    except Exception as e:
        logger.error(f"Error in trigger_synchronization: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to run end-to-end intelligence synchronization pipeline."
        )
