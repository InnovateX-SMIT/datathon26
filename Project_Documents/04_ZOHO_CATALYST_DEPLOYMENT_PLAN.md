 Zoho Catalyst: Cloud Migration & Deployment Blueprint

This document details the migration and deployment plan for hosting the **AI-Driven Crime Analytics & Visualization Platform** on the **Zoho Catalyst** platform. It outlines how to map the FastAPI and Next.js stack to native Catalyst serverless components, handle database migrations to ZCQL, manage resource quotas, and configure continuous integration.

---

## 1. Compliance & Mandatory Services Mapping

To comply with Datathon 2026 guidelines, all external or custom infrastructure components (such as local SQLite, Dockerized PostgreSQL, or custom JWT authentication) must be replaced with native Zoho Catalyst services. 

The following table maps the existing codebase to its target Catalyst component:

| Existing Local Stack | Target Zoho Catalyst Component | Role and Integration Strategy |
| :--- | :--- | :--- |
| **FastAPI Backend** | **Catalyst AppSail** | Persistent web hosting for the FastAPI backend, utilizing a custom Python runtime or Docker image. Configured via `app-config.json`. |
| **Next.js Frontend** | **Catalyst Slate / Web Client** | Zero-configuration static site hosting with global CDN caching. Mapped via build commands in `catalyst.json`. |
| **SQLite / PostgreSQL** | **Catalyst Data Store** | Relational data persistence queried via **Zoho Catalyst Query Language (ZCQL)**. |
| **Bcrypt & JWT Auth** | **Catalyst Authentication** | Shifting identity verification to Catalyst's hosted authentication pages. Supports native Role-Based Access Control (RBAC). |
| **Model Pickles (.pkl)** | **Catalyst Stratus** | Object storage (S3-compatible) to store XGBoost model binaries, which are pulled into AppSail RAM on startup. |
| **NetworkX Computations** | **Catalyst Job Pools** | Asynchronous tasks with up to 10 GB of RAM and 15-minute execution limits for running heavy graph algorithms. |
| **PDF Reporting** | **Catalyst SmartBrowz** | Headless Chrome browser rendering designed HTML/CSS templates with JSON payloads into PDFs. |
| **XGBoost Pipeline** | **Catalyst Zia AutoML / QuickML** | No-code training pipelines, LLM serving (Qwen 2.5), and RAG integrations. |
| **Unstructured FIR Parsing**| **Catalyst Zia Text Analytics** | Extracting entities (names, locations, weapons) from raw FIR narratives using Zia's Named Entity Recognition (NER). |
| **Rules Alerting Engine** | **Catalyst Signals & Events** | Event-driven alerting. Database inserts trigger event functions to process severity metrics. |
| **Background Cron Scripts**| **Catalyst Job Scheduling / Cron** | Triggers nightly model retraining and weekly email PDF dispatches. |
| **Local Scripts** | **Catalyst Serverless Functions** | Lightweight serverless routines (I/O) to handle webhooks and email routing. |

---

## 2. Database Migration: SQLAlchemy to Catalyst ZCQL

The migration of the relational database layer from SQLAlchemy models to the Catalyst Data Store is a significant change.

### Key ZCQL Constraints & Tradeoffs:
1. **No ORM Support**: The Python SDK does not support SQLAlchemy or other Object-Relational Mappers. The data access layer (`backend/repositories/`) must be refactored to execute raw SQL-like strings using the `zcql` service.
2. **Four-JOIN Limit**: ZCQL restricts queries to a maximum of **4 JOIN clauses** and allows only **1 conditional statement per JOIN**. Complex operations that span multiple tables (e.g., `locations -> crime_events -> crime_participation -> criminals`) must be flattened using denormalized read-projection tables or split into sequential database calls.
3. **Primary Key Exclusivity**: Catalyst tables automatically generate unique string-based IDs called `ROWID`. The codebase must adapt to use string-based identifiers instead of auto-incrementing integer fields.
4. **Inserting Data**: Instead of SQL `INSERT` strings, rows must be inserted using dictionary structures sent to the Catalyst Table Service.

### Code Migration Example (CRUD Refactoring):

#### Before (SQLAlchemy):
```python
# SQLAlchemy Query
def get_crimes_by_district(db: Session, district_name: str):
    return db.query(CrimeEvent).join(Location).filter(Location.district == district_name).all()
```

#### After (ZCQL + Python SDK):
```python
# ZCQL Query
import zcatalyst_sdk

def get_crimes_by_district(district_name: str):
    app = zcatalyst_sdk.initialize()
    zcql_service = app.zcql()
    
    query = f"SELECT ROWID, crime_type, severity FROM crime_events WHERE location_id.district = '{district_name}'"
    query_result = zcql_service.execute_query(query)
    return query_result
```

---

## 3. Catalyst Environment Row Limits & Scalability

The synthetic dataset (50,000 crime records, 50,000 criminals) exceeds the default limits of the Catalyst development tier.

* **Development Environment Constraints**: Gated at a maximum of **5,000 rows per table** and **25,000 rows overall per project**. Ingesting the 50,000-row dataset will trigger a `403 API Limit Reached` error.
* **Mitigation Strategy**:
  1. The project must use the **Catalyst Production Environment** for final evaluation to support the dataset.
  2. Alternatively, store static historical records in CSV format inside **Catalyst Stratus** object storage. The AppSail backend container can read these CSV files directly into memory during initialization, reserving the Catalyst Data Store for active user sessions and transactional records.

---

## 4. Target Monorepo Structure & Deployment

To support simultaneous deployment of both the frontend client and the backend server, the repository must be organized as a Catalyst monorepo governed by a central `catalyst.json` file:

```text
datathon26-catalyst-project/
├── catalyst.json                 # Core routing mappings for Slate & AppSail
├── .catalystrc                   # Project metadata
├── client/                       # Next.js SPA Frontend
│   ├── package.json
│   ├── client-package.json       # Slate build directives
│   └── src/
└── server/                       # FastAPI Python Backend
    ├── app-config.json           # AppSail startup mapping
    ├── requirements.txt
    └── main.py
```

### Routing Configuration (`catalyst.json`):
```json
{
  "frontend": {
    "targets": [
      {
        "name": "crime-analytics-client",
        "type": "slate",
        "path": "client"
      }
    ]
  },
  "backend": {
    "targets": [
      {
        "name": "crime-analytics-server",
        "type": "appsail",
        "path": "server"
      }
    ]
  }
}
```

### AppSail Configuration (`server/app-config.json`):
```json
{
  "deployment": {
    "stack": "python-3.10",
    "type": "managed"
  },
  "run": {
    "command": "uvicorn main:app --host 0.0.0.0 --port $X_ZOHO_CATALYST_LISTEN_PORT --workers 4"
  }
}
```

---

## 5. Deployment Commands & CI/CD Pipelines

### CLI Local Deployment Sequence:
Developers must install the Catalyst CLI globally and run the deployment commands:

```powershell
# 1. Install CLI
npm install -g zcatalyst-cli

# 2. Login to Zoho
catalyst login

# 3. Initialize project
catalyst init

# 4. Run emulator locally for testing
catalyst serve

# 5. Deploy all components to the cloud
catalyst deploy
```

### CI/CD Pipelines:
Avoid using external services like GitHub Actions. Instead, configure a `catalyst-pipelines.yaml` pipeline in the root directory. Link the GitHub repository through the Catalyst Console to automatically run tests and trigger a production deployment whenever a commit is pushed to the `main` branch.
