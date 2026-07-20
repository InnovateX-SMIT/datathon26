import os
import sys
import types

# Dynamically construct the 'backend' namespace package in memory before importing app modules
dir_path = os.path.dirname(os.path.abspath(__file__))
backend_mod = types.ModuleType("backend")
backend_mod.__path__ = [dir_path]
sys.modules["backend"] = backend_mod

# Import the FastAPI application object
from app.main import app

# Retrieve dynamic listening port injected by the Catalyst runtime
port_str = os.environ.get("X_ZOHO_CATALYST_LISTEN_PORT")
if port_str:
    port = int(port_str)
    print(f"Listening on port: {port} (Catalyst AppSail runtime)")
else:
    port = 8000
    print(f"X_ZOHO_CATALYST_LISTEN_PORT not found. Defaulting to: {port}")

# Start Uvicorn programmatically passing the app instance directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
