import os
import sys

# Ensure repository root is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import uvicorn
from backend.app.main import app

if __name__ == "__main__":
    print("Starting CrimeNexus Backend in Local Development Mode on http://127.0.0.1:8000 ...")
    uvicorn.run("backend.app.main_local:app", host="127.0.0.1", port=8000, reload=True)
