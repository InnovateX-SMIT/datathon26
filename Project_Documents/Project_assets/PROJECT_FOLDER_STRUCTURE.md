# PROJECT_FOLDER_STRUCTURE.md

# Datathon 2026

## AI-Powered Crime Intelligence & Decision Support Platform

---

# Purpose

This document defines the official repository structure for the project.

The structure is designed to support:

* Team Collaboration
* AI-Assisted Development
* Scalability
* Maintainability
* Clear Separation of Concerns

This structure is considered the V1 project organization.

---

# Architecture Overview

```text
project-root/
│
├── frontend/
├── backend/
├── analytics/
├── ml/
├── database/
├── docs/
├── scripts/
├── datasets/
├── infrastructure/
└── .github/
```

---

# Root Structure

```text
project-root/
│
├── frontend/
├── backend/
├── analytics/
├── ml/
├── database/
├── docs/
├── scripts/
├── datasets/
├── infrastructure/
├── .github/
│
├── docker-compose.yml
├── README.md
├── .gitignore
└── LICENSE
```

---

# Frontend

Technology:

```text
Next.js
TypeScript
TailwindCSS
```

---

Structure:

```text
frontend/
│
├── app/
│
├── components/
│
├── features/
│
├── services/
│
├── hooks/
│
├── lib/
│
├── types/
│
├── constants/
│
├── assets/
│
└── public/
```

---

# Frontend Features

```text
features/
│
├── dashboard/
├── analytics/
├── geo/
├── prediction/
├── network/
├── decision-support/
├── alerts/
├── reports/
├── admin/
└── auth/
```

---

# Shared Components

```text
components/
│
├── charts/
├── maps/
├── graphs/
├── tables/
├── layout/
├── forms/
└── ui/
```

---

# Backend

Technology:

```text
FastAPI
SQLAlchemy
JWT
```

---

Structure:

```text
backend/
│
├── app/
│
├── api/
├── services/
├── models/
├── schemas/
├── repositories/
├── middleware/
├── core/
├── utils/
└── tests/
```

---

# API Modules

```text
api/
│
├── auth/
├── crimes/
├── analytics/
├── geo/
├── predictions/
├── network/
├── recommendations/
├── alerts/
├── reports/
└── admin/
```

---

# Service Layer

```text
services/
│
├── crime_service.py
├── analytics_service.py
├── geo_service.py
├── prediction_service.py
├── network_service.py
├── recommendation_service.py
├── alert_service.py
└── report_service.py
```

---

# Database Models

```text
models/
│
├── user.py
├── crime.py
├── criminal.py
├── victim.py
├── location.py
├── police_station.py
├── prediction.py
├── alert.py
├── recommendation.py
└── report.py
```

---

# Analytics Layer

Purpose:

Business analytics and statistical processing.

---

Structure:

```text
analytics/
│
├── crime_analysis/
├── temporal_analysis/
├── geo_analysis/
├── hotspot_detection/
├── correlation_analysis/
└── reporting/
```

---

# Crime Analysis

```text
crime_analysis/
│
├── category_analysis.py
├── trend_analysis.py
├── district_analysis.py
└── station_analysis.py
```

---

# Temporal Analysis

```text
temporal_analysis/
│
├── yearly.py
├── monthly.py
├── weekly.py
└── daily.py
```

---

# Geo Analysis

```text
geo_analysis/
│
├── hotspot.py
├── heatmap.py
├── district_map.py
└── station_map.py
```

---

# Machine Learning Layer

Purpose:

Prediction and intelligence generation.

---

Structure:

```text
ml/
│
├── crime_prediction/
├── hotspot_prediction/
├── offender_prediction/
├── explainability/
└── network_analysis/
```

---

# Crime Prediction

```text
crime_prediction/
│
├── train.py
├── predict.py
├── evaluate.py
└── model.pkl
```

---

# Hotspot Prediction

```text
hotspot_prediction/
│
├── train.py
├── predict.py
└── evaluate.py
```

---

# Offender Prediction

```text
offender_prediction/
│
├── train.py
├── predict.py
└── evaluate.py
```

---

# Explainability

```text
explainability/
│
├── shap_analysis.py
└── feature_importance.py
```

---

# Network Intelligence

```text
network_analysis/
│
├── graph_builder.py
├── cluster_detection.py
├── centrality.py
├── link_analysis.py
└── network_metrics.py
```

---

# Database Layer

Purpose:

Database definitions and migrations.

---

Structure:

```text
database/
│
├── migrations/
├── seed/
├── schemas/
└── backups/
```

---

# Dataset Layer

Purpose:

Synthetic and official datasets.

---

Structure:

```text
datasets/
│
├── raw/
├── processed/
├── synthetic/
└── samples/
```

---

# Synthetic Data

```text
synthetic/
│
├── crimes/
├── criminals/
├── victims/
├── locations/
└── stations/
```

---

# Documentation

Purpose:

Project knowledge base.

---

Structure:

```text
docs/
│
├── architecture/
├── planning/
├── api/
├── database/
├── deployment/
├── presentations/
└── meeting-notes/
```

---

# Planning Documents

```text
planning/
│
├── PHASE_0_BLUEPRINT.md
├── DATA_ARCHITECTURE.md
├── SYSTEM_ARCHITECTURE.md
├── DATABASE_DESIGN.md
├── PROJECT_FOLDER_STRUCTURE.md
└── FUTURE_PHASES.md
```

---

# Scripts

Purpose:

Automation.

---

Structure:

```text
scripts/
│
├── generate_synthetic_data.py
├── seed_database.py
├── train_models.py
├── export_reports.py
└── cleanup.py
```

---

# Infrastructure

Purpose:

Deployment.

---

Structure:

```text
infrastructure/
│
├── catalyst/
├── docker/
├── monitoring/
└── environments/
```

---

# Catalyst

```text
catalyst/
│
├── deployment/
├── functions/
└── configs/
```

---

# GitHub

```text
.github/
│
├── workflows/
└── ISSUE_TEMPLATE/
```

---

# Branch Strategy

Main Branches

```text
main

develop
```

---

Feature Branches

Examples:

```text
phase-0-blueprint

phase-1-auth-layout

phase-1A-data-foundation

phase-2-dashboard

phase-3-crime-analytics

phase-4-geo-intelligence

phase-5-predictive-intelligence

phase-6A-network-modeling

phase-6B-network-visualization

phase-6C-network-analytics
```

---

# AI Development Philosophy

The structure is intentionally modular.

Reason:

```text
One Phase
↓
One Module
↓
One AI Prompt
↓
One Deliverable
```

This improves:

* Reviewability
* Testing
* Collaboration
* AI-Agent Accuracy

---

# Current Status

```text
Project Folder Structure
≈ 95% Complete
```

Pending:

```text
Catalyst Workshop Details

Official Schema Release
```

After those are available:

```text
Project Folder Structure
→ Finalized
```

---

END OF DOCUMENT
