# CrimeNexus

**Unified operational intelligence for law enforcement connecting structured crime records into real-time dashboards, predictive ML intelligence, geospatial maps, criminal network graphs, and executive reports.**

<p align="center">
  <img alt="Status" src="https://img.shields.io/badge/status-active--production-success?style=plastic" />
  <img alt="Datathon" src="https://img.shields.io/badge/Datathon-2026-6366f1?style=plastic" />
  <img alt="License" src="https://img.shields.io/badge/license-MIT-green?style=plastic" />
  <img alt="AI/ML" src="https://img.shields.io/badge/AI%2FML-Zoho%20QuickML-FF6B6B?style=plastic&logo=scikitlearn&logoColor=white" />
  <img alt="Backend" src="https://img.shields.io/badge/backend-FastAPI-009688?style=plastic&logo=fastapi&logoColor=white" />
  <img alt="Frontend" src="https://img.shields.io/badge/frontend-Next.js%2016-000000?style=plastic&logo=nextdotjs&logoColor=white" />
  <img alt="Database" src="https://img.shields.io/badge/database-PostgreSQL%2015-336791?style=plastic&logo=postgresql&logoColor=white" />
  <img alt="Python" src="https://img.shields.io/badge/python-3.10%2B-3776AB?style=plastic&logo=python&logoColor=white" />
  <img alt="TypeScript" src="https://img.shields.io/badge/TypeScript-strict-3178C6?style=plastic&logo=typescript&logoColor=white" />
</p>

<p align="center">
  <!-- Onslate / Catalyst Deployment -->
  <a href="https://crimenexus.onslate.in">
    <img src="https://img.shields.io/website?url=https%3A%2F%2Fcrimenexus.onslate.in&up_message=CrimeNexus%20Live%20%F0%9F%8C%90&up_color=2ea44f&style=plastic&logo=googlechrome&logoColor=white" alt="CrimeNexus Catalyst Live" />
  </a>
  &nbsp;
  <!-- Vercel Deployment -->
  <a href="https://datathon26-ouxvtzz4b-abhinavpuris-projects.vercel.app/">
    <img src="https://img.shields.io/website?url=https%3A%2F%2Fdatathon26-ouxvtzz4b-abhinavpuris-projects.vercel.app%2F&up_message=Vercel%20Mirror%20%F0%9F%9A%80&up_color=2ea44f&style=plastic&logo=vercel&logoColor=white" alt="CrimeNexus Vercel Live" />
  </a>
</p>
<p align="center">
<img src="docs/screenshots/datathon26_banner-final.png" alt="CrimeNexus Home / Platform Overview" width="100%">
</p>

---

## Table of Contents

