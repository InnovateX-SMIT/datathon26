from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
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
    DatasetConfigRequest,
    DatasetConfigResponse,
)
from backend.services.dataset_service import DatasetService
from backend.models.dataset import Dataset
from backend.core.logging import logger

router = APIRouter()

@router.post("/detect", response_model=dict)
async def detect_dataset_schema(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Lightweight endpoint to determine schema type by reading columns from file.
    """
    try:
        file_bytes = await file.read()
        filename = file.filename
        
        import pandas as pd
        import io
        if filename.lower().endswith((".xlsx", ".xls")):
            df = pd.read_excel(io.BytesIO(file_bytes), engine="openpyxl", nrows=1)
        elif filename.lower().endswith(".csv"):
            df = pd.read_csv(io.BytesIO(file_bytes), nrows=1)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file format.")
            
        from backend.services.fir_import_service import FIRImportService
        fir_importer = FIRImportService(db)
        schema_type = fir_importer.detect_schema_type(df.columns)
        return {"schema_type": schema_type}
    except Exception as e:
        logger.error(f"Error detecting dataset schema: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

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

@router.get("/active", response_model=List[DatasetResponse])
def get_active_datasets_endpoint(
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Retrieves all currently active datasets.
    """
    try:
        service = DatasetService(db)
        return service.get_active_datasets()
    except Exception as e:
        logger.error(f"Error fetching active datasets: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve active datasets."
        )

@router.post("/deactivate", response_model=DatasetResponse)
def deactivate_dataset_endpoint(
    payload: DatasetSwitchRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Deactivates a specific dataset by setting is_active to False.
    """
    try:
        service = DatasetService(db)
        dataset = service.deactivate_dataset(payload.dataset_id)
        # Audit Log deactivation
        try:
            admin_id = get_current_user_id(current_user)
            from backend.repositories.admin_repository import AdminRepository
            admin_repo = AdminRepository(db)
            admin_repo.create_audit_log(
                user_id=admin_id,
                action="DATASET_DEACTIVATED",
                entity_type="dataset",
                entity_id=payload.dataset_id,
                details=f"Deactivated dataset '{dataset.display_name}' (ID: {payload.dataset_id})"
            )
        except Exception as ae:
            logger.error(f"Failed to log dataset deactivation audit: {ae}")
        return dataset
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Error deactivating dataset {payload.dataset_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate dataset."
        )

@router.get("/config", response_model=DatasetConfigResponse)
def get_dataset_config_endpoint(
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Retrieves the dataset selection configuration (Maximum Active Datasets setting).
    """
    try:
        service = DatasetService(db)
        return service.get_dataset_config()
    except Exception as e:
        logger.error(f"Error fetching dataset config: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dataset configuration."
        )

@router.put("/config", response_model=DatasetConfigResponse)
def update_dataset_config_endpoint(
    payload: DatasetConfigRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Updates the dataset selection configuration (Maximum Active Datasets setting).
    """
    try:
        service = DatasetService(db)
        return service.update_dataset_config(payload.max_active_datasets)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Error updating dataset config: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update dataset configuration."
        )

@router.post("/upload", response_model=Union[DatasetResponse, List[DatasetResponse], dict, List[dict]])
async def upload_dataset_file(
    display_name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    files: Optional[List[UploadFile]] = File(None),
    preview: bool = Query(False),
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

    # Verify file extensions, sizes, and sanitize filenames
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    import os
    for f in upload_files:
        filename = f.filename
        if not (filename.lower().endswith(".csv") or filename.lower().endswith(".xlsx") or filename.lower().endswith(".xls")):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format for '{filename}'. Only CSV and Excel (.xlsx, .xls) files are supported."
            )
        
        # Enforce 50MB file limit
        try:
            f.file.seek(0, 2)
            size = f.file.tell()
            f.file.seek(0)
            if size > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File '{filename}' exceeds the maximum allowed size limit of 50MB."
                )
        except HTTPException as he:
            raise he
        except Exception as e:
            logger.error(f"Error checking file size: {e}")
            
        # Path traversal sanitization
        f.filename = os.path.basename(f.filename).replace("..", "").replace("/", "").replace("\\", "")

    try:
        service = DatasetService(db)
        admin_id = get_current_user_id(current_user)
        results = []

        for f in upload_files:
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
                file_obj=f.file,
                user_id=admin_id,
                preview=preview
            )
            results.append(db_dataset)

        # Audit dataset upload/import
        if not preview:
            try:
                import json
                from backend.repositories.admin_repository import AdminRepository
                admin_repo = AdminRepository(db)
                for res in results:
                    record_count = 0
                    if hasattr(res, "import_summary") and res.import_summary:
                        try:
                            summary_data = json.loads(res.import_summary)
                            record_count = summary_data.get("inserted_rows", 0)
                        except Exception:
                            pass
                    
                    existing_matching = db.query(Dataset).filter(
                        Dataset.display_name == res.display_name,
                        Dataset.id != res.id
                    ).first()
                    action = "DATASET_REPLACED" if existing_matching else "DATASET_IMPORTED"
                    
                    admin_repo.create_audit_log(
                        user_id=admin_id,
                        action=action,
                        entity_type="dataset",
                        entity_id=res.id,
                        details=f"Uploaded and imported dataset '{res.display_name}'. Records: {record_count}. File: {res.original_filename}"
                    )
            except Exception as ae:
                logger.error(f"Failed to log dataset upload audit: {ae}")

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
        from backend.services.network_analytics_service import NetworkAnalyticsService
        dataset = service.activate_dataset(payload.dataset_id)
        
        NetworkAnalyticsService._cached_graph = None
        NetworkAnalyticsService._cached_dataset_id = None
        NetworkAnalyticsService._cached_centrality = None
        NetworkAnalyticsService._cached_clusters = None
        NetworkAnalyticsService._cached_associations = None
        NetworkAnalyticsService._cached_location_intel = None
        
        # Audit Log Activation
        try:
            admin_id = get_current_user_id(current_user)
            from backend.repositories.admin_repository import AdminRepository
            admin_repo = AdminRepository(db)
            admin_repo.create_audit_log(
                user_id=admin_id,
                action="DATASET_ACTIVATED",
                entity_type="dataset",
                entity_id=payload.dataset_id,
                details=f"Activated dataset '{dataset.display_name}' (ID: {payload.dataset_id})"
            )
        except Exception as ae:
            logger.error(f"Failed to log dataset activation audit: {ae}")
            
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
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        ds_name = dataset.display_name if dataset else f"ID {dataset_id}"
        service.delete_dataset(dataset_id)
        # Audit Log Deletion
        try:
            admin_id = get_current_user_id(current_user)
            from backend.repositories.admin_repository import AdminRepository
            admin_repo = AdminRepository(db)
            admin_repo.create_audit_log(
                user_id=admin_id,
                action="DATASET_DELETED",
                entity_type="dataset",
                entity_id=dataset_id,
                details=f"Deleted dataset '{ds_name}' (ID: {dataset_id})"
            )
        except Exception as ae:
            logger.error(f"Failed to log dataset deletion audit: {ae}")
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

@router.delete("/{dataset_id}/permanent", status_code=status.HTTP_200_OK)
def delete_dataset_permanent_endpoint(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Hard-deletes the dataset and all associated records (cascade delete on table records & file deletion on disk).
    """
    try:
        service = DatasetService(db)
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        ds_name = dataset.display_name if dataset else f"ID {dataset_id}"
        service.delete_dataset_permanent(dataset_id)
        # Audit Log Permanent Deletion
        try:
            admin_id = get_current_user_id(current_user)
            from backend.repositories.admin_repository import AdminRepository
            admin_repo = AdminRepository(db)
            admin_repo.create_audit_log(
                user_id=admin_id,
                action="DATASET_DELETED",
                entity_type="dataset",
                entity_id=dataset_id,
                details=f"Permanently deleted dataset '{ds_name}' (ID: {dataset_id})"
            )
        except Exception as ae:
            logger.error(f"Failed to log dataset permanent deletion audit: {ae}")
        return {"detail": "Dataset and all associated records permanently deleted."}
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Error permanently deleting dataset {dataset_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to permanently delete dataset."
        )




