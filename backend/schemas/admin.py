from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr
from backend.models.user import UserRole


# ─── User Management Schemas ────────────────────────────────────────────────

class AdminUserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.OFFICER


class AdminUserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[UserRole] = None


class AdminUserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: UserRole
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ─── Audit Log Schemas ───────────────────────────────────────────────────────

class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    details: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AuditLogListResponse(BaseModel):
    logs: List[AuditLogResponse]
    total: int
    page: int
    page_size: int


# ─── System Health Schemas ───────────────────────────────────────────────────

class DatabaseHealthInfo(BaseModel):
    status: str
    dialect: str
    url_masked: str


class ApiStatusInfo(BaseModel):
    status: str
    version: str
    environment: str


class ServerInfo(BaseModel):
    python_version: str
    fastapi_version: str


class SystemHealthResponse(BaseModel):
    database: DatabaseHealthInfo
    tables: Dict[str, int]
    api: ApiStatusInfo
    server: ServerInfo


# ─── ML Model Status Schemas ─────────────────────────────────────────────────

class ModelStatusItem(BaseModel):
    name: str
    path: str
    status: str          # "loaded" or "missing"
    size_kb: Optional[float] = None


class ModelStatusResponse(BaseModel):
    models: List[ModelStatusItem]
    checked_at: datetime


# ─── Dataset Status Schemas ──────────────────────────────────────────────────

class DatasetTableInfo(BaseModel):
    table: str
    record_count: int


class DatasetStatusResponse(BaseModel):
    tables: List[DatasetTableInfo]
    total_records: int
    checked_at: datetime
