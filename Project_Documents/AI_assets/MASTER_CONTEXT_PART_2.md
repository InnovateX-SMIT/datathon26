# MASTER_CONTEXT_PART_2.md

# DATATHON PROJECT MASTER CONTEXT

## Part 2 — Technology Architecture, Engine Design, Dataset Understanding, Data Architecture

---

# PURPOSE OF THIS DOCUMENT

This document records all major technical decisions that have been discussed and agreed upon.

Future AI sessions should treat these decisions as the current baseline architecture.

Changes should only be made after discussion.

---

# TECHNOLOGY ARCHITECTURE STATUS

Current Status:

```text
Technology Architecture = 95% Locked
```

Reason:

The team has discussed all major layers.

Only minor implementation-level decisions remain.

---

# ARCHITECTURE PHILOSOPHY

The repository follows:

```text
Streamlit
↓
CSV
↓
Python Scripts
↓
H2O
```

The new platform will follow:

```text
Frontend
↓
Backend APIs
↓
Database
↓
Analytics Layer
↓
ML Layer
↓
Decision Support Layer
```

The new architecture is:

* Modular
* Scalable
* Multi-user
* Cloud-friendly
* Production-oriented

---

# FRONTEND LAYER

## Locked Stack

```text
Next.js
TypeScript
TailwindCSS
```

Reason:

* Modern
* Fast
* Professional
* Scalable
* Dashboard friendly

---

# VISUALIZATION STACK

## Recharts

Purpose:

* Line Charts
* Bar Charts
* Pie Charts
* Trend Analysis
* Executive Dashboards

Status:

LOCKED

---

# GEOSPATIAL STACK

## Leaflet

Purpose:

* Crime Maps
* District Maps
* Hotspots
* Police Station Views
* Beat-Level Views

Status:

LOCKED

---

# NETWORK VISUALIZATION STACK

## React Flow

Purpose:

* Criminal Relationship Graphs
* Criminal ↔ Crime ↔ Location Graphs
* Cluster Visualization
* Link Analysis

Status:

LOCKED

Important:

React Flow is a core technology because Criminal Network Intelligence is the primary WOW feature.

---

# BACKEND LAYER

## FastAPI

Purpose:

* Authentication APIs
* Crime APIs
* Analytics APIs
* Prediction APIs
* Network Intelligence APIs
* Recommendation APIs
* Report APIs

Reason:

```text
Python
+
ML
+
Analytics
+
Fast APIs
```

Status:

LOCKED

---

# DATABASE LAYER

## PostgreSQL

Purpose:

Primary data storage.

Reason:

* Relational
* Scalable
* Professional
* Multi-user
* Analytics Friendly

Repository used:

```text
CSV Storage
```

New Platform uses:

```text
PostgreSQL
```

Status:

LOCKED

---

# ORM LAYER

## SQLAlchemy

Reason:

* Stable
* Mature
* Battle-tested
* Large ecosystem

Status:

LOCKED

---

# MACHINE LEARNING STRATEGY

Repository uses:

```text
H2O AutoML
```

Decision:

Replace H2O.

Reason:

* Heavy
* Java Dependency
* Complex Deployment
* Harder Maintenance

---

# PRIMARY MODEL

## XGBoost

Purpose:

* Crime Risk Scoring
* Crime Type Prediction
* Repeat Offender Prediction
* Hotspot Prediction

Status:

LOCKED

---

# SECONDARY MODEL

## LightGBM

Purpose:

Fallback option.

Used only if:

* Better performance
* Better efficiency

Status:

BACKUP OPTION

---

# CORE ML LIBRARIES

Mandatory:

```text
Pandas
NumPy
Scikit-Learn
```

Status:

LOCKED

---

# EXPLAINABILITY LAYER

## SHAP

Purpose:

Explain predictions.

Example:

```text
Risk Score = 82%

Contributors:

Previous Crimes +40%
Area Risk +20%
Demographics +15%
```

Reason:

Predictions should be explainable.

Status:

LOCKED

---

# ANALYTICS STACK

## Pandas

Data Processing

---

## NumPy

Mathematics

---

## SciPy

Statistics

---

## GeoPandas

Geospatial Analytics

---

## NetworkX

Criminal Network Intelligence

Purpose:

* Centrality Analysis
* Graph Analysis
* Cluster Detection
* Link Analysis

Status:

LOCKED

---

# AI LAYER

Important Decision:

AI is NOT required for platform functionality.

Platform must work without AI APIs.

---

# AI Status

```text
Optional Enhancement Layer
```

NOT:

```text
Core Dependency
```

---

# Future AI Providers

Possible:

* OpenRouter
* OpenAI
* Gemini

Use Cases:

* Executive Reports
* Insight Summaries
* Recommendations

Only if needed.

---

# AUTHENTICATION

