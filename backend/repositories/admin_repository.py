from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, text

from backend.models.user import User, UserRole
from backend.models.audit_log import AuditLog


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
        details: Optional[str] = None
    ) -> AuditLog:
        log = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def get_audit_logs(
        self,
        skip: int = 0,
        limit: int = 50,
        action_filter: Optional[str] = None
    ) -> List[AuditLog]:
        query = self.db.query(AuditLog)
        if action_filter:
            query = query.filter(AuditLog.action == action_filter)
        return query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()

    def get_audit_log_count(self, action_filter: Optional[str] = None) -> int:
        query = self.db.query(func.count(AuditLog.id))
        if action_filter:
            query = query.filter(AuditLog.action == action_filter)
        return query.scalar() or 0

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
        ]
        counts: Dict[str, int] = {}
        for table in tables:
            try:
                result = self.db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                counts[table] = result.scalar() or 0
            except Exception:
                counts[table] = 0
        return counts
