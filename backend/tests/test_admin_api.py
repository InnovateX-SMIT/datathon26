import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.core.database import Base, get_db
from backend.api.auth.router import get_current_user
from backend.app.main import app
from backend.models.user import User, UserRole
from backend.models.audit_log import AuditLog

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


# ── Client fixtures ───────────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def client_as_admin(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def mock_admin_user():
        return {"id": 1, "email": "admin@police.gov.in", "role": "ADMIN", "status": "active"}

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = mock_admin_user
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client_as_officer(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def mock_officer_user():
        return {"id": 2, "email": "officer@police.gov.in", "role": "OFFICER", "status": "active"}

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = mock_officer_user
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# ── Helper: Seed a user in DB ─────────────────────────────────────────────────

def seed_user(db, email="seeded@police.gov.in", role=UserRole.OFFICER, status="active") -> User:
    from backend.core.security import get_password_hash
    user = User(
        name="Seeded User",
        email=email,
        password_hash=get_password_hash("password"),
        role=role,
        status=status
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_get_users_requires_admin(client_as_officer):
    response = client_as_officer.get("/api/v1/admin/users")
    assert response.status_code == 403


def test_get_users_as_admin(client_as_admin, db_session):
    seed_user(db_session)
    response = client_as_admin.get("/api/v1/admin/users")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_user_api(client_as_admin):
    payload = {
        "name": "New Officer",
        "email": "newofficer@police.gov.in",
        "password": "secret123",
        "role": "OFFICER"
    }
    response = client_as_admin.post("/api/v1/admin/users", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["email"] == "newofficer@police.gov.in"
    assert data["role"] == "OFFICER"
    assert data["status"] == "active"


def test_create_user_duplicate_email(client_as_admin, db_session):
    seed_user(db_session, email="test@test.com")
    payload = {
        "name": "Dup",
        "email": "test@test.com",
        "password": "secret",
        "role": "OFFICER"
    }
    response = client_as_admin.post("/api/v1/admin/users", json=payload)
    assert response.status_code == 409


def test_get_user_by_id(client_as_admin, db_session):
    user = seed_user(db_session)
    response = client_as_admin.get(f"/api/v1/admin/users/{user.id}")
    assert response.status_code == 200
    assert response.json()["id"] == user.id


def test_get_user_not_found(client_as_admin):
    response = client_as_admin.get("/api/v1/admin/users/99999")
    assert response.status_code == 404


def test_update_user_api(client_as_admin, db_session):
    user = seed_user(db_session)
    response = client_as_admin.put(
        f"/api/v1/admin/users/{user.id}",
        json={"name": "New Name"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"


def test_deactivate_user_api(client_as_admin, db_session):
    # mock_admin_user has id=1; seed a dummy user first so target gets id=2
    seed_user(db_session, email="dummy@test.com")
    target = seed_user(db_session, email="target@test.com")
    response = client_as_admin.put(f"/api/v1/admin/users/{target.id}/deactivate")
    assert response.status_code == 200
    assert response.json()["status"] == "inactive"


def test_cannot_deactivate_self(client_as_admin, db_session):
    # The mock admin has id=1; seed user with id=1 by inserting a real user
    from backend.core.security import get_password_hash
    admin = User(
        name="Admin",
        email="admin@police.gov.in",
        password_hash=get_password_hash("pass"),
        role=UserRole.ADMIN,
        status="active"
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)

    response = client_as_admin.put(f"/api/v1/admin/users/{admin.id}/deactivate")
    assert response.status_code == 400


def test_activate_user_api(client_as_admin, db_session):
    user = seed_user(db_session, email="inactive@test.com", status="inactive")
    response = client_as_admin.put(f"/api/v1/admin/users/{user.id}/activate")
    assert response.status_code == 200
    assert response.json()["status"] == "active"


def test_system_health_api(client_as_admin):
    response = client_as_admin.get("/api/v1/admin/system/health")
    assert response.status_code == 200
    data = response.json()
    assert "database" in data
    assert "tables" in data
    assert "api" in data


def test_model_status_api(client_as_admin):
    response = client_as_admin.get("/api/v1/admin/system/models")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert isinstance(data["models"], list)
    assert len(data["models"]) == 4


def test_audit_logs_api(client_as_admin):
    response = client_as_admin.get("/api/v1/admin/audit-logs")
    assert response.status_code == 200
    data = response.json()
    assert "logs" in data
    assert "total" in data
    assert "page" in data


def test_audit_logs_with_filter(client_as_admin, db_session):
    # Seed an audit log directly
    log = AuditLog(
        user_id=1,
        action="USER_CREATED",
        entity_type="user",
        entity_id=42,
        details='{"email": "x@x.com"}'
    )
    db_session.add(log)
    db_session.commit()

    response = client_as_admin.get("/api/v1/admin/audit-logs?action=USER_CREATED")
    assert response.status_code == 200
    data = response.json()
    for entry in data["logs"]:
        assert entry["action"] == "USER_CREATED"


def test_dataset_status_api(client_as_admin):
    response = client_as_admin.get("/api/v1/admin/dataset/status")
    assert response.status_code == 200
    data = response.json()
    assert "tables" in data
    assert "total_records" in data


def test_non_admin_cannot_access_system_health(client_as_officer):
    response = client_as_officer.get("/api/v1/admin/system/health")
    assert response.status_code == 403
