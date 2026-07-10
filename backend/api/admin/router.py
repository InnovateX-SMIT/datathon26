from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Any, Optional, List

from backend.core.database import get_db
from backend.core.logging import logger
from backend.api.auth.router import get_current_user
from backend.schemas.admin import (
    AuditLogListResponse,
    SystemHealthResponse,
    ModelStatusResponse,
    DatasetStatusResponse,
    AdminUserCreate,
    AdminUserUpdate,
    AdminUserResponse,
)
from backend.services.admin_service import AdminService

router = APIRouter()

# Include database management sub-router
from backend.api.admin.database import router as database_router
router.include_router(database_router, prefix="/database")

# Include datasets sub-router
from backend.api.admin.datasets import router as datasets_router
router.include_router(datasets_router, prefix="/datasets")

# Include models sub-router
from backend.api.admin.models import router as models_router
router.include_router(models_router, prefix="/models")




# ── Role Guard ────────────────────────────────────────────────────────────────

from backend.models.user import UserRole

def require_admin(current_user=Depends(get_current_user)):
    role = None
    if isinstance(current_user, dict):
        role = current_user.get("role")
    elif current_user:
        role = getattr(current_user, "role", None)
        if isinstance(role, UserRole):
            role = role.value
    
    if not role or str(role) != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Admin access required."
        )
    return current_user


def get_current_user_id(current_user=Depends(require_admin)) -> int:
    """Extract user ID from either ORM object or mock dict."""
    if isinstance(current_user, dict):
        return current_user.get("id", 0)
    return current_user.id

@router.get("/system/health", response_model=SystemHealthResponse)
def get_system_health(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
) -> Any:
    """Returns database health, table counts, API status, and server info."""
    try:
        service = AdminService(db)
        admin_id = get_current_user_id(current_user)
        return service.get_system_health(performed_by_user_id=admin_id)
    except Exception as e:
        logger.error(f"Error in get_system_health: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to compute system health.")


@router.get("/system/models", response_model=ModelStatusResponse)
def get_model_status(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
) -> Any:
    """Returns the on-disk status of all ML model files."""
    try:
        service = AdminService(db)
        return service.get_model_status()
    except Exception as e:
        logger.error(f"Error in get_model_status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to check model status.")


# ── Audit Logs Endpoint ───────────────────────────────────────────────────────

from fastapi.responses import StreamingResponse
import io
import csv
import pandas as pd

