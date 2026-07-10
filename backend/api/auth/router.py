from dataclasses import dataclass
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from backend.models.user import User, UserRole
from backend.core.database import get_db

router = APIRouter()

@dataclass(frozen=True)
class PublicUser:
    id: int = 0
    name: str = "Public Analyst"
    email: str = "public@crimenexus-ai.local"
    role: UserRole = UserRole.ADMIN
    status: str = "active"
    created_at: datetime = datetime(2026, 1, 1)
    updated_at: datetime = datetime(2026, 1, 1)


def get_current_user() -> PublicUser:
    """Public deployment principal used only for audit attribution after auth removal."""
    return PublicUser()

@router.post("/login")
def simulated_login(
    email: str = Body(..., embed=True),
    password: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    # Simulated auth validation
    user = db.query(User).filter(User.email == email).first()
    from backend.repositories.admin_repository import AdminRepository
    admin_repo = AdminRepository(db)
    
    if not user:
        # Log Failed Login
        admin_repo.create_audit_log(
            user_id=None,
            action="FAILED_LOGIN_ATTEMPT",
            entity_type="user",
            details=f"Failed login attempt for email: {email}"
        )
        raise HTTPException(status_code=400, detail="Invalid email or password.")
        
    if password == "invalid_pass":
        admin_repo.create_audit_log(
            user_id=user.id,
            action="FAILED_LOGIN_ATTEMPT",
            entity_type="user",
            entity_id=user.id,
            details=f"Incorrect password for user {email}"
        )
        raise HTTPException(status_code=400, detail="Invalid password.")

    # Log Success Login
    admin_repo.create_audit_log(
        user_id=user.id,
        action="LOGIN_SUCCESS",
        entity_type="user",
        entity_id=user.id,
        details=f"User {email} logged in successfully."
    )
    return {"success": True, "token": "simulated-jwt-token", "user": {"id": user.id, "email": user.email, "role": str(user.role)}}

@router.post("/logout")
def simulated_logout(
    user_id: int = Query(..., description="User ID logging out"),
    db: Session = Depends(get_db)
):
    from backend.repositories.admin_repository import AdminRepository
    admin_repo = AdminRepository(db)
    admin_repo.create_audit_log(
        user_id=user_id,
        action="LOGOUT",
        entity_type="user",
        entity_id=user_id,
        details=f"User ID {user_id} logged out."
    )
    return {"success": True, "message": "Logged out successfully."}

@router.post("/password-change")
def simulated_password_change(
    user_id: int = Body(..., embed=True),
    old_password: str = Body(..., embed=True),
    new_password: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    from backend.repositories.admin_repository import AdminRepository
    admin_repo = AdminRepository(db)
    # Log password change
    admin_repo.create_audit_log(
        user_id=user_id,
        action="PASSWORD_CHANGED",
        entity_type="user",
        entity_id=user_id,
        details=f"User ID {user_id} changed their password."
    )
    return {"success": True, "message": "Password changed successfully."}

@router.post("/profile-update")
def simulated_profile_update(
    user_id: int = Body(..., embed=True),
    name: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    from backend.repositories.admin_repository import AdminRepository
    admin_repo = AdminRepository(db)
    user = db.query(User).filter(User.id == user_id).first()
    old_name = user.name if user else "Unknown"
    
    if user:
        user.name = name
        db.commit()
        
    admin_repo.create_audit_log(
        user_id=user_id,
        action="PROFILE_UPDATED",
        entity_type="user",
        entity_id=user_id,
        details=f"User ID {user_id} updated profile name from '{old_name}' to '{name}'"
    )
    return {"success": True, "message": "Profile updated successfully."}
