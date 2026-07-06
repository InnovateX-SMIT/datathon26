from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Any

from backend.core.database import get_db
from backend.api.admin.database import require_admin
from backend.schemas.ml_model import (
    MLModelResponse,
    MLModelCompareRequest,
    MLModelCompareResponse,
    TrainModelRequest
)
from backend.services.ml_training_service import MLTrainingService
from backend.core.logging import logger

router = APIRouter()

@router.post("/train", response_model=MLModelResponse, status_code=status.HTTP_202_ACCEPTED)
def train_model(
    payload: TrainModelRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Triggers model training / retraining asynchronously.
    """
    try:
        service = MLTrainingService(db)
        return service.trigger_retraining(payload.model_type)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Error triggering model training: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate model training."
        )

@router.get("/history", response_model=List[MLModelResponse])
def get_model_history(
    model_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Lists the version history of all trained models.
    """
    try:
        service = MLTrainingService(db)
        return service.get_model_history(model_type)
    except Exception as e:
        logger.error(f"Error retrieving model history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve model registry history."
        )

@router.post("/rollback", response_model=MLModelResponse)
def rollback_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Rollbacks the active/production model of a specific type to an older completed version.
    """
    try:
        service = MLTrainingService(db)
        return service.rollback_model(model_id)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Error rolling back model: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to rollback model version."
        )

@router.post("/production", response_model=MLModelResponse)
def mark_production_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Marks a completed model version as the active production model.
    """
    try:
        service = MLTrainingService(db)
        return service.mark_production(model_id)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Error marking model as production: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark model as production."
        )

@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Deletes a model version from the registry and disk.
    """
    try:
        service = MLTrainingService(db)
        service.delete_model(model_id)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Error deleting model: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete model registry entry."
        )

@router.post("/compare", response_model=MLModelCompareResponse)
def compare_models(
    payload: MLModelCompareRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Compares metrics of two model versions.
    """
    try:
        service = MLTrainingService(db)
        return service.compare_models(payload.model_id_1, payload.model_id_2)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Error comparing models: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to perform model comparison."
        )

@router.get("/{model_id}/logs", response_model=str)
def get_model_logs(
    model_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Retrieves the training execution logs for a model version.
    """
    try:
        from backend.models.ml_model import MLModel
        model = db.query(MLModel).filter(MLModel.id == model_id).first()
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Model not found."
            )
        return model.training_logs or ""
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving model logs: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve training logs."
        )
