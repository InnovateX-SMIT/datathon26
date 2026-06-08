# Development Setup Guide

Follow this guide to set up the **Predictive Guardians** local development sandbox.

---

## 1. Prerequisites

Ensure you have the following installed on your machine:
- **Node.js** (v18.0.0 or higher)
- **Python** (v3.10.0 or higher)
- **Docker** (recommended for database setup)

---

## 2. Database Integration

The system runs on **PostgreSQL**. To spin up the database container:

1. Make sure Docker Desktop is running.
2. Run the following command from the project root:
   ```bash
   docker compose up -d db
   ```
   *Note: This starts PostgreSQL on port `5432` with username `postgres`, password `password123`, and database name `crime_intel`.*

---

## 3. Backend Setup

Initialize the FastAPI backend server:

1. Navigate to the `backend` folder:
   ```bash
   cd backend
   ```
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```
3. Activate the environment:
   - **Windows (PowerShell)**: `.venv\Scripts\Activate.ps1`
   - **macOS/Linux**: `source .venv/bin/activate`
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the uvicorn development server:
   ```bash
   uvicorn backend.app.main:app --reload --port 8000
   ```
6. Verify startup by visiting: [http://localhost:8000/health](http://localhost:8000/health)

---

## 4. Frontend Setup

Run the Next.js visual dashboard:

1. Navigate to the `frontend` folder:
   ```bash
   cd frontend
   ```
2. Install npm packages:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
4. Open the interface in your browser: [http://localhost:3000](http://localhost:3000)
