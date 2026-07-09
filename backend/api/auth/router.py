from dataclasses import dataclass
from datetime import datetime
from fastapi import APIRouter
from backend.models.user import UserRole

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
