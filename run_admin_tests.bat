@echo off
cd /d d:\Dacathon\datathon26
echo ===== RUNNING ADMIN SERVICE TESTS =====
python -m pytest backend/tests/test_admin_service.py -v --tb=short
echo.
echo ===== RUNNING ADMIN API TESTS =====
python -m pytest backend/tests/test_admin_api.py -v --tb=short
echo.
echo ===== RUNNING ALL EXISTING TESTS (REGRESSION) =====
python -m pytest backend/tests/ -v --tb=short
pause
