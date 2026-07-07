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

@router.get("/audit-logs", response_model=AuditLogListResponse)
def get_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    action: Optional[str] = Query(None, description="Filter by action type"),
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
) -> Any:
    """Returns paginated audit logs. Optionally filter by action type."""
    try:
        service = AdminService(db)
        admin_id = get_current_user_id(current_user)
        return service.get_audit_logs(
            page=page,
            page_size=page_size,
            action_filter=action,
            performed_by_user_id=admin_id
        )
    except Exception as e:
        logger.error(f"Error in get_audit_logs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve audit logs.")


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
