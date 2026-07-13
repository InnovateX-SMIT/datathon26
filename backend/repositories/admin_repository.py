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
