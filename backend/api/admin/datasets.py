from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional, Union, Any
from backend.core.database import get_db
from backend.api.admin.database import require_admin, get_current_user_id
from backend.schemas.dataset import (
    DatasetResponse,
    DatasetSwitchRequest,
    DatasetSummaryResponse,
    DatasetPreviewResponse,
    DatasetStatisticsResponse,
)
from backend.services.dataset_service import DatasetService
from backend.models.dataset import Dataset
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

@router.post("/upload", response_model=Union[DatasetResponse, List[DatasetResponse]])
async def upload_dataset_file(
    display_name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    files: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Registers and uploads a new dataset, importing crime events, criminals,
    victims, and participations. Supports single file or multiple files upload.
    """
    # Collect all files to process
    upload_files = []
    if file is not None:
        upload_files.append(file)
    if files is not None:
        upload_files.extend(files)

    if not upload_files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files uploaded. Please upload at least one CSV or Excel file."
        )

    # Verify file extensions for all uploaded files
    for f in upload_files:
        filename = f.filename
        if not (filename.lower().endswith(".csv") or filename.lower().endswith(".xlsx") or filename.lower().endswith(".xls")):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format for '{filename}'. Only CSV and Excel (.xlsx, .xls) files are supported."
            )

    try:
        service = DatasetService(db)
        admin_id = get_current_user_id(current_user)
        results = []

        for f in upload_files:
            file_bytes = await f.read()
            # If multiple files are uploaded, display name is customized
            if len(upload_files) > 1:
                # If display name was provided, suffix it
                if display_name:
                    current_display_name = f"{display_name} - {f.filename}"
                else:
                    # Clean filename as display name
                    current_display_name = f.filename.rsplit(".", 1)[0].replace("_", " ").replace("-", " ").title()
            else:
                current_display_name = display_name or f.filename.rsplit(".", 1)[0].replace("_", " ").replace("-", " ").title()

            db_dataset = service.import_dataset(
                display_name=current_display_name,
                description=description,
                file_name=f.filename,
                file_bytes=file_bytes,
                user_id=admin_id
            )
            results.append(db_dataset)

        # If a single file was uploaded, return the single response (compatibility with tests)
        if len(upload_files) == 1 and file is not None:
            return results[0]
        else:
            return results

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

@router.get("/{dataset_id}", response_model=DatasetResponse)
def get_dataset_details(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Retrieves the metadata details of a specific dataset by ID.
    """
    try:
        service = DatasetService(db)
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset with ID {dataset_id} not found."
            )
        return dataset
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching dataset {dataset_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dataset details."
        )

@router.get("/{dataset_id}/preview", response_model=DatasetPreviewResponse)
def get_dataset_preview(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Retrieves a preview of the dataset including columns, datatypes, and first 20 rows.
    """
    try:
        service = DatasetService(db)
        return service.get_dataset_preview(dataset_id)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Error previewing dataset {dataset_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate dataset preview: {str(e)}"
        )

@router.get("/{dataset_id}/statistics", response_model=DatasetStatisticsResponse)
def get_dataset_statistics(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Computes statistical analysis metrics on the dataset's file.
    """
    try:
        service = DatasetService(db)
        return service.get_dataset_statistics(dataset_id)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Error generating statistics for dataset {dataset_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compute dataset statistics: {str(e)}"
        )

