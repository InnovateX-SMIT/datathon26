import os
import tempfile
import pytest

# Ensure tests run against an isolated test database
os.environ["ENVIRONMENT"] = "test"
test_db_dir = os.path.dirname(os.path.abspath(__file__))
os.environ["DATABASE_URL"] = f"sqlite:///{os.path.join(test_db_dir, 'test_crime_intel.db')}"

@pytest.fixture(autouse=True)
def clear_rate_limiter():
    """Clear rate limiting counters before every test to prevent cross-test rate limit starvation."""
    try:
        import backend.app.main
        backend.app.main.request_counts.clear()
    except Exception:
        pass
