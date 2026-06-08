# Project Folder Structure Definition

This document details the file and folder layout of the **Predictive Guardians** AI-Powered Crime Intelligence Platform. It outlines the separation of concerns and explains the role of each directory.

---

## Workspace Map

```text
project-root/
│
├── frontend/                 # Presentation Layer (Next.js, Tailwind, TS)
│   ├── app/                  # App Router setup and layout configurations
│   ├── components/           # Shared charts, maps, forms, and layouts
│   ├── features/             # Specific panels (analytics, network, predictive)
│   ├── services/             # Frontend-side api fetches
│   └── public/               # Static assets
│
├── backend/                  # API and ORM Core (FastAPI, SQLAlchemy, JWT)
│   ├── app/                  # FastAPI main application configuration
│   ├── api/                  # Versioned routers by domain features
│   ├── services/             # Core business logics
│   ├── models/               # SQLAlchemy PostgreSQL schemas
│   ├── schemas/              # Pydantic validation schemas
│   ├── core/                 # Configs, DB sessions, Security, and Logging
│   └── tests/                # Test suites
│
├── analytics/                # Statistical Calculations & Trends (Pandas, NumPy)
│   ├── crime_analysis/       # Category, trend, and station groupings
│   ├── temporal_analysis/    # Yearly, monthly, weekly, and daily calculations
│   └── geo_analysis/         # Spatial bounds and heatmaps generators
│
├── ml/                       # Machine Learning Layer (XGBoost, H2O, SHAP)
│   ├── crime_prediction/     # Incident forecasting and classification
│   ├── hotspot_prediction/   # Spatial predictive models
│   ├── offender_prediction/  # Suspect recidivism prediction
│   ├── explainability/       # SHAP values explanations
│   └── network_analysis/     # Link and degree centralities (NetworkX)
│
├── database/                 # Migration scripts, seeds, and backups
├── datasets/                 # CSV data files (raw, processed, synthetic)
├── docs/                     # Strategic planners and implementation guides
├── scripts/                  # Automated helper utilities
└── infrastructure/           # Docker configs and Catalyst environments
```

---

## Directory Roles & Descriptions

### 1. Presentation (`frontend/`)
- **`app/`**: Contains App Router page routes for Dashboard, Crime Analytics, Geo Intelligence, Predictive Intelligence, Network Intelligence, Decision Support, Alerts, Reports, and Admin.
- **`components/`**: House reusable visualization templates such as leaflet canvas hooks, recharts wraps, and common layout bars.

### 2. Backend API (`backend/`)
- **`app/main.py`**: Initializes FastAPI, loads middleware configurations, registers routes, and maps global errors handlers.
- **`core/`**: Houses settings extraction via Pydantic, database connections configurations, security utilities (password hashing and jwt generation), and logging formatters.
- **`models/`**: PostgreSQL table schemas mapped using SQLAlchemy declarative base.

### 3. Analytics & Statistical Calculations (`analytics/`)
- Handles heavy dataframe calculations out-of-band to prevent bottlenecking backend API requests. It groups temporal intervals (yearly, weekly) and aggregates crime counts.

### 4. Predictive modeling (`ml/`)
- Encapsulates modeling training pipelines, feature serialization, SHAP explainability analyses, and network centrality calculations.