@router.get("/audit-logs", response_model=AuditLogListResponse)
def get_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    action: Optional[str] = Query(None, description="Filter by action type"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    module: Optional[str] = Query(None, description="Filter by module"),
    search: Optional[str] = Query(None, description="Search term"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    sort_by: Optional[str] = Query(None, description="Sort column"),
    sort_order: Optional[str] = Query(None, description="Sort order: 'asc' or 'desc'"),
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
) -> Any:
    """Returns paginated audit logs with search, filters, and sorting."""
    try:
        service = AdminService(db)
        admin_id = get_current_user_id(current_user)
        return service.get_audit_logs(
            page=page,
            page_size=page_size,
            action_filter=action,
            user_id_filter=user_id,
            module_filter=module,
            search_filter=search,
            start_date=start_date,
            end_date=end_date,
            sort_by=sort_by,
            sort_order=sort_order,
            performed_by_user_id=admin_id
        )
    except Exception as e:
        logger.error(f"Error in get_audit_logs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve audit logs.")

@router.get("/audit-logs/export")
def export_audit_logs(
    action: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None),
    module: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    sort_by: Optional[str] = Query(None),
    sort_order: Optional[str] = Query(None),
    export_format: str = Query("csv", description="Format: 'csv', 'excel', or 'pdf'"),
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
) -> StreamingResponse:
    """Exports filtered audit logs as CSV, Excel, or PDF."""
    try:
        service = AdminService(db)
        # Pull up to 50000 matching records for the report
        result = service.get_audit_logs(
            page=1,
            page_size=50000,
            action_filter=action,
            user_id_filter=user_id,
            module_filter=module,
            search_filter=search,
            start_date=start_date,
            end_date=end_date,
            sort_by=sort_by,
            sort_order=sort_order
        )
        logs = result.get("logs", [])
        filters_desc = f"Filters: Action={action or 'All'}, UserID={user_id or 'All'}, Module={module or 'All'}, Search={search or 'None'}"
        
        if export_format == "excel":
            data_list = []
            for log in logs:
                data_list.append({
                    "ID": log.id,
                    "Timestamp": log.created_at.strftime("%Y-%m-%d %H:%M:%S") if log.created_at else "N/A",
                    "User ID": log.user_id or "System",
                    "User Name": log.user_name or "N/A",
                    "Role": log.user_role or "N/A",
                    "Module": log.module or "N/A",
                    "Action": log.action,
                    "Entity Type": log.entity_type or "N/A",
                    "Entity ID": log.entity_id or "N/A",
                    "Details": log.details or "N/A",
                    "IP Address": log.ip_address or "N/A",
                    "API Endpoint": log.api_endpoint or "N/A",
                    "Status": log.response_status or "N/A"
                })
            df = pd.DataFrame(data_list)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Audit Logs")
            output.seek(0)
            return StreamingResponse(
                output,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": "attachment; filename=audit_logs_export.xlsx"}
            )
            
        elif export_format == "pdf":
            # Generate a custom Courier-based PDF table report
            pdf = []
            pdf.append(b"%PDF-1.4")
            pdf.append(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj")
            pdf.append(b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj")
            
            stream_content = []
            stream_content.append(b"BT /F1 9 Tf 30 800 Td 12 TL")
            stream_content.append(b"(SYSTEM AUDIT LOGS TRAIL REPORT) Tj T*")
            stream_content.append(f"({filters_desc}) Tj T*".encode("utf-8"))
            stream_content.append(b"() Tj T*")
            stream_content.append(b"(TIMESTAMP           | ACTION               | USER                 | DETAILS) Tj T*")
            stream_content.append(b"(--------------------------------------------------------------------------------) Tj T*")
            
            for log in logs[:50]:
                ts = log.created_at.strftime("%Y-%m-%d %H:%M") if log.created_at else "N/A"
                act = (log.action[:18] + "..") if len(log.action) > 20 else log.action.ljust(20)
                usr = (log.user_name[:18] + "..") if log.user_name and len(log.user_name) > 20 else (log.user_name or "System").ljust(20)
                det = (log.details[:30] + "..") if log.details and len(log.details) > 32 else (log.details or "N/A")
                det_escaped = det.replace("(", "\\(").replace(")", "\\)")
                log_line = f"{ts.ljust(20)} | {act.ljust(20)} | {usr.ljust(20)} | {det_escaped}"
                stream_content.append(f"({log_line}) Tj T*".encode("utf-8"))
                
            stream_content.append(b"ET")
            stream_bytes = b"\n".join(stream_content)
            
            pdf.append(b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj")
            pdf.append(f"4 0 obj\n<< /Length {len(stream_bytes)} >>\nstream\n".encode("utf-8") + stream_bytes + b"\nendstream\nendobj")
            pdf.append(b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>\nendobj")
            pdf.append(b"xref\n0 6\n0000000000 65535 f \n")
            pdf.append(b"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n120\n%%EOF")
            
            output = io.BytesIO(b"\n".join(pdf))
            return StreamingResponse(
                output,
                media_type="application/pdf",
                headers={"Content-Disposition": "attachment; filename=audit_logs_report.pdf"}
            )
            
        else: # csv
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["ID", "Timestamp", "User ID", "User Name", "Role", "Module", "Action", "Entity Type", "Entity ID", "Details", "IP Address", "API Endpoint", "Status"])
            for log in logs:
                writer.writerow([
                    log.id,
                    log.created_at.strftime("%Y-%m-%d %H:%M:%S") if log.created_at else "N/A",
                    log.user_id or "System",
                    log.user_name or "N/A",
                    log.user_role or "N/A",
                    log.module or "N/A",
                    log.action,
                    log.entity_type or "N/A",
                    log.entity_id or "N/A",
                    log.details or "N/A",
                    log.ip_address or "N/A",
                    log.api_endpoint or "N/A",
                    log.response_status or "N/A"
                ])
            output.seek(0)
            return StreamingResponse(
                io.BytesIO(output.getvalue().encode("utf-8")),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=audit_logs_export.csv"}
            )
    except Exception as e:
        logger.error(f"Error exporting audit logs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to export audit logs.")


# ── Dataset Management Endpoint ───────────────────────────────────────────────

@router.get("/dataset/status", response_model=DatasetStatusResponse)
def get_dataset_status(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
) -> Any:
    """Returns record counts across all platform database tables."""
    try:
        service = AdminService(db)
        admin_id = get_current_user_id(current_user)
        return service.get_dataset_status(performed_by_user_id=admin_id)
    except Exception as e:
        logger.error(f"Error in get_dataset_status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve dataset status.")

@router.post("/dataset/refresh-models")
def refresh_models(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
) -> Any:
    """Clears the ML model cache, forcing a disk reload on the next prediction request."""
    try:
        service = AdminService(db)
        admin_id = get_current_user_id(current_user)
        return service.refresh_models(performed_by_user_id=admin_id)
    except Exception as e:
        logger.error(f"Error in refresh_models: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to refresh models.")

@router.post("/dataset/reimport")
def reimport_data(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
) -> Any:
    """Safely truncates and re-seeds crime and geospatial datasets."""
    try:
        service = AdminService(db)
        admin_id = get_current_user_id(current_user)
        return service.trigger_safe_reimport(performed_by_user_id=admin_id)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error in reimport_data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to reimport data.")

@router.post("/dataset/optimize")
def optimize_database_endpoint(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
) -> Any:
    """Rebuilds database indexes and shrinks database file size (VACUUM)."""
    try:
        service = AdminService(db)
        admin_id = get_current_user_id(current_user)
        return service.optimize_indexes(performed_by_user_id=admin_id)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error in optimize_database_endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to optimize database.")

@router.post("/dataset/backup")
def backup_database_endpoint(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
) -> Any:
    """Creates a backup file copy of the current SQLite database."""
    try:
        service = AdminService(db)
        admin_id = get_current_user_id(current_user)
        return service.backup_database(performed_by_user_id=admin_id)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error in backup_database_endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to backup database.")

# ── User Management Endpoints ─────────────────────────────────────────────────

@router.get("/users", response_model=List[AdminUserResponse])
def get_users(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
) -> Any:
    """Returns all registered users in the database."""
    try:
        service = AdminService(db)
        return service.list_users()
    except Exception as e:
        logger.error(f"Error in get_users: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve users.")

@router.post("/users", response_model=AdminUserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: AdminUserCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
) -> Any:
    """Creates a new user profile with password hashing and audit logging."""
    try:
        service = AdminService(db)
        admin_id = get_current_user_id(current_user)
        return service.create_user(payload, performed_by_user_id=admin_id)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(ve))
    except Exception as e:
        logger.error(f"Error in create_user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create user.")

@router.get("/users/{user_id}", response_model=AdminUserResponse)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
) -> Any:
    """Retrieves a single user's profile by ID."""
    try:
        service = AdminService(db)
        return service.get_user_by_id(user_id)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error(f"Error in get_user_by_id: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve user.")

@router.put("/users/{user_id}", response_model=AdminUserResponse)
def update_user(
    user_id: int,
    payload: AdminUserUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
) -> Any:
    """Updates name and/or role of a user."""
    try:
        service = AdminService(db)
        admin_id = get_current_user_id(current_user)
        return service.update_user(user_id, payload, performed_by_user_id=admin_id)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error(f"Error in update_user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update user.")

@router.put("/users/{user_id}/deactivate", response_model=AdminUserResponse)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
) -> Any:
    """Deactivates a user account (cannot deactivate self)."""
    try:
        service = AdminService(db)
        admin_id = get_current_user_id(current_user)
        return service.deactivate_user(user_id, performed_by_user_id=admin_id)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error in deactivate_user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to deactivate user.")

@router.put("/users/{user_id}/activate", response_model=AdminUserResponse)
def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
) -> Any:
    """Re-activates a deactivated user account."""
    try:
        service = AdminService(db)
        admin_id = get_current_user_id(current_user)
        return service.activate_user(user_id, performed_by_user_id=admin_id)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error in activate_user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to activate user.")
