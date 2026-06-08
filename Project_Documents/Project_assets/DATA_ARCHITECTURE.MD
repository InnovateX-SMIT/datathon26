# DATA_ARCHITECTURE.md

# Datathon 2026

## AI-Powered Crime Intelligence & Decision Support Platform

---

# Purpose

This document defines the business entities, relationships, and data architecture of the platform.

This document is created before database implementation.

It represents the real-world crime intelligence domain and acts as the foundation for:

* Database Design
* Backend APIs
* Analytics Engine
* Predictive Intelligence Engine
* Criminal Network Intelligence Engine
* Decision Support Engine
* Executive Reporting

---

# Architecture Philosophy

The platform follows:

```text
Real World Domain
↓
Entities
↓
Relationships
↓
Database
↓
APIs
↓
Analytics
↓
Visualizations
```

The goal is to model how crime data actually exists within law enforcement systems.

---

# Core Entities

The platform is built around ten primary entities.

---

# Entity 1: Crime Event

## Purpose

Represents an individual crime occurrence.

This is the central entity of the system.

Every major feature ultimately connects to a Crime Event.

---

## Example

```text
Theft occurred on 12 June 2026
District: Bengaluru Urban
Police Station: Whitefield
Victims: 2
Accused: 1
```

---

## Attributes

```text
crime_id
crime_type
crime_category
crime_subcategory

description

severity

status

crime_date
crime_time

location_id

victim_count
accused_count

created_at
updated_at
```

---

# Entity 2: Criminal

## Purpose

Represents an accused individual involved in one or more crimes.

Supports:

* Criminal Profiling
* Repeat Offender Detection
* Risk Scoring
* Criminal Network Intelligence

---

## Attributes

```text
criminal_id

name
gender
age

occupation

caste

risk_score

status

created_at
updated_at
```

---

# Entity 3: Victim

## Purpose

Represents individuals affected by crimes.

Supports:

* Victim Analysis
* Demographic Insights
* Crime Impact Studies

---

## Attributes

```text
victim_id

gender
age

occupation

location_id

created_at
updated_at
```

---

# Entity 4: Location

## Purpose

Represents geographical hierarchy.

Supports:

* Maps
* Geo Intelligence
* Hotspots
* Heatmaps
* Trend Analysis

---

## Attributes

```text
location_id

state

district

latitude
longitude

created_at
updated_at
```

---

# Entity 5: Police Station

## Purpose

Represents police administrative units.

Supports:

* Resource Allocation
* Jurisdiction Mapping
* Operational Intelligence

---

## Attributes

```text
station_id

station_name

district

beat

latitude
longitude

officer_count

vehicle_count

equipment_count

capacity

availability

created_at
updated_at
```

---

# Entity 6: Crime Participation

## Purpose

Bridge entity connecting Criminals and Crime Events.

Allows:

* One Criminal → Many Crimes
* One Crime → Many Criminals

This entity powers Network Intelligence.

---

## Attributes

```text
participation_id

crime_id

criminal_id

role

created_at
```

---

# Entity 7: Prediction

## Purpose

Stores outputs from predictive models.

Supports:

* Risk Prediction
* Crime Type Prediction
* Hotspot Prediction
* Repeat Offender Prediction

---

## Attributes

```text
prediction_id

crime_id

prediction_type

prediction_value

confidence_score

generated_at
```

---

# Entity 8: Alert

## Purpose

Stores generated alerts.

Supports:

* Trend Alerts
* Risk Alerts
* Hotspot Alerts
* Anomaly Alerts

---

## Attributes

```text
alert_id

alert_type

severity

message

status

created_at
```

---

# Entity 9: Recommendation

## Purpose

Stores decision-support recommendations.

Supports:

* Resource Allocation
* Strategic Planning
* Intervention Suggestions

---

## Attributes

```text
recommendation_id

priority

recommendation_text

reason

status

created_at
```

---

# Entity 10: Report

## Purpose

Stores executive intelligence reports.

Supports:

* Superintendent Reviews
* Strategic Meetings
* PDF Exports
* Executive Dashboards

---

## Attributes

```text
report_id

title

summary

generated_at

report_type
```

---

# Entity Relationships

---

## Relationship 1

```text
Location
    │
    ▼
Crime Event
```

One Location

can contain

Many Crime Events

---

## Relationship 2

```text
Police Station
    │
    ▼
Crime Event
```

One Police Station

handles

Many Crime Events

---

## Relationship 3

```text
Crime Event
    │
    ▼
Victim
```

One Crime

can involve

Many Victims

---

## Relationship 4

```text
Crime Event
    │
    ▼
Crime Participation
    │
    ▼
Criminal
```

Many-to-Many Relationship

---

## Relationship 5

```text
Crime Event
    │
    ▼
Prediction
```

One Crime

can have

Multiple Predictions

---

## Relationship 6

```text
Crime Event
    │
    ▼
Alert
```

One Crime

can generate

Multiple Alerts

---

## Relationship 7

```text
Crime Event
    │
    ▼
Recommendation
```

One Crime

can generate

Multiple Recommendations

---

## Relationship 8

```text
Crime Event
    │
    ▼
Report
```

Crime intelligence contributes to reports.

---

# Criminal Network Intelligence Model

This is the primary WOW feature.

---

## Approved Graph Structure

```text
Criminal
     │
     ▼
Crime Event
     │
     ▼
Location
```

---

## Example

```text
Criminal A
     │
     ▼
Burglary Case
     │
     ▼
Whitefield

Criminal B
     │
     ▼
Burglary Case
```

Result:

```text
Criminal A
↔
Criminal B
```

association discovered.

---

# Network Analytics Features

Supports:

```text
Link Analysis

Cluster Detection

Centrality Analysis

Repeat Associations

Investigation Intelligence
```

---

# Intelligence Layer

Built on top of operational data.

---

## Inputs

```text
Crime Events

Criminals

Victims

Locations

Police Stations
```

---

## Generated Intelligence

```text
Predictions

Alerts

Recommendations

Reports

Network Insights
```

---

# Data Flow

```text
Synthetic Dataset
        │
        ▼
PostgreSQL
        │
        ▼
Backend APIs
        │
        ▼
Analytics Layer
        │
        ▼
Prediction Layer
        │
        ▼
Network Intelligence Layer
        │
        ▼
Decision Support Layer
        │
        ▼
Frontend Dashboards
```

---

# Future Considerations

After official schema release:

Review:

* Additional entities
* Additional relationships
* Additional attributes

Update this document accordingly.

---

# Current Status

```text
Data Architecture
≈ 95% Complete
```

Remaining dependency:

```text
Official Datathon Schema
```

After schema release:

```text
Data Architecture
→ Finalized
```

---

END OF DOCUMENT
