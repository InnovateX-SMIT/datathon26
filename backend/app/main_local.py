import os
import sys

# Ensure backend package and vendor packages can be imported
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_root = os.path.dirname(current_dir)
parent_dir = os.path.dirname(backend_root)

vendor_dir = os.path.join(backend_root, "vendor")
if sys.platform.startswith("linux") and os.path.exists(vendor_dir) and vendor_dir not in sys.path:
    sys.path.insert(0, vendor_dir)

if os.path.basename(backend_root) == "backend" and os.path.exists(os.path.join(parent_dir, "backend")):
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

os.environ["ENVIRONMENT"] = "development"

# Import the original app
from backend.app.main import app
from fastapi.middleware.cors import CORSMiddleware
from backend.core.config import settings

# Explicit origins and dynamic regex support for all HTTP/HTTPS origins locally
allowed_origins = [
    "https://crimenexus.onslate.in",
    "https://crimenexus-backend-50045204017.development.catalystappsail.in",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
allowed_origins_env = os.getenv("ALLOWED_ORIGINS") or os.getenv("ALLOWED_CORS_ORIGINS")
if allowed_origins_env:
    for origin in allowed_origins_env.split(","):
        o = origin.strip().rstrip("/")
        if o and o not in allowed_origins:
            allowed_origins.append(o)

# Add CORS middleware for local run
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"^https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    # Make sure we run in development environment
    os.environ["ENVIRONMENT"] = "development"
    port = int(os.getenv("PORT") or 8000)
    print(f"Starting CrimeNexus local backend on http://localhost:{port} in {settings.ENVIRONMENT} environment...")
    uvicorn.run(app, host="0.0.0.0", port=port)
