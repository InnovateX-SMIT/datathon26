from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Any, Optional

from backend.core.database import get_db
from backend.core.logging import logger
from backend.api.auth.router import get_current_user
from backend.models.user import User, UserRole
from backend.schemas.admin import (
    AdminUserCreate,
    AdminUserUpdate,
    AdminUserResponse,
    AuditLogListResponse,
    SystemHealthResponse,
    ModelStatusResponse,
    DatasetStatusResponse,
)
from backend.services.admin_service import AdminService

router = APIRouter()


# ── Role Guard ────────────────────────────────────────────────────────────────

def require_admin(current_user=Depends(get_current_user)):
    """
    Dependency that enforces ADMIN role.
    Returns current_user if admin, raises 403 otherwise.
    Handles both ORM User objects and test mock dicts.
    """
    if isinstance(current_user, dict):
        role = current_user.get("role")
        if role != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin role required to access this endpoint."
            )
        return current_user
    # ORM User object
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required to access this endpoint."
        )
    return current_user


def get_current_user_id(current_user=Depends(require_admin)) -> int:
    """Extract user ID from either ORM object or mock dict."""
    if isinstance(current_user, dict):
        return current_user.get("id", 0)
    return current_user.id


# ── User Management Endpoints ─────────────────────────────────────────────────

@router.get("/users", response_model=List[AdminUserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
) -> Any:
    """Lists all platform users. Admin only."""
    try:
        service = AdminService(db)
        return service.get_all_users()
    except Exception as e:
        logger.error(f"Error in get_all_users: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve users.")


@router.post("/users", response_model=AdminUserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: AdminUserCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
) -> Any:
    """Creates a new platform user. Admin only."""
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
    """Gets a single user by ID. Admin only."""
    try:
        service = AdminService(db)
        user = service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found.")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_user_by_id: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch user.")


@router.put("/users/{user_id}", response_model=AdminUserResponse)
def update_user(
    user_id: int,
    payload: AdminUserUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
) -> Any:
    """Updates a user's name or role. Admin only."""
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
    """Deactivates a user. Admin only. Cannot deactivate self."""
    try:
        service = AdminService(db)
        admin_id = get_current_user_id(current_user)
        return service.deactivate_user(user_id, performed_by_user_id=admin_id)
    except ValueError as ve:
        err = str(ve)
        code = 400 if "own account" in err or "already inactive" in err else 404
        raise HTTPException(status_code=code, detail=err)
    except Exception as e:
        logger.error(f"Error in deactivate_user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to deactivate user.")


@router.put("/users/{user_id}/activate", response_model=AdminUserResponse)
def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
) -> Any:
    """Reactivates a deactivated user. Admin only."""
    try:
        service = AdminService(db)
        admin_id = get_current_user_id(current_user)
        return service.activate_user(user_id, performed_by_user_id=admin_id)
    except ValueError as ve:
        err = str(ve)
        code = 400 if "already active" in err else 404
        raise HTTPException(status_code=code, detail=err)
    except Exception as e:
        logger.error(f"Error in activate_user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to activate user.")


# ── System Monitoring Endpoints ───────────────────────────────────────────────

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