## JWT

Purpose:

Authentication

Status:

LOCKED

---

# ROLES

## Admin

Responsibilities:

* System Management
* User Management

---

## District Superintendent

Responsibilities:

* Strategic Decisions
* Resource Allocation

---

## Police Officer

Responsibilities:

* Local Crime Monitoring
* Criminal Intelligence

---

# DEPLOYMENT STRATEGY

Current Decision:

Lock architecture.

Do not lock providers yet.

Possible Providers:

Frontend:

* Vercel

Backend:

* Railway
* Render

Database:

* Neon
* Supabase PostgreSQL

Status:

Provider undecided.

Architecture approved.

---

# REJECTED TECHNOLOGIES

The following are intentionally rejected.

## H2O

Rejected.

---

## Java Runtime Dependency

Rejected.

---

## CSV Persistence

Rejected.

---

## Streamlit-Centered Architecture

Rejected.

---

## Monolithic Design

Rejected.

---

# ENGINE DESIGN

The platform is organized around engines.

NOT modules.

---

# ENGINE 1

## Crime Analytics Engine

Question Answered:

```text
What is happening?
```

---

### Feature 1

Crime Overview Dashboard

Includes:

* Total Crimes
* Total Victims
* Total Accused
* Trend Overview

---

### Feature 2

Temporal Analysis

Includes:

* Daily
* Weekly
* Monthly
* Yearly

---

### Feature 3

Geospatial Analysis

Hierarchy:

State
↓
District
↓
Police Station
↓
Beat

---

### Feature 4

Hotspot Detection

Includes:

* Heatmaps
* Crime Clusters

---

### Feature 5

Crime Category Analysis

Examples:

* Theft
* Assault
* Fraud
* Cybercrime

---

### Feature 6

Socio-Economic Correlation

Examples:

* Age vs Crime
* Occupation vs Crime
* Locality vs Crime

---

### Feature 7

Historical Comparison

Approved.

Examples:

* This Month vs Last Month
* This Year vs Last Year

---

# ENGINE 2

## Predictive Intelligence Engine

Question Answered:

```text
What is likely to happen?
```

---

### Feature 1

Repeat Offender Prediction

---

### Feature 2

Crime Risk Scoring

---

### Feature 3

Emerging Hotspot Prediction

---

### Feature 4

Crime Type Prediction

Missing from repository.

Will be built independently.

---

# Important Decision

Predictions focus primarily on:

```text
Locations
```

rather than individuals.

Reason:

More aligned with proactive policing.

---

# Risk Display

Both:

```text
Low
Medium
High
```

AND

```text
Percentage
```

---

# ENGINE 3

## Criminal Network Intelligence Engine

Primary WOW Feature

Question Answered:

```text
Who is connected to whom?
```

---

### Feature 1

Criminal Relationship Graph

---

### Feature 2

Repeat Association Detection

---

### Feature 3

Network Centrality Analysis

---

### Feature 4

Cluster Detection

---

### Feature 5

Location-Based Networks

---

# Important Decision

Network Graph Structure:

Approved:

```text
Criminal
↔
Crime
↔
Location
```

Rejected:

```text
Criminal
↔
Criminal only
```

Reason:

Richer intelligence.

---

# ENGINE 4

## Decision Support Engine

Question Answered:

```text
What should I do?
```

---

### Feature 1

Resource Allocation

---

### Feature 2

AI Recommendations

---

### Feature 3

Executive Reports

Secondary WOW Feature

---

### Feature 4

Trend Alerts

---

### Feature 5

Anomaly Detection

---

# Recommendation Strategy

Approved:

```text
Hybrid
```

Meaning:

Rules
+
AI Narratives

---

# Executive Reports

Approved:

Dashboard First

PDF Second

Reason:

Visual information is more effective.

---

# DATASET UNDERSTANDING

Repository datasets analyzed:

1. Crime Pattern Analysis
2. Crime Type Data
3. Criminal Profiling
4. Recidivism
5. Resource Allocation
6. Feedback

---

# IMPORTANT DISCOVERY

Repository datasets support:

* Analytics
* Profiling
* Prediction
* Allocation

Repository datasets do NOT strongly support:

```text
Criminal Network Intelligence
```

This becomes a major innovation opportunity.

---

# DATA ARCHITECTURE (CURRENT)

Core Entities Identified:

1. Crime Event
2. Location
3. Criminal Profile
4. Police Resource
5. Prediction
6. Network Intelligence
7. Recommendation
8. Alert
9. Report

These entities will become the foundation for future database design.

---

# IMPORTANT FUTURE DISCUSSION

Data Architecture is approximately:

```text
90% Complete
```

Remaining uncertainty depends on:

* Hackathon Dataset
* Organizer Information
* Additional Data Availability

---

END OF PART 2
