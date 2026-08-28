# CrimeNexus: Local Setup Changes Audit

This document audits and details all configuration and code adjustments made to set up the CrimeNexus project for local development on a newly cloned repository. Share these steps with other team members to align their local systems.

---

## 1. Environment Configurations (Gitignored Files)

Because local environment configurations are gitignored, they must be created manually.

### A. Frontend Environment
Create a file at [`frontend/.env.local`](file:///Users/krishanand/datathon26/frontend/.env.local) with the following content to point the Next.js client to the local FastAPI server:
```env
# ==============================================================================
# CrimeNexus Frontend Configuration
# ==============================================================================
# 1. LOCAL DEVELOPMENT (FastAPI on http://localhost:8000)
NEXT_PUBLIC_API_URL=http://localhost:8000

# 2. PRODUCTION DEPLOYMENT (Zoho Catalyst AppSail)
# NEXT_PUBLIC_API_URL=https://crimenexus-backend-50045204017.development.catalystappsail.in
# ==============================================================================
```

### B. Backend Environment
Create a file at [`backend/.env`](file:///Users/krishanand/datathon26/backend/.env) with local development settings:
```env
# ==============================================================================
# CrimeNexus Backend Configuration
# ==============================================================================
ENVIRONMENT=development
SECRET_KEY=supersecretjwtkeyforcrimeplatform2026!
# DATABASE_URL resolves automatically to local crime_intel.db absolutely in config.py
# ==============================================================================
```

---

## 2. Directory Creation (Gitignored Folders)

FastAPI requires specific local upload/model directories which are excluded in `.gitignore`. Create these directory paths from the project root:
```bash
mkdir -p datasets/uploaded datasets/models backend/datasets/uploaded backend/datasets/models
```

---

## 3. CORS Configuration Fix

To allow the frontend (`localhost:3000`) to request resources from the backend (`localhost:8000`), the CORS middleware must be enabled.

In [`backend/app/main.py`](file:///Users/krishanand/datathon26/backend/app/main.py):
1.  **Uncomment the import** (around line 27):
    ```python
    from fastapi.middleware.cors import CORSMiddleware
    ```
2.  **Uncomment the middleware configuration** (around line 336-358):
    ```python
    # Explicit origins and dynamic regex support for all HTTP/HTTPS origins
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

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_origin_regex=r"^https?://.*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    ```

---

## 4. Local Database Seeding

The SQLite database must be seeded to populate master dropdown lookups (Nationalities, Genders, Blood Groups, Castes, Religions, Occupations, Case Categories, Gravity Offences, Case Statuses, States, Districts, Courts, Police Stations, and Acts/Sections).

Run the seeding script using your virtual environment Python interpreter:
```bash
# From the project root directory
backend/.venv/bin/python scripts/seed_database.py
```

---

## 5. Startup & Execution Instructions

### A. Run Backend API (FastAPI)
Using the virtual environment Python interpreter from the project root:
```bash
backend/.venv/bin/python backend/app/main.py
```
*(Runs the FastAPI app on Uvicorn listening at `http://127.0.0.1:8000`)*

### B. Run Frontend Web App (Next.js)
From the project root:
```bash
cd frontend
npm run dev
```
*(Runs the development server at `http://localhost:3000`)*

### C. Troubleshooting Port Conflicts
If you receive an `Address already in use` error on ports `8000` or `3000`:
```bash
# Find PIDs occupying the ports
lsof -i :8000
lsof -i :3000

# Terminate the process by PID
kill -9 <PID>
```
