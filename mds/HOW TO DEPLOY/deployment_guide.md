# 🚀 Complete Deployment Guide & Git Commit Reference

## 📌 1. Git Commit Message

Use this clear, descriptive commit message for your repository:

```text
feat(deployment): complete working Catalyst AppSail backend & Slate frontend setup

- Backend: Configured AppSail Python 3.13 runtime with pre-bundled Linux vendor packages (sys.path in app/main.py)
- Backend: Configured dynamic port binding for X_ZOHO_CATALYST_LISTEN_PORT in app/main.py
- Backend: Enabled automatic database schema creation & migrations across all environments
- Backend: Configured app-config.json for python3 app/main.py execution
- Frontend: Centralized process.env.NEXT_PUBLIC_API_URL pointing to live AppSail backend
- Frontend: Configured Next.js static HTML export (output: "export") for Catalyst Slate
```

---

## 🛠️ 2. Future Backend Deployment Cheatsheet

### Case A: You ONLY updated backend Python code (`app/`, `api/`, `models/`, `services/`, `core/`)
No new `pip` packages added. Simply deploy:

```powershell
cd backend
catalyst deploy
```

---

### Case B: You added NEW packages to `backend/requirements.txt`
Re-package Linux binaries via Docker, then deploy:

```powershell
cd backend
docker run --rm -v "${PWD}:/app" -w /app python:3.13-slim sh -c "pip install --target /app/vendor -r requirements.txt"
catalyst deploy
```

---

## 🌐 3. Live Deployment URLs Reference

* **AppSail Backend URL**:
  `https://crimenexus-backend-50045204017.development.catalystappsail.in`
* **Health Check Verification**:
  `https://crimenexus-backend-50045204017.development.catalystappsail.in/health`

---

## ⚙️ 4. Key Configuration Files Checklist

1. **`backend/app-config.json`**:
   ```json
   {
     "command": "python3 app/main.py",
     "build_path": "./",
     "stack": "python_3_13",
     "env_variables": {
       "ENVIRONMENT": "production",
       "SECRET_KEY": "supersecretjwtkeyforcrimeplatform2026!"
     },
     "memory": 2048,
     "disk": 1024,
     "scripts": {}
   }
   ```

2. **`backend/app/main.py` (Vendor Auto-Load & Port)**:
   ```python
   vendor_dir = os.path.join(backend_root, "vendor")
   if os.path.exists(vendor_dir) and vendor_dir not in sys.path:
       sys.path.insert(0, vendor_dir)

   if __name__ == "__main__":
       import uvicorn
       port = int(os.getenv("X_ZOHO_CATALYST_LISTEN_PORT") or os.getenv("PORT") or 8000)
       uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
   ```

3. **`frontend/.env.local`**:
   ```env
   NEXT_PUBLIC_API_URL=https://crimenexus-backend-50045204017.development.catalystappsail.in
   ```

4. **`frontend/next.config.ts`**:
   ```typescript
   const nextConfig: NextConfig = {
     output: "export",
     devIndicators: false,
     images: { unoptimized: true }
   };
   ```