1. [Overview](#1-overview)
2. [Problem Statement](#2-problem-statement)
3. [Why CrimeNexus](#3-why-crimenexus)
4. [Platform at a Glance](#4-platform-at-a-glance)
5. [Technology Stack](#7-technology-stack)
6. [Product Tour & Core Modules](#8-product-tour--core-modules)
7. [Machine Learning & Predictive Intelligence](#9-machine-learning--predictive-intelligence)
8. [Backend Architecture](#10-backend-architecture)
9. [Database Overview](#11-database-overview)
10. [Project Structure](#12-project-structure)
11. [API Overview](#13-api-overview)
12. [Installation & Local Setup](#14-installation--local-setup)
13. [Docker Orchestration](#15-docker-orchestration)
14. [Configuration & Environment Variables](#16-configuration--environment-variables)
15. [Deployment](#17-deployment)
16. [Future Roadmap](#18-future-roadmap)
17. [Team](#19-team)
18. [License](#20-license)

---

## 1. Overview

**CrimeNexus** is an end-to-end intelligence and decision-support platform engineered for law enforcement agencies and investigative command centers. It transforms siloed First Information Report (FIR) data, incident registries, demographic distributions, and repeat offender histories into a single, unified operational cockpit. 

Instead of waiting days for manual case audits or static spreadsheet summaries, investigative officers and police leadership gain instant access to district-level trend lines, interactive geospatial heatmaps, relational criminal network graphs, automated threat alerts, demographic risk correlations, Modus Operandi (MO) pattern matching, and real-time machine learning predictions powered by **Zoho Catalyst QuickML**.

The platform is designed around strict separation of concerns:
- **Presentation Layer**: Next.js 16 (React 19) App Router with TailwindCSS, Lucide icons, React-Leaflet, React Flow, and Recharts.
- **Service Layer**: FastAPI REST API handling RBAC authentication, validation, domain services, and dataset ingestion.
- **Analytics & Graph Layer**: Pandas, NumPy, SciPy, and NetworkX computing temporal aggregations, spatial density, and network centrality.
- **AI & Predictive Intelligence Layer**: 3-pipeline machine learning engine integrated with **Zoho Catalyst QuickML** cloud endpoints alongside local CatBoost/Scikit-Learn fallback inference.

CrimeNexus was built by **Team InnovateX** from **Sikkim Manipal Institute of Technology (SMIT)** for **Datathon 2026**.

---

## 2. Problem Statement

Police departments and investigative bodies produce massive amounts of operational data daily—FIR filings, victim and accused dossiers, legal sections, station beat logs, and judicial proceeding records. However, this wealth of information remains largely un-operationalized due to:

- **Data Fragmentation**: Disconnected spreadsheets and legacy paper records lack a shared schema, preventing cross-station intelligence sharing.
- **Reactive Posture**: Crime hotspots and emerging patterns are identified after escalation rather than intercepted proactively.
- **Hidden Syndicates**: Co-offending networks, criminal rings, and geographic links live in an investigator's memory rather than in a queryable graph.
- **Heuristic Resourcing**: Beat patrols and tactical resource deployments are frequently assigned on intuition rather than empirical incident density and risk scoring.
- **Disjointed Modus Operandi & Social Context**: Lack of tools to correlate signature tactics, weapon usage, and socio-economic vulnerability indicators across jurisdictional boundaries.

CrimeNexus solves these challenges by converting structured records into actionable operational decisions in real time.

---

## 3. Why CrimeNexus

| Principle | What it means in practice |
| :--- | :--- |
| **Single Source of Truth** | FIR filings, offender profiles, crime classifications, and locations are normalized into an interconnected relational schema. |
| **Multi-Feed Ingestion** | Robust alias mapping handles diverse CSV/XLSX feeds from metro stations, regional commissionerates, and heritage zones seamlessly. |
| **Predictive AI Intelligence** | End-to-end ML integration with **Zoho Catalyst QuickML** delivers live crime risk scoring, future hotspot forecasting, and recidivism likelihood prediction. |
| **Graph-Based Investigations** | Criminal networks are modeled with NetworkX and visualized with React Flow, exposing syndicates, kingpins, and structural links. |
| **Modus Operandi & Sociological Intel** | Dedicated modules correlate criminal tactics, weapon signatures, and demographic risk indicators across jurisdictions. |
| **Actionable Decision Support** | Converts raw data into prioritized tactical interventions, patrol rosters, and executive dossiers. |

---

## 4. Platform at a Glance

| Metric | Value / Capability |
| :--- | :--- |
| **Core Modules** | **11 Dedicated Operational Modules** |
| **Predictive ML Pipelines** | **3 End-to-End Pipelines** (Crime Risk, Future Hotspots, Recidivism Risk) |
| **ML Engine** | **Zoho Catalyst QuickML** + Local CatBoost/Scikit-Learn Fallback |
| **Map GIS Layers** | Choropleths, Incident Clusters, Density Heatmaps, Hotspot Predictor |
| **Network Graph Types** | Offender-to-Crime, Offender-to-Location, Co-offending Linkage |
| **Active Statewide Datasets** | 15,000+ Multi-District Synthetic & Historical Police Records |
| **Jurisdictional Coverage** | 31 Karnataka Districts / 235+ Police Station Beats |
| **Executive Reports** | Dynamic multi-parameter dossier generation with instant PDF/print export |

---


## 5. Technology Stack

| Layer | Technology | Key Capabilities |
| :--- | :--- | :--- |
| **Frontend** | Next.js 16.2.7, React 19, TypeScript | App Router, Server/Client components, strict type safety |
| **Styling & UI** | TailwindCSS v4, Lucide React | Modern dark-mode law enforcement operational interface |
| **GIS & Maps** | Leaflet, React-Leaflet ^5.0.0 | Choropleths, density heatmap overlays, station clustering |
| **Graph Visuals** | React Flow (`@xyflow/react`) ^12.11.0 | Interactive criminal network diagrams with custom nodes |
| **Data Viz** | Recharts ^3.8.1 | Temporal crime trends, category distribution, demographic charts |
| **Backend** | FastAPI ≥0.100.0, Uvicorn, Pydantic v2 | Async REST API, automatic OpenAPI/Swagger documentation |
| **Machine Learning** | **Zoho Catalyst QuickML**, CatBoost, Scikit-Learn | Crime risk scoring, hotspot forecasting, recidivism prediction |
| **Graph Analytics** | NetworkX | Degree centrality, community detection, link discovery |
| **Data Processing** | Pandas ≥2.2.0, NumPy ≥2.0.0, SciPy ≥1.13.0 | Fast vectorized statistical aggregations |
| **Database & ORM** | PostgreSQL 15, SQLAlchemy ≥2.0.0, Psycopg2 | Relational schema with normalized FIR & entity models |
| **Authentication** | PyJWT, Passlib (Bcrypt) | Secure token-based auth with Role-Based Access Control |
| **Testing** | Pytest ≥8.3.2, Pytest-asyncio | Backend service and API test coverage |
| **Deployment** | Zoho Catalyst (AppSail, Client Hosting), Docker | Hybrid cloud serverless and containerized deployment |

---

## 6. Product Tour & Core Modules

### 6.1 Command Center
The central operational dashboard providing instant visibility into total incident counts, active investigations, arrest rates, average severity indexes, temporal crime volume trendlines, and a live statewide incident feed.

<p align="center">
<img src="docs/screenshots/command-center-1.jpeg" alt="Command Center KPI Cards and Trends" width="100%">
</p>
<p align="center">
<img src="docs/screenshots/command-center-2.jpeg" alt="Command Center Top Districts and Recent Feed" width="100%">
</p>

---

### 6.2 Dataset Manager
Allows administrators to manage, validate, preview, and activate multi-format police record feeds (CSV/XLSX). Built-in alias mapping normalizes varying regional column nomenclature (e.g., Bengaluru Metro, Coastal Hubballi, Mysuru Heritage) into the unified platform schema.

<p align="center">
<img src="docs/screenshots/Dataset-Manager.jpeg" alt="Dataset Manager Portal" width="100%">
</p>

---

### 6.3 Crime Analytics
Aggregates crime data across temporal dimensions (daily, weekly, monthly, yearly), gravity classes (Grave vs. Non-Grave), and IPC/BNS crime major heads.

<p align="center">
<img src="docs/screenshots/crime-analytics.png" alt="Crime Analytics Dashboard" width="100%">
</p>

---

### 6.4 FIR Management & Intake
A comprehensive system of record for First Information Reports. Enables officers to search cases by number, law cited, accused names, and procedural stages (Under Investigation, Chargesheeted, B-Report). Includes a multi-step digital intake portal for filing new FIRs.

<p align="center">
<img src="docs/screenshots/FIR.jpeg" alt="FIR Case Explorer" width="100%">
</p>
<p align="center">
<img src="docs/screenshots/Register-FIR.jpeg" alt="Register New FIR Case" width="100%">
</p>

---

### 6.5 Geo Intelligence & Hotspot Prediction
Renders synchronized GIS layers with district-level choropleths, density heatmap overlays, and station beat clusters. Incorporates **Pipeline 2: Future Hotspot Prediction Card** powered by Zoho QuickML to forecast future high-risk sectors and peak operational time windows.

<p align="center">
<img src="docs/screenshots/geo-intelligence-1.png" alt="Geo Intelligence Engine" width="100%">
</p>

<p align="center">
<img src="docs/screenshots/CRIME RISK PREDICTIVE.jpg" alt="CRIME RISK PREDICTIVE" width="100%">
</p>

<p align="center">
<img src="docs/screenshots/FUTURE HOTSPOT PREDICTION.jpg" alt="FUTURE HOTSPOT PREDICTION" width="100%">
</p>

<p align="center">
<img src="docs/screenshots/TIME-OF-DAY INCIDENT ANALYSIS.jpg" alt="TIME-OF-DAY INCIDENT ANALYSIS" width="100%">
</p>






---

### 6.6 Network Intelligence & Recidivism Prediction
Traces connections between offenders, organized crime syndicates, crime events, and locations using NetworkX graph centrality and interactive React Flow diagrams. Embeds **Pipeline 3: Repeat Offender Recidivism Prediction Card** to evaluate an offender's re-offending risk score and future gravity potential.

<p align="center">
<img src="docs/screenshots/network-intel-1.png" alt="Network Intelligence Search Interface" width="100%">
</p>


<p align="center">
<img src="docs/screenshots/Repeat Offender Recidivism.jpg" alt="Repeat Offender Recidivism" width="100%">
</p>

<p align="center">
<img src="docs/screenshots/Network-intel.jpeg" alt="Rendered Criminal Network Graph" width="100%">
</p>

---

### 6.7 Modus Operandi (MO) Intelligence
A specialized investigative module that performs cross-jurisdictional signature matching:
<p align="center">
<img src="docs/screenshots/MO.jpg" alt="Modus Operandi (MO) Intelligence" width="100%">
</p>

---

### 6.8 Sociological Intelligence & Demographic Analytics
Analyzes the socio-economic and demographic fabric underlying regional crime patterns:
<p align="center">
<img src="docs/screenshots/Sociological.jpg" alt="Sociological Intelligence & Demographic Analytics" width="100%">
</p>

---

### 6.9 Decision Support Center
Translates statistical signals and ML predictions into actionable tactical directives:
- **Priority Actions**: Ranked tactical recommendations with confidence scores and impact ratings.
- **Patrol Allocation**: Dynamic beat patrol optimization balancing incident density with station manpower.
- **Proactive Interventions**: Automated recommendations for community policing and high-risk offender surveillance.

<p align="center">
<img src="docs/screenshots/decision-support-1.png" alt="Decision Support Priority Actions" width="100%">
</p>

---

### 6.10 Operational Alerts Panel
Rule-based detection engine monitoring the active dataset for spatial spikes, serial offender activity, and grave crime escalations. Provides tactical dispatch triage and historical archive management.

<p align="center">
<img src="docs/screenshots/Alert.jpeg" alt="Operational Alerts Panel" width="100%">
</p>

---

### 6.11 Executive Dossier Briefings
Generates standardized, multi-parameter intelligence dossiers for commanding officers and executive review cycles with configurable report types, date ranges, and export capabilities.

<p align="center">
<img src="docs/screenshots/Executive-reports.jpeg" alt="Executive Reports Portal" width="100%">
</p>

---

## 7. Machine Learning & Predictive Intelligence

CrimeNexus incorporates **three production-grade machine learning pipelines** with a hybrid architecture: live cloud inference via **Zoho Catalyst QuickML REST endpoints** with automated OAuth token refresh and seamless fallback to local CatBoost/Scikit-Learn models.

```mermaid
flowchart LR
    subgraph Frontend["Frontend UI Cards"]
        P1Card[Crime Risk Card]
        P2Card[Hotspot Prediction Card]
        P3Card[Recidivism Risk Card]
    end

    subgraph API["FastAPI (/predictions/*)"]
        Router[predictions/router.py]
    end

    subgraph Service["Prediction Service Engine"]
        Svc[prediction_service.py]
        TokenMgr[OAuth Token Auto-Refresh]
    end

    subgraph QuickML["Zoho Catalyst QuickML Endpoints"]
        QM1[Pipeline 1: Crime Risk Model]
        QM2[Pipeline 2: Hotspot Forecasting Model]
        QM3[Pipeline 3: Recidivism Risk Model]
    end

    subgraph Fallback["Local ML Fallback Engine"]
        CatBoostEngine[CatBoost / Scikit-Learn Pipeline]
    end

    Frontend --> Router
    Router --> Svc
    Svc --> TokenMgr
    Svc -->|Primary REST Inference| QuickML
    Svc -.->|Offline / Fallback| Fallback
```

### Pipeline Overview

| Pipeline | Target Output | Input Features | Integration Point |
| :--- | :--- | :--- | :--- |
| **Pipeline 1: Crime Risk Prediction** | Crime gravity level, risk score, probability distribution | Spatial coordinates, hour of day, day of week, gravity offence class, 30d station crime density | Geo Intelligence & Command Center |
| **Pipeline 2: Future Hotspot Prediction** | Sector hotspot probability (0-100%), tactical patrol rating | Prior 7d/30d/90d/180d crime counts, spatial density ratio, peak hour window ID, district ID | Geo Intelligence (`/geo`) |
| **Pipeline 3: Recidivism Prediction** | Repeat offender risk tier (Low/Medium/High/Critical), re-offending likelihood | Offender age, gender, prior crime gravity, major crime head, prior arrest count | Network Intelligence (`/network`) |

---

## 8. Backend Architecture

The backend follows a clean **Router → Service → Repository / Model** pattern:

```
backend/
├── api/                  # FastAPI routers and route handlers
│   ├── auth/             # JWT login, token refresh, and RBAC verification
│   ├── admin/            # Dataset upload, preview, and activation
│   ├── alerts/           # Threat alert queries and status triage
│   ├── analytics/        # Statistical aggregations and sociological intelligence
│   ├── crimes/           # Incident querying and history
│   ├── fir/              # FIR CRUD, intake, and Modus Operandi analytics
│   ├── geo/              # Spatial coordinate feeds and choropleth data
│   ├── network/          # Graph node/edge generator and centrality metrics
│   ├── predictions/      # Phase 5 QuickML ML inference endpoints
│   ├── recommendations/  # Decision support action generators
│   └── reports/          # Executive dossier builders
├── services/             # Domain logic and computational services
│   ├── alert_service.py
│   ├── analytics_service.py
│   ├── dataset_service.py
│   ├── fir_service.py
│   ├── geo_service.py
│   ├── network_service.py
│   ├── network_analytics_service.py
│   ├── prediction_service.py      # QuickML REST client + local fallback
│   ├── recommendation_service.py
│   └── report_service.py
├── models/               # SQLAlchemy ORM database models
├── repositories/         # Database query and persistence abstractions
├── schemas/              # Pydantic v2 validation models
└── core/                 # Config, security, database session, and logging
```

---

## 9. Database Overview

The relational database is structured to model both standard operational police records and the detailed procedural lifecycle of Indian First Information Reports (FIRs):

```mermaid
erDiagram
    USER ||--o{ AUDIT_LOG : generates
    USER ||--o{ REPORT : authors
    DATASET ||--o{ CRIME : sources
    CRIME ||--o{ CRIME_PARTICIPATION : has
    CRIMINAL ||--o{ CRIME_PARTICIPATION : involved_in
    VICTIM ||--o{ CRIME_PARTICIPATION : involved_in
    CRIME ||--o{ ALERT : triggers
    CRIME ||--o{ RECOMMENDATION : informs
    LOCATION ||--o{ CRIME : occurred_at
    POLICE_STATION ||--o{ LOCATION : covers

    FIR_CASE ||--|| FIR_GEOGRAPHY : located_in
    FIR_CASE ||--o{ FIR_LAW : cites
    FIR_CASE ||--o{ FIR_PEOPLE : names
    FIR_CASE ||--o{ FIR_PROCEEDINGS : tracks
    FIR_CASE }o--|| FIR_ORGANIZATION : filed_by
    FIR_CASE ||--o{ FIR_LOOKUP : references
```

---

## 12. Project Structure

```
crimenexus-ai/
├── frontend/                  # Next.js 16 presentation layer
│   ├── app/                   # App Router pages
│   │   ├── dashboard/         # Command Center
│   │   ├── dataset-manager/   # Multi-feed dataset registry
│   │   ├── analytics/         # Crime statistical analytics
│   │   ├── fir/               # FIR cases and register intake
│   │   ├── geo/               # GIS map & Hotspot prediction
│   │   ├── network/           # Criminal network & Recidivism prediction
│   │   ├── modus-operandi/    # MO signature matching & behavioral profiles
│   │   ├── sociological/      # Demographic & socio-economic risk correlation
│   │   ├── decision-support/  # Priority actions & patrol allocation
│   │   ├── alerts/            # Operational threat dispatch
│   │   ├── reports/           # Executive dossiers
│   │   ├── about/             # Team & platform documentation
│   │   └── login/             # Secure authentication portal
│   ├── components/            # Reusable UI cards, tables, maps, and layouts
│   ├── features/              # Modular domain components, hooks, and types
│   └── services/              # Client API clients (api.ts, predictionService.ts)
│
├── backend/                   # FastAPI REST application
│   ├── api/                   # Route controllers
│   ├── services/              # Domain business logic & QuickML client
│   ├── models/                # SQLAlchemy database entities
│   ├── schemas/               # Pydantic input/output schemas
│   ├── core/                  # App configuration & JWT auth
│   └── tests/                 # Pytest test suite
│
├── datasets/                  # Datasets & synthetic generation feeds
│   ├── processed/             # Preprocessed ML training sets (hotspot, offender)
│   └── *.csv                  # Karnataka statewide, metro, coastal & heritage feeds
│
├── docs/                      # Technical documentation & screenshots
├── scripts/                   # Validation and helper scripts
├── docker-compose.yml         # Multi-container orchestration
├── catalyst.json              # Zoho Catalyst deployment configuration
└── .catalystrc                # Catalyst environment metadata
```

---

## 10. API Overview

| Router | Path Prefix | Description | Status |
| :--- | :--- | :--- | :--- |
| `auth/router.py` | `/auth` | Authentication, JWT login, and profile info | Complete |
| `admin/datasets.py` | `/admin/datasets` | CSV/XLSX upload, preview, and dataset activation | Complete |
| `analytics/router.py` | `/analytics` | Dashboard KPIs, temporal trends, sociological intelligence | Complete |
| `fir/router.py` | `/fir` | FIR case retrieval, creation, and MO analytics | Complete |
| `geo/router.py` | `/geo` | Spatial coordinates, district choropleths, beat clustering | Complete |
| `network/router.py` | `/network` | Graph nodes, edges, degree centrality, and links | Complete |
| `predictions/router.py` | `/predictions` | QuickML crime risk, hotspot, and recidivism predictions | Complete |
| `alerts/router.py` | `/alerts` | Tactical alerts and severity dispatch | Complete |
| `recommendations/router.py` | `/recommendations` | Decision support and patrol allocation actions | Complete |
| `reports/router.py` | `/reports` | Executive dossier generation and retrieval | Complete |

---

## 11. Installation & Local Setup

### Prerequisites

- **Python**: 3.10 or higher
- **Node.js**: 18+ (Node 20+ recommended for Next.js 16)
- **PostgreSQL**: 15+
- **Git**

### 1. Clone the Repository

```bash
git clone https://github.com/InnovateX-SMIT/datathon26.git
cd datathon26
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate

pip install -r requirements.txt

# Configure environment variables
cp .env.example .env

# Initialize PostgreSQL database schema
python -c "from backend.core.database import init_db; init_db()"

# Start FastAPI development server
uvicorn main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd ../frontend
npm install

# Configure environment variables
cp .env.example .env.local

# Start Next.js development server
npm run dev
```

The frontend will be live at `http://localhost:3000` communicating with the FastAPI backend at `http://localhost:8000`.

---

## 12. Docker Orchestration

Run the complete platform (Database + Backend + Frontend) using Docker Compose:

```bash
# Build and run containers in detached mode
docker compose up --build -d

# Check running status
docker compose ps

# View real-time logs
docker compose logs -f

# Shut down services
docker compose down
```

| Service | Container URL | Description |
| :--- | :--- | :--- |
| **Frontend** | `http://localhost:3000` | Next.js 16 Application |
| **Backend API** | `http://localhost:8000` | FastAPI REST Engine |
| **Swagger Docs** | `http://localhost:8000/docs` | Interactive API documentation |
| **PostgreSQL** | `localhost:5432` | Relational database store |

---

## 13. Configuration & Environment Variables

### Backend Configuration (`backend/.env`)

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/crimenexus
JWT_SECRET_KEY=your_super_secret_jwt_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CORS_ORIGINS=["http://localhost:3000","https://crimenexus.onslate.in"]

# Zoho Catalyst QuickML Endpoints & Auth
QUICKML_CRIME_RISK_ENDPOINT=https://api.catalyst.zoho.in/quickml/.../predict
QUICKML_HOTSPOT_ENDPOINT=https://api.catalyst.zoho.in/quickml/.../predict
QUICKML_OFFENDER_ENDPOINT=https://api.catalyst.zoho.in/quickml/.../predict
QUICKML_API_KEY=your_quickml_api_key
ZOHO_CLIENT_ID=your_zoho_client_id
ZOHO_CLIENT_SECRET=your_zoho_client_secret
ZOHO_REFRESH_TOKEN=your_zoho_refresh_token
```

### Frontend Configuration (`frontend/.env.local`)

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_MAP_TILE_PROVIDER=https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png
```

---

## 14. Deployment

### Zoho Catalyst Deployment (Production)

The platform is natively configured for deployment to **Zoho Catalyst**:
- **AppSail**: Hosts the containerized FastAPI backend.
- **Web Client Hosting**: Serves the Next.js production build.
- **Data Store**: Manages persistent application storage.

```bash
catalyst login
catalyst deploy
```

---

## 15. Future Roadmap
- [ ] **Real-time CCTV & Drone Feed Ingestion**: Computer vision integration for automated license plate and crowd anomaly detection.
- [ ] **Speech-to-Text Multi-Lingual FIR Intake**: Voice-driven FIR registration supporting regional languages (Kannada, Hindi, etc.).
- [ ] **Automated Court Summons & Bail Prediction**: Predictive modeling for judicial attendance and bail compliance.

---

## 16. Team

**Team InnovateX** · Sikkim Manipal Institute of Technology (SMIT) · Datathon 2026

| Name | Role |
| :--- | :--- |
| **Krish Anand** | Team Leader |
| **Abhinav Puri** | Team Member |
| **Debojit Deb** | Team Member |
| **Dishaba Siddhrajsinh Zala** | Team Member |
| **Shreya Singh** | Team Member |

---

## 17. License

This project is released under the **MIT License**. See [`LICENSE`](./LICENSE) for full details.

---

<p align="center">
<sub>CrimeNexus · Built with ❤️ for Datathon 2026 by Team InnovateX, SMIT.</sub>
</p>
