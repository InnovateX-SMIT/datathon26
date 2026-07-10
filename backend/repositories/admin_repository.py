from typing import Optional, List, Dict
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, text
import threading

from backend.models.user import User, UserRole
from backend.models.audit_log import AuditLog
from backend.core.database import SessionLocal
from backend.core.config import settings

def _write_audit_log_bg(
    user_id: Optional[int],
    action: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    details: Optional[str] = None,
    module: Optional[str] = None,
    previous_value: Optional[str] = None,
    new_value: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    request_method: Optional[str] = None,
    api_endpoint: Optional[str] = None,
    response_status: Optional[int] = None,
    db_session: Optional[Session] = None
):
    close_db = False
    db = db_session
    if db is None:
        db = SessionLocal()
        close_db = True
    try:
        user_name = None
        user_role = None
        if user_id:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user_name = user.email
                user_role = user.role.value if hasattr(user.role, "value") else str(user.role)
        
        log = AuditLog(
            user_id=user_id,
            user_name=user_name,
            user_role=user_role,
            action=action,
            action_type=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            module=module or entity_type or "system",
            previous_value=previous_value,
            new_value=new_value,
            ip_address=ip_address,
            user_agent=user_agent,
            request_method=request_method,
            api_endpoint=api_endpoint,
            response_status=response_status
        )
        db.add(log)
        db.commit()
    except Exception as e:
        import logging
        logging.getLogger("fastapi").error(f"Error in _write_audit_log_bg: {e}")
    finally:
        if close_db:
            db.close()



class AdminRepository:
    def __init__(self, db: Session):
        self.db = db

    # ── User Management ──────────────────────────────────────────────────────

    def get_all_users(self) -> List[User]:
        return self.db.query(User).order_by(User.created_at.desc()).all()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def create_user(
        self,
        name: str,
        email: str,
        password_hash: str,
        role: UserRole
    ) -> User:
        user = User(
            name=name,
            email=email,
            password_hash=password_hash,
            role=role,
            status="active"
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_user(
        self,
        user_id: int,
        name: Optional[str],
        role: Optional[UserRole]
    ) -> Optional[User]:
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        if name is not None:
            user.name = name
        if role is not None:
            user.role = role
        self.db.commit()
        self.db.refresh(user)
        return user

    def set_user_status(self, user_id: int, status: str) -> Optional[User]:
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        user.status = status
        self.db.commit()
        self.db.refresh(user)
        return user

    # ── Audit Logs ───────────────────────────────────────────────────────────

    def create_audit_log(
        self,
        user_id: Optional[int],
        action: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        details: Optional[str] = None,
        module: Optional[str] = None,
        previous_value: Optional[str] = None,
        new_value: Optional[str] = None,
        response_status: Optional[int] = None
    ) -> AuditLog:
        try:
            from backend.app.main import request_var
            request = request_var.get()
        except Exception:
            request = None

        ip_address = None
        user_agent = None
        request_method = None
        api_endpoint = None
        if request:
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")
            request_method = request.method
            api_endpoint = request.url.path

        # Spawn daemon thread to write to database asynchronously, or run synchronously in tests
        kwargs = {
            "user_id": user_id,
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "details": details,
            "module": module or entity_type,
            "previous_value": previous_value,
            "new_value": new_value,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "request_method": request_method,
            "api_endpoint": api_endpoint,
            "response_status": response_status
        }
        if settings.ENVIRONMENT == "test":
            _write_audit_log_bg(**kwargs, db_session=self.db)
        else:
            threading.Thread(
                target=_write_audit_log_bg,
                kwargs=kwargs,
                daemon=True
            ).start()

        return AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details
        )

    def get_audit_logs(
        self,
        skip: int = 0,
        limit: int = 50,
        action_filter: Optional[str] = None,
        user_id_filter: Optional[int] = None,
        module_filter: Optional[str] = None,
        search_filter: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None
    ) -> List[AuditLog]:
        query = self.db.query(AuditLog)
        query = self._apply_audit_filters(
            query, action_filter, user_id_filter, module_filter, search_filter, start_date, end_date
        )

        sort_col = AuditLog.created_at
        if sort_by and hasattr(AuditLog, sort_by):
            sort_col = getattr(AuditLog, sort_by)

        if sort_order == "asc":
            query = query.order_by(sort_col.asc())
        else:
            query = query.order_by(sort_col.desc())

        return query.offset(skip).limit(limit).all()

    def get_audit_log_count(
        self,
        action_filter: Optional[str] = None,
        user_id_filter: Optional[int] = None,
        module_filter: Optional[str] = None,
        search_filter: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> int:
        query = self.db.query(func.count(AuditLog.id))
        query = self._apply_audit_filters(
            query, action_filter, user_id_filter, module_filter, search_filter, start_date, end_date
        )
        return query.scalar() or 0

    def _apply_audit_filters(
        self,
        query,
        action_filter: Optional[str] = None,
        user_id_filter: Optional[int] = None,
        module_filter: Optional[str] = None,
        search_filter: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ):
        if action_filter and action_filter != "ALL":
            query = query.filter(AuditLog.action == action_filter)
        if user_id_filter is not None:
            query = query.filter(AuditLog.user_id == user_id_filter)
        if module_filter and module_filter != "ALL":
            query = query.filter(AuditLog.module == module_filter)
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)
        if search_filter:
            pat = f"%{search_filter}%"
            query = query.filter(
                (AuditLog.details.ilike(pat)) |
                (AuditLog.action.ilike(pat)) |
                (AuditLog.user_name.ilike(pat)) |
                (AuditLog.module.ilike(pat)) |
                (AuditLog.ip_address.ilike(pat)) |
                (AuditLog.api_endpoint.ilike(pat))
            )
        return query


    # ── System / Dataset ─────────────────────────────────────────────────────

    def get_table_record_counts(self) -> Dict[str, int]:
        tables = [
            "users",
            "crime_events",
            "criminals",
            "victims",
            "locations",
            "police_stations",
            "predictions",
            "alerts",
            "recommendations",
            "resource_allocations",
            "reports",
            "audit_logs",
            # Normalized tables
            "case_master",
            "accused",
            "victim",
            "complainant_details",
            "arrest_surrender",
            "chargesheet_details",
            "act",
            "section",
            "crime_head",
            "crime_sub_head",
            "district",
            "unit"
        ]
        counts: Dict[str, int] = {}
        for table in tables:
            try:
                result = self.db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                counts[table] = result.scalar() or 0
            except Exception:
                counts[table] = 0
        return counts
