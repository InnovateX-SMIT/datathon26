# DATABASE_DESIGN.md

# Datathon 2026

## AI-Powered Crime Intelligence & Decision Support Platform

---

# Purpose

This document converts the approved Data Architecture into a relational database design.

This document defines:

* Tables
* Relationships
* Foreign Keys
* Query Strategy
* Indexing Strategy
* Scalability Considerations

This is the final planning layer before implementation.

---

# Database Philosophy

Technology:

```text
PostgreSQL
```

The database must support:

* Analytics
* Predictions
* Network Intelligence
* Decision Support
* Reporting

while remaining scalable for:

```text
100,000+
to
1,000,000+
records
```

---

# Database Overview

Core Tables:

```text
locations

police_stations

crime_events

criminals

victims

crime_participation

predictions

alerts

recommendations

reports

users
```

---

# Table: locations

Purpose:

Geographic hierarchy.

---

Columns:

```text
id (PK)

state

district

latitude

longitude

created_at

updated_at
```

---

Indexes:

```text
district

(latitude, longitude)
```

---

# Table: police_stations

Purpose:

Police administration units.

---

Columns:

```text
id (PK)

station_name

district

beat

location_id (FK)

officer_count

vehicle_count

equipment_count

capacity

availability

created_at

updated_at
```

---

Relationships:

```text
police_station
    │
    ▼
location
```

---

Indexes:

```text
district

station_name
```

---

# Table: crime_events

Purpose:

Central operational table.

---

Columns:

```text
id (PK)

crime_type

crime_category

crime_subcategory

description

severity

status

crime_date

crime_time

location_id (FK)

police_station_id (FK)

victim_count

accused_count

created_at

updated_at
```

---

Relationships:

```text
crime_event
    │
    ├── location
    └── police_station
```

---

Indexes:

```text
crime_date

crime_type

crime_category

location_id

police_station_id
```

---

# Table: criminals

Purpose:

Store offender information.

---

Columns:

```text
id (PK)

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

Indexes:

```text
risk_score

age

occupation
```

---

# Table: victims

Purpose:

Store victim information.

---

Columns:

```text
id (PK)

crime_event_id (FK)

gender

age

occupation

location_id (FK)

created_at

updated_at
```

---

Indexes:

```text
crime_event_id

age
```

---

# Table: crime_participation

Purpose:

Many-to-many bridge.

---

Columns:

```text
id (PK)

crime_event_id (FK)

criminal_id (FK)

role

created_at
```

---

Relationships:

```text
criminal
    │
    ▼
crime_participation
    │
    ▼
crime_event
```

---

Indexes:

```text
crime_event_id

criminal_id
```

---

# Table: predictions

Purpose:

Store model outputs.

---

Columns:

```text
id (PK)

crime_event_id (FK)

prediction_type

prediction_value

confidence_score

generated_at
```

---

Indexes:

```text
prediction_type

generated_at
```

---

# Table: alerts

Purpose:

Store intelligence alerts.

---

Columns:

```text
id (PK)

crime_event_id (FK)

alert_type

severity

message

status

created_at
```

---

Indexes:

```text
severity

status
```

---

# Table: recommendations

Purpose:

Decision support outputs.

---

Columns:

```text
id (PK)

crime_event_id (FK)

priority

recommendation_text

reason

status

created_at
```

---

Indexes:

```text
priority

status
```

---

# Table: reports

Purpose:

Executive intelligence reports.

---

Columns:

```text
id (PK)

title

summary

report_type

generated_at
```

---

Indexes:

```text
report_type

generated_at
```

---

# Table: users

Purpose:

Authentication & authorization.

---

Columns:

```text
id (PK)

name

email

password_hash

role

status

created_at

updated_at
```

---

Roles:

```text
ADMIN

SUPERINTENDENT

OFFICER
```

---

Indexes:

```text
email

role
```

---

# Entity Relationship Summary

```text
Location
    │
    ▼
Police Station
    │
    ▼
Crime Event
    │
    ├── Victim
    │
    ├── Prediction
    │
    ├── Alert
    │
    ├── Recommendation
    │
    └── Crime Participation
              │
              ▼
           Criminal
```

---

# Network Intelligence Query Path

Approved model:

```text
Criminal
↔
Crime Event
↔
Location
```

Implementation:

```text
criminals
↓
crime_participation
↓
crime_events
↓
locations
```

---

# Analytics Query Strategy

Examples:

### Crimes by District

```text
crime_events
JOIN locations
```

---

### Crimes by Police Station

```text
crime_events
JOIN police_stations
```

---

### Crime Trends

```text
GROUP BY crime_date
```

---

### Crime Categories

```text
GROUP BY crime_category
```

---

# Prediction Query Strategy

Examples:

```text
crime_event
↓
prediction
```

Supports:

* Risk Scoring
* Hotspot Prediction
* Crime Type Prediction

---

# Recommendation Query Strategy

Examples:

```text
crime_event
↓
recommendation
```

Supports:

* Resource Allocation
* Strategic Planning
* Intervention Suggestions

---

# Scalability Considerations

Expected Scale:

```text
100,000+
Records
```

Target Scale:

```text
1,000,000+
Records
```

Database must support:

* Pagination
* Filtering
* Indexing
* Aggregation Queries

---

# Future Enhancements

Possible additions:

```text
audit_logs

activity_history

model_registry

feedback

notifications
```

These are optional and not required for V1.

---

# Current Status

```text
Database Design
≈ 95% Complete
```

Pending:

```text
Official Schema Release

Catalyst Data Layer Review
```

After those are available:

```text
Database Design
→ Finalized
```

---

END OF DOCUMENT
