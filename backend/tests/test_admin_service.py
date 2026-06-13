import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.core.database import Base

# All models must be imported so metadata is populated
from backend.models.user import User, UserRole
from backend.models.audit_log import AuditLog
from backend.models.alert import Alert
from backend.models.prediction import Prediction
from backend.models.recommendation import Recommendation, ResourceAllocation
from backend.models.location import Location
from backend.models.crime import CrimeEvent
from backend.models.report import Report

from backend.services.admin_service import AdminService
from backend.schemas.admin import AdminUserCreate, AdminUserUpdate

# ── In-memory SQLite setup ────────────────────────────────────────────────────

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


# ── Helper ────────────────────────────────────────────────────────────────────

def make_admin_user(db, email="admin@test.com") -> User:
    from backend.core.security import get_password_hash
    user = User(
        name="Admin",
        email=email,
        password_hash=get_password_hash("password"),
        role=UserRole.ADMIN,
        status="active"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_create_user_success(db_session):
    admin = make_admin_user(db_session)
    service = AdminService(db_session)

    payload = AdminUserCreate(
        name="Officer Singh",
        email="singh@police.gov.in",
        password="pass123",
        role=UserRole.OFFICER
    )
    user = service.create_user(payload, performed_by_user_id=admin.id)

    assert user is not None
    assert user.email == "singh@police.gov.in"
    assert user.role == UserRole.OFFICER
    assert user.status == "active"

    # Audit log must be created
    log = db_session.query(AuditLog).filter(AuditLog.action == "USER_CREATED").first()
    assert log is not None
    assert log.entity_type == "user"
    assert log.entity_id == user.id


def test_create_user_duplicate_email(db_session):
    admin = make_admin_user(db_session)
    service = AdminService(db_session)

    payload = AdminUserCreate(
        name="First User",
        email="dup@police.gov.in",
        password="pass123",
        role=UserRole.OFFICER
    )
    service.create_user(payload, performed_by_user_id=admin.id)

    # Attempt duplicate
    with pytest.raises(ValueError, match="already registered"):
        service.create_user(
            AdminUserCreate(name="Second User", email="dup@police.gov.in", password="p", role=UserRole.OFFICER),
            performed_by_user_id=admin.id
        )


def test_update_user(db_session):
    admin = make_admin_user(db_session)
    service = AdminService(db_session)

    target = service.create_user(
        AdminUserCreate(name="Old Name", email="target@test.com", password="p", role=UserRole.OFFICER),
        performed_by_user_id=admin.id
    )

    updated = service.update_user(
        target.id,
        AdminUserUpdate(name="New Name"),
        performed_by_user_id=admin.id
    )

    assert updated.name == "New Name"

    log = db_session.query(AuditLog).filter(AuditLog.action == "USER_UPDATED").first()
    assert log is not None
    assert log.entity_id == target.id


def test_deactivate_user_success(db_session):
    admin = make_admin_user(db_session)
    service = AdminService(db_session)

    target = service.create_user(
        AdminUserCreate(name="Target", email="target@test.com", password="p", role=UserRole.OFFICER),
        performed_by_user_id=admin.id
    )

    result = service.deactivate_user(target.id, performed_by_user_id=admin.id)

    assert result.status == "inactive"

    log = db_session.query(AuditLog).filter(AuditLog.action == "USER_DEACTIVATED").first()
    assert log is not None


def test_cannot_deactivate_self(db_session):
    admin = make_admin_user(db_session)
    service = AdminService(db_session)

    with pytest.raises(ValueError, match="own account"):
        service.deactivate_user(admin.id, performed_by_user_id=admin.id)


def test_activate_user(db_session):
    admin = make_admin_user(db_session)
    service = AdminService(db_session)

    target = service.create_user(
        AdminUserCreate(name="Target", email="target@test.com", password="p", role=UserRole.OFFICER),
        performed_by_user_id=admin.id
    )
    service.deactivate_user(target.id, performed_by_user_id=admin.id)

    activated = service.activate_user(target.id, performed_by_user_id=admin.id)
    assert activated.status == "active"

    log = db_session.query(AuditLog).filter(AuditLog.action == "USER_ACTIVATED").first()
    assert log is not None


def test_get_system_health(db_session):
    admin = make_admin_user(db_session)
    service = AdminService(db_session)

    result = service.get_system_health(performed_by_user_id=admin.id)

    assert result["database"]["status"] == "healthy"
    assert "tables" in result
    assert isinstance(result["tables"], dict)
    assert "api" in result
    assert "server" in result


def test_get_model_status(db_session):
    service = AdminService(db_session)
    result = service.get_model_status()

    assert "models" in result
    assert isinstance(result["models"], list)
    assert len(result["models"]) == 4

    for model in result["models"]:
        assert "name" in model
        assert "path" in model
        assert "status" in model
        assert model["status"] in ("loaded", "missing")
        assert "size_kb" in model


def test_get_dataset_status(db_session):
    admin = make_admin_user(db_session)
    # Seed a second user
    from backend.core.security import get_password_hash
    u2 = User(name="U2", email="u2@test.com", password_hash=get_password_hash("p"), role=UserRole.OFFICER, status="active")
    db_session.add(u2)
    db_session.commit()

    service = AdminService(db_session)
    result = service.get_dataset_status(performed_by_user_id=admin.id)

    assert "tables" in result
    assert isinstance(result["tables"], list)
    assert result["total_records"] >= 0
    assert "checked_at" in result


def test_get_audit_logs_pagination(db_session):
    admin = make_admin_user(db_session)
    service = AdminService(db_session)

    # Create 3 users to generate 3 USER_CREATED audit log entries
    for i in range(3):
        service.create_user(
            AdminUserCreate(name=f"User{i}", email=f"user{i}@test.com", password="p", role=UserRole.OFFICER),
            performed_by_user_id=admin.id
        )

    result = service.get_audit_logs(page=1, page_size=2, performed_by_user_id=admin.id)

    assert result["total"] >= 3
    assert len(result["logs"]) == 2
    assert result["page"] == 1
    assert result["page_size"] == 2
