from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.core.database import get_db
from backend.api.admin.database import require_admin, get_current_user_id
from backend.schemas.dataset import DatasetResponse, DatasetSwitchRequest, DatasetSummaryResponse
from backend.services.dataset_service import DatasetService
from backend.core.logging import logger

router = APIRouter()

@router.get("/", response_model=List[DatasetResponse])
def get_datasets(
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Lists all registered datasets in the Dataset Registry.
    """
    try:
        service = DatasetService(db)
        return service.list_datasets()
    except Exception as e:
        logger.error(f"Error listing datasets: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve registered datasets."
        )

@router.post("/upload", response_model=DatasetResponse)
async def upload_dataset_file(
    display_name: str = Form(...),
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Registers and uploads a new dataset, importing crime events, criminals,
    victims, and participations.
    """
    # Verify file extension
    filename = file.filename
    if not (filename.lower().endswith(".csv") or filename.lower().endswith(".xlsx") or filename.lower().endswith(".xls")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Only CSV and Excel (.xlsx, .xls) files are supported."
        )

    try:
        file_bytes = await file.read()
        service = DatasetService(db)
        admin_id = get_current_user_id(current_user)
        
        db_dataset = service.import_dataset(
            display_name=display_name,
            description=description,
            file_name=filename,
            file_bytes=file_bytes,
            user_id=admin_id
        )
        return db_dataset
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Failed to upload and import dataset: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process dataset file: {str(e)}"
        )

@router.post("/activate", response_model=DatasetResponse)
def activate_dataset(
    payload: DatasetSwitchRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Switches the active dataset of the platform.
    """
    try:
        service = DatasetService(db)
        # Clear graph cache on switch
        from backend.services.network_analytics_service import NetworkAnalyticsService
        # Set new active dataset
        dataset = service.activate_dataset(payload.dataset_id)
        
        # Explicitly invalidate network analytics caches
        NetworkAnalyticsService._cached_graph = None
        NetworkAnalyticsService._cached_dataset_id = None
        NetworkAnalyticsService._cached_centrality = None
        NetworkAnalyticsService._cached_clusters = None
        NetworkAnalyticsService._cached_associations = None
        NetworkAnalyticsService._cached_location_intel = None
        
        return dataset
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Error activating dataset {payload.dataset_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to switch active dataset."
        )

@router.delete("/{dataset_id}", status_code=status.HTTP_200_OK)
def delete_dataset_record(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Deletes the dataset and all associated records (crimes, criminals, victims, participations) via cascade deletion.
    """
    try:
        service = DatasetService(db)
        service.delete_dataset(dataset_id)
        return {"detail": "Dataset deleted successfully."}
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Error deleting dataset {dataset_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete dataset."
        )

@router.get("/{dataset_id}/summary", response_model=DatasetSummaryResponse)
def get_dataset_summary_metrics(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Exposes statistical summary metrics of a dataset for administration overview.
    """
    try:
        service = DatasetService(db)
        return service.get_dataset_summary(dataset_id)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Error compiling summary for dataset {dataset_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to compile dataset summary statistics."
        )
