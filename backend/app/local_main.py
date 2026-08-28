"""
local_main.py — Local Development Entry Point for CrimeNexus Backend
======================================================================
This file is used ONLY for local development. It MUST NOT be used for
Zoho Catalyst / AppSail deployment.

For deployment, use: backend/app/main.py (unchanged)
For local dev, run:  backend\\.venv\\Scripts\\python.exe backend/app/local_main.py

What this file does:
  1. Imports the existing FastAPI `app` from main.py (all routes, middleware,
     DB setup, lifespan — everything — are inherited unchanged).
  2. Adds CORSMiddleware for local development so that the frontend at
     http://localhost:3000 can communicate with the backend at
     http://127.0.0.1:8000.
  3. Starts uvicorn on 127.0.0.1:8000.

IMPORTANT:
  - Do NOT add routes, services, or handlers here.
  - Do NOT modify deployment logic here.
  - This file does not contain secrets.
  - The backend/.env file (gitignored) provides ENVIRONMENT=development.
"""

import os
import sys

# ---------------------------------------------------------------------------
# Ensure project root is on sys.path so "backend.*" imports work correctly
# when this script is run from the repo root.
# ---------------------------------------------------------------------------
_here = os.path.dirname(os.path.abspath(__file__))          # backend/app/
_backend_root = os.path.dirname(_here)                       # backend/
_project_root = os.path.dirname(_backend_root)               # datathon26/

if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# ---------------------------------------------------------------------------
# Import the production FastAPI app — ALL routes, middleware, DB, lifespan
# are inherited exactly as they are in main.py.
# ---------------------------------------------------------------------------
from backend.app.main import app  # noqa: E402

# ---------------------------------------------------------------------------
# Add CORS middleware for local development only.
#
# In production (Catalyst / AppSail), CORS is handled at the platform level
# (or intentionally left open via allow_origin_regex). Here we add explicit
# localhost origins so the Next.js dev server at localhost:3000 can call
# the backend at 127.0.0.1:8000 without CORS errors.
#
# app.add_middleware() can be called after app creation; FastAPI/Starlette
# builds the middleware stack lazily on first request.
# ---------------------------------------------------------------------------
from fastapi.middleware.cors import CORSMiddleware

_local_allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    # Keep production origins so staging/testing against this local server works
    "https://crimenexus.onslate.in",
    "https://crimenexus-backend-50045204017.development.catalystappsail.in",
]

# Support optional ALLOWED_ORIGINS / ALLOWED_CORS_ORIGINS env vars
_extra_origins_env = os.getenv("ALLOWED_ORIGINS") or os.getenv("ALLOWED_CORS_ORIGINS")
if _extra_origins_env:
    for _o in _extra_origins_env.split(","):
        _o = _o.strip().rstrip("/")
        if _o and _o not in _local_allowed_origins:
            _local_allowed_origins.append(_o)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_local_allowed_origins,
    allow_origin_regex=r"^https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Start the local uvicorn server
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT") or 8000)
    print(f"\n{'='*60}")
    print("  CrimeNexus - LOCAL DEVELOPMENT SERVER")
    print(f"  Backend:  http://127.0.0.1:{port}")
    print(f"  Docs:     http://127.0.0.1:{port}/api/v1/openapi.json")
    print(f"  Frontend: http://localhost:3000  (run 'npm run dev' in frontend/)")
    print(f"{'='*60}\n")

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=port,
        reload=False,    # Set to True if you want hot-reload (slower startup)
        log_level="info",
    )
