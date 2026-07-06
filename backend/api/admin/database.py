import json
import io
from typing import Any, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.logging import logger
from backend.api.auth.router import get_current_user
from backend.models.user import UserRole

def require_admin(current_user=Depends(get_current_user)):
    if isinstance(current_user, dict):
        role = current_user.get("role")
        if role != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin role required to access this endpoint."
            )
        return current_user
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required to access this endpoint."
        )
    return current_user

def get_current_user_id(current_user=Depends(require_admin)) -> int:
    if isinstance(current_user, dict):
        return current_user.get("id", 0)
    return current_user.id

from backend.services.database_management_service import DatabaseManagementService, TABLE_MODELS

router = APIRouter()


# Helper to validate table name parameter
def validate_table_name(table: str):
    if table not in TABLE_MODELS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Table '{table}' is not supported. Supported tables: {list(TABLE_MODELS.keys())}"
        )


# ── 1. Stats / Dashboard ──────────────────────────────────────────────────────

@router.get("/stats")
def get_database_stats(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
) -> Any:
    """Returns total record count and last updated timestamp for each supported table."""
    try:
        service = DatabaseManagementService(db)
        admin_id = get_current_user_id(current_user)
        return service.get_dashboard_stats(performed_by_user_id=admin_id)
    except Exception as e:
        logger.error(f"Error fetching database stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve database stats."
        )


# ── 2. Export Data (Defined before dynamic {record_id} endpoints to avoid route conflicts) ─

@router.get("/{table}/export")
def export_table_records(
    table: str,
    export_format: str = Query("csv", description="Export format: 'csv' or 'excel'"),
    filters: Optional[str] = Query(None, description="JSON string of column-specific filters"),
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
) -> StreamingResponse:
    """Exports records from a table matching the provided filters."""
    validate_table_name(table)
    try:
        parsed_filters = None
        if filters:
            try:
                parsed_filters = json.loads(filters)
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid JSON format in 'filters' parameter."
                )

        service = DatabaseManagementService(db)
        file_bytes, filename = service.export_data(
            table=table,
            filters=parsed_filters,
            export_format=export_format
        )

        # Set appropriate MIME content types
        if export_format.lower() == "excel":
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        else:
            media_type = "text/csv"

        headers = {
            "Content-Disposition": f"attachment; filename={filename}",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }

        return StreamingResponse(
            io.BytesIO(file_bytes),
            media_type=media_type,
            headers=headers
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting data for {table}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export dataset."
        )


# ── 3. Bulk Upload (Defined before dynamic {record_id} endpoints to avoid route conflicts) ─

@router.post("/{table}/bulk-upload")
async def bulk_upload_records(
    table: str,
    preview: bool = Query(False),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
) -> Any:
    """
    Parses, validates, previews, and imports CSV/Excel datasets.
    Restricted to ADMIN users. Skips invalid rows and returns row-level error reporting.
    """
    validate_table_name(table)
    try:
        file_bytes = await file.read()
        service = DatabaseManagementService(db)
        admin_id = get_current_user_id(current_user)
        
        summary = service.bulk_upload(
            table=table,
            file_bytes=file_bytes,
            filename=file.filename,
            performed_by_user_id=admin_id,
            preview=preview
        )
        return summary
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Error in bulk upload for {table}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk upload failed: {str(e)}"
        )


# ── 4. Read / Search ──────────────────────────────────────────────────────────

@router.get("/{table}")
def list_table_records(
    table: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    q: Optional[str] = Query(None, description="Global keyword search query"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_order: str = Query("asc", description="Sort order: 'asc' or 'desc'"),
    filters: Optional[str] = Query(None, description="JSON string of column-specific filters"),
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
) -> Any:
    """Retrieves paginated, filtered, sorted, and searched records from a table."""
    validate_table_name(table)
    try:
        parsed_filters = None
        if filters:
            try:
                parsed_filters = json.loads(filters)
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid JSON format in 'filters' parameter."
                )

        service = DatabaseManagementService(db)
        result = service.list_records(
            table=table,
            page=page,
            page_size=page_size,
            search_query=q,
            sort_by=sort_by,
            sort_order=sort_order,
            filters=parsed_filters
        )
        
        # Serialize ORM objects safely
        records_serialized = []
        for rec in result["records"]:
            r_dict = {c.name: getattr(rec, c.name) for c in rec.__table__.columns}
            records_serialized.append(r_dict)
            
        return {
            "records": records_serialized,
            "total": result["total"],
            "page": result["page"],
            "page_size": result["page_size"]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing records for {table}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch records for table '{table}'."
        )


# ── 5. Read Specific Record ───────────────────────────────────────────────────

@router.get("/{table}/{record_id}")
def get_table_record(
    table: str,
    record_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
) -> Any:
    """Retrieves a single record from a table by ID."""
    validate_table_name(table)
    try:
        service = DatabaseManagementService(db)
        record = service.get_record_by_id(table, record_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Record {record_id} not found in table '{table}'."
            )
        
        r_dict = {c.name: getattr(record, c.name) for c in record.__table__.columns}
        return r_dict
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching record {record_id} in {table}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch record."
        )


# ── 6. Create Record ──────────────────────────────────────────────────────────

@router.post("/{table}", status_code=status.HTTP_201_CREATED)
def create_table_record(
    table: str,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
) -> Any:
    """Adds a new record to the specified table after validation."""
    validate_table_name(table)
    try:
        service = DatabaseManagementService(db)
        admin_id = get_current_user_id(current_user)
        record = service.create_record(table, payload, performed_by_user_id=admin_id)
        r_dict = {c.name: getattr(record, c.name) for c in record.__table__.columns}
        return r_dict
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Error creating record in {table}: {e}", exc_info=True)
        err_msg = str(e)
        if "FOREIGN KEY" in err_msg or "constraint failed" in err_msg:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Foreign key constraint failure. Check linked ID values.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create record."
        )


# ── 7. Update Record ──────────────────────────────────────────────────────────

@router.put("/{table}/{record_id}")
def update_table_record(
    table: str,
    record_id: int,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
) -> Any:
    """Edits an existing record in the specified table by ID."""
    validate_table_name(table)
    try:
        service = DatabaseManagementService(db)
        admin_id = get_current_user_id(current_user)
        record = service.update_record(table, record_id, payload, performed_by_user_id=admin_id)
        r_dict = {c.name: getattr(record, c.name) for c in record.__table__.columns}
        return r_dict
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        logger.error(f"Error updating record {record_id} in {table}: {e}", exc_info=True)
        err_msg = str(e)
        if "FOREIGN KEY" in err_msg or "constraint failed" in err_msg:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Foreign key constraint failure. Check linked ID values.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update record."
        )


# ── 8. Delete Record ──────────────────────────────────────────────────────────

@router.delete("/{table}/{record_id}")
def delete_table_record(
    table: str,
    record_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
) -> Any:
    """Deletes a record from the specified table by ID."""
    validate_table_name(table)
    try:
        service = DatabaseManagementService(db)
        admin_id = get_current_user_id(current_user)
        service.delete_record(table, record_id, performed_by_user_id=admin_id)
        return {"status": "success", "message": f"Record {record_id} deleted successfully from '{table}'."}
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        logger.error(f"Error deleting record {record_id} from {table}: {e}", exc_info=True)
        err_msg = str(e)
        if "FOREIGN KEY" in err_msg or "constraint failed" in err_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete this record because it is referenced by other tables."
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete record."
        )
