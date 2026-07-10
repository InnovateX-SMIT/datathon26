import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.core.database import SessionLocal
from backend.models.audit_log import AuditLog
from backend.models.user import User, UserRole
from backend.models.dataset import Dataset

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_audit_logs():
    db = SessionLocal()
    db.query(AuditLog).delete()
    
    # Ensure test dataset exists and is active for reports generation to succeed
    test_ds = db.query(Dataset).filter(Dataset.id == 9999).first()
    if not test_ds:
        test_ds = Dataset(
            id=9999,
            name="test_dataset",
            original_filename="test_dataset.csv",
            display_name="Test Dataset",
            is_active=True,
            status="Ready",
            upload_status="Completed",
            schema_type="legacy_crime_intel"
        )
        db.add(test_ds)
    else:
        test_ds.is_active = True
        test_ds.status = "Ready"

    test_admin = db.query(User).filter(User.email == "admin@crimenexus.local").first()
    if not test_admin:
        from backend.core.security import get_password_hash
        admin = User(
            name="Test Administrator",
            email="admin@crimenexus.local",
            password_hash=get_password_hash("password123"),
            role=UserRole.ADMIN,
            status="active"
        )
        db.add(admin)
    db.commit()
    db.close()
    yield
    db = SessionLocal()
    db.query(AuditLog).delete()
    db.commit()
    db.close()

def test_simulated_auth_audit_logging():
    # 1. Test Login Success
    res = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@crimenexus.local", "password": "password123"}
    )
    assert res.status_code == 200
    
    import time
    time.sleep(0.1)
    
    db = SessionLocal()
    logs = db.query(AuditLog).all()
    assert len(logs) == 1
    assert logs[0].action == "LOGIN_SUCCESS"
    assert logs[0].user_name == "admin@crimenexus.local"
    assert logs[0].module == "user"

    # 2. Test Login Failure (Invalid Password)
    res_fail = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@crimenexus.local", "password": "invalid_pass"}
    )
    assert res_fail.status_code == 400
    
    time.sleep(0.1)
    logs = db.query(AuditLog).order_by(AuditLog.id.desc()).all()
    assert logs[0].action == "FAILED_LOGIN_ATTEMPT"
    
    # 3. Test Logout
    res_logout = client.post("/api/v1/auth/logout?user_id=1")
    assert res_logout.status_code == 200
    
    time.sleep(0.1)
    logs = db.query(AuditLog).order_by(AuditLog.id.desc()).all()
    assert logs[0].action == "LOGOUT"
    assert logs[0].user_id == 1
    db.close()

def test_prediction_auditing():
    payload = {
        "age": 30.0,
        "occupation": "Business",
        "caste": "General",
        "district": "Bangalore"
    }
    res = client.post("/api/v1/predictions/repeat-offender", json=payload)
    assert res.status_code in (200, 503)
    
    import time
    time.sleep(0.1)
    
    db = SessionLocal()
    logs = db.query(AuditLog).filter(AuditLog.action == "PREDICTION_REPEAT_OFFENDER").all()
    if res.status_code == 200:
        assert len(logs) == 1
        assert logs[0].entity_type == "prediction"
        assert "repeat_offender_xgb" in logs[0].details
    db.close()

def test_report_sharing_auditing():
    payload = {
        "title": "Monthly Patrol briefing",
        "report_type": "district_intelligence"
    }
    res_gen = client.post("/api/v1/reports/generate", json=payload)
    assert res_gen.status_code == 201
    report_id = res_gen.json().get("report_id")
    assert report_id is not None
    
    res_share = client.post(f"/api/v1/reports/{report_id}/share?shared_with_email=chief@agency.local")
    assert res_share.status_code == 200
    
    import time
    time.sleep(0.1)
    
    db = SessionLocal()
    logs = db.query(AuditLog).filter(AuditLog.action == "REPORT_SHARED").all()
    assert len(logs) == 1
    assert logs[0].entity_id == report_id
    assert "chief@agency.local" in logs[0].details
    db.close()

def test_audit_logs_filters_endpoint():
    db = SessionLocal()
    log1 = AuditLog(user_id=1, user_name="admin@crimenexus.local", action="USER_CREATED", module="user", details="Created user test", created_at=datetime.utcnow())
    log2 = AuditLog(user_id=1, user_name="admin@crimenexus.local", action="PREDICTION_CRIME_RISK", module="prediction", details="Run risk metrics", created_at=datetime.utcnow())
    db.add(log1)
    db.add(log2)
    db.commit()
    db.close()
    
    res = client.get("/api/v1/admin/audit-logs?module=prediction")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    assert data["logs"][0]["action"] == "PREDICTION_CRIME_RISK"
    
    res_search = client.get("/api/v1/admin/audit-logs?search=metrics")
    assert res_search.status_code == 200
    data_search = res_search.json()
    assert data_search["total"] == 1
    assert data_search["logs"][0]["action"] == "PREDICTION_CRIME_RISK"

def test_audit_logs_exports():
    db = SessionLocal()
    log1 = AuditLog(user_id=1, user_name="admin@crimenexus.local", action="USER_CREATED", module="user", details="Created user test")
    db.add(log1)
    db.commit()
    db.close()
    
    res_csv = client.get("/api/v1/admin/audit-logs/export?export_format=csv")
    assert res_csv.status_code == 200
    assert "text/csv" in res_csv.headers["content-type"]
    assert b"USER_CREATED" in res_csv.content
    
    res_xlsx = client.get("/api/v1/admin/audit-logs/export?export_format=excel")
    assert res_xlsx.status_code == 200
    assert "application/vnd.openxmlformats" in res_xlsx.headers["content-type"]
    
    res_pdf = client.get("/api/v1/admin/audit-logs/export?export_format=pdf")
    assert res_pdf.status_code == 200
    assert "application/pdf" in res_pdf.headers["content-type"]
    assert b"%PDF-1.4" in res_pdf.content
