# SYSTEM_ARCHITECTURE.md

# Datathon 2026

## AI-Powered Crime Intelligence & Decision Support Platform

---

# Purpose

This document defines the overall system architecture of the platform.

It describes:

* Major system layers
* Module boundaries
* Service responsibilities
* Data flow
* Integration points

This document is technology-aware but implementation-independent.

---

# Architecture Philosophy

The platform follows:

```text
Data
↓
Processing
↓
Intelligence
↓
Decision Support
↓
Visualization
```

The goal is not merely to visualize crime data.

The goal is to transform crime data into actionable intelligence.

---

# High Level Architecture

```text
Frontend
    │
    ▼
FastAPI Backend
    │
    ▼
Service Layer
    │
    ▼
Database + Analytics + ML
```

---

# System Layers

```text
Presentation Layer
↓
API Layer
↓
Business Logic Layer
↓
Analytics Layer
↓
ML Layer
↓
Data Layer
```

---

# Layer 1: Presentation Layer

Technology:

```text
Next.js
TypeScript
TailwindCSS
```

Purpose:

Provide user interface.

---

# Main Pages

```text
Dashboard

Crime Analytics

Geo Intelligence

Predictive Intelligence

Network Intelligence

Decision Support

Alerts

Executive Reports

Admin
```

---

# Responsibilities

* Data Visualization
* User Interaction
* Filters
* Maps
* Graphs
* Reports
* Navigation

---

# Layer 2: API Layer

Technology:

```text
FastAPI
```

Purpose:

Expose platform capabilities.

---

# API Groups

```text
Authentication APIs

Crime APIs

Analytics APIs

Prediction APIs

Network APIs

Recommendation APIs

Alert APIs

Report APIs

Admin APIs
```

---

# Responsibilities

* Request Validation
* Authentication
* Authorization
* Response Formatting

---

# Layer 3: Business Logic Layer

Purpose:

Core platform intelligence.

This layer contains actual application logic.

---

# Modules

```text
Crime Service

Geo Service

Prediction Service

Network Service

Recommendation Service

Alert Service

Report Service
```

---

# Responsibilities

Examples:

```text
Calculate trends

Generate insights

Detect hotspots

Allocate resources

Generate reports
```

---

# Layer 4: Analytics Layer

Purpose:

Transform raw data into intelligence.

---

# Technologies

```text
Pandas

NumPy

SciPy

GeoPandas
```

---

# Capabilities

```text
Trend Analysis

Crime Distribution

Temporal Analysis

Geospatial Analysis

Correlation Analysis

Historical Comparison
```

---

# Layer 5: Machine Learning Layer

Purpose:

Prediction and intelligence generation.

---

# Technologies

```text
XGBoost

Scikit-Learn

SHAP

NetworkX
```

---

# Models

```text
Crime Type Prediction

Crime Risk Prediction

Repeat Offender Prediction

Hotspot Prediction
```

---

# Explainability

Technology:

```text
SHAP
```

Purpose:

Explain why predictions were made.

---

# Layer 6: Data Layer

Technology:

```text
PostgreSQL
```

Purpose:

Store all operational data.

---

# Stored Data

```text
Crimes

Criminals

Victims

Locations

Police Stations

Predictions

Alerts

Recommendations

Reports
```

---

# Core Engines

The platform is organized around four engines.

---

# Engine 1

## Crime Analytics Engine

Question:

```text
What is happening?
```

Features:

```text
Crime Trends

Category Analysis

Temporal Analysis

Historical Analysis

District Analysis
```

---

# Engine 2

## Predictive Intelligence Engine

Question:

```text
What is likely to happen?
```

Features:

```text
Risk Prediction

Crime Type Prediction

Hotspot Prediction

Repeat Offender Prediction
```

---

# Engine 3

## Criminal Network Intelligence Engine

Primary WOW Feature.

Question:

```text
Who is connected?
```

Features:

```text
Link Analysis

Association Discovery

Network Graphs

Cluster Detection

Centrality Analysis
```

---

# Approved Network Model

```text
Criminal
↔
Crime Event
↔
Location
```

---

# Engine 4

## Decision Support Engine

Question:

```text
What should be done?
```

Features:

```text
Recommendations

Resource Allocation

Alerts

Executive Intelligence
```

---

# Module Structure

## Frontend

```text
frontend/

├── dashboard/
├── analytics/
├── geo/
├── prediction/
├── network/
├── decision-support/
├── alerts/
├── reports/
├── admin/
├── shared/
└── auth/
```

---

## Backend

```text
backend/

├── auth/
├── crimes/
├── analytics/
├── geo/
├── prediction/
├── network/
├── recommendations/
├── alerts/
├── reports/
├── admin/
└── shared/
```

---

## Analytics

```text
analytics/

├── trends/
├── hotspot/
├── correlations/
├── temporal/
└── geo/
```

---

## ML

```text
ml/

├── crime_prediction/
├── hotspot_prediction/
├── recidivism/
├── explainability/
└── network_analysis/
```

---

# Data Flow

## Crime Analytics Flow

```text
Database
↓
Analytics Engine
↓
API
↓
Frontend
```

---

## Prediction Flow

```text
Database
↓
ML Models
↓
Predictions
↓
API
↓
Frontend
```

---

## Network Intelligence Flow

```text
Criminals
+
Crimes
+
Locations
↓
NetworkX
↓
Graph Intelligence
↓
API
↓
React Flow
```

---

## Decision Support Flow

```text
Analytics
+
Predictions
+
Network Intelligence
↓
Recommendation Engine
↓
Alerts
↓
Reports
```

---

# Security Architecture

Authentication:

```text
JWT
```

Roles:

```text
Admin

District Superintendent

Police Officer
```

Authorization:

```text
Role Based Access Control
```

---

# Deployment Architecture

Mandatory Platform:

```text
Zoho Catalyst
```

Current Plan:

```text
Frontend
↓
Catalyst Hosting

Backend
↓
Catalyst Functions

Database
↓
Catalyst Data Store
or PostgreSQL Integration
```

Final deployment architecture may be refined after Catalyst workshops.

---

# Non Functional Goals

Scalability:

```text
100,000+
Records
```

Target:

```text
1M+
Synthetic Records
```

---

# Reliability

System should support:

```text
Near Real Time Analytics
```

as specified by the challenge.

---

# Maintainability

Architecture should support:

```text
New Crime Types

New Models

New Reports

New Analytics
```

without redesign.

---

# Current Status

```text
System Architecture
≈ 95% Complete
```

Remaining dependency:

```text
Official Datathon Schema

Catalyst Workshop Details
```

---

END OF DOCUMENT
