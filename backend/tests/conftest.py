import os
import pytest

# Set ENVIRONMENT to test to prevent background network cache warmups and database locking during test runs
os.environ["ENVIRONMENT"] = "test"

@pytest.fixture(autouse=True)
def clear_rate_limiter():
    """Clear rate limiting counters before every test to prevent cross-test rate limit starvation."""
    try:
        import backend.app.main
        backend.app.main.request_counts.clear()
    except Exception:
        pass
