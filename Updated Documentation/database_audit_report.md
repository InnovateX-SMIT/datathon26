# Database Audit Report: AI-Driven Crime Analytics Platform

This document presents a comprehensive technical audit of the implemented SQLite database (`crime_intel.db`), SQLAlchemy ORM models, and database access layers against the official references:
1. [Police_FIR_Schema.sql](file:///Users/krishanand/datathon26/assets/Police_FIR_Schema.sql) (Official SQL Schema)
2. [Police_FIR_ER_Diagram.pdf](file:///Users/krishanand/datathon26/Project_Documents/Police_FIR_ER_Diagram.pdf) (Official ER Diagram)

---

## Executive Summary

| Audit Metric | Score | Rating / Status |
| :--- | :---: | :--- |
| **Overall Database Score** | **40 / 100** | Needs Immediate Refactoring |
| **SQL Schema Compliance** | **5 / 100** | Non-Compliant (Entirely Different Structures) |
| **ER Diagram Compliance** | **5 / 100** | Non-Compliant (Missing/Altered Entities) |
| **Security Score** | **50 / 100** | Moderate (Exposure of Secrets & Non-Standard Hashing) |
| **Performance Score** | **60 / 100** | Acceptable (Requires Composite Indexing & Eager Loading) |
| **Scalability Score** | **45 / 100** | Poor (SQLite File Locking & Catalyst Row Limits) |
| **Production Readiness** | **35 / 100** | Not Ready for Final Submission |

> [!WARNING]
> **Critical Schema Deviation**: There is a complete misalignment between the implemented SQLite database and the official MySQL/PDF specifications. The official documents describe a highly normalized relational system of **26 tables**, whereas the implementation contains a highly denormalized prototype system of **14 tables** designed to support ML graph features.

---

## Findings

### 🔴 Critical Findings

#### 1. Complete Schema & ER Diagram Non-Compliance (Mismatched Tables)
* **Description**: The implemented database structure deviates entirely from the official SQL schema and ER diagram. It has only 14 tables instead of the expected 26 tables.
* **Impact**: Completely invalidates compliance with the official challenge deliverables. Bypasses core operational tables, legal lookup masters (Acts, Sections), courts, and employee registries.
* **Evidence**: [backend/models/__init__.py](file:///Users/krishanand/datathon26/backend/models/__init__.py) lists 14 tables (e.g. `crime_events`, `criminals`, `victims`) which do not exist in the official MySQL script.
* **Affected File(s)**: All files in [backend/models/](file:///Users/krishanand/datathon26/backend/models/)
* **Recommended Fix**: Re-implement ORM models according to the 26 tables defined in [Police_FIR_Schema.sql](file:///Users/krishanand/datathon26/assets/Police_FIR_Schema.sql).

#### 2. Hardcoded JWT Secret Key in Configurations
* **Description**: The platform's JWT signature secret key is hardcoded directly in the settings class.
* **Impact**: Exposes the system to unauthorized authentication bypass. Attackers can forge JWT payloads to gain administrator access.
* **Evidence**: [backend/core/config.py#L12](file:///Users/krishanand/datathon26/backend/core/config.py#L12): `SECRET_KEY: str = Field(default="supersecretjwtkeyforcrimeplatform2026!", env="SECRET_KEY")`
* **Affected File(s)**: [backend/core/config.py](file:///Users/krishanand/datathon26/backend/core/config.py)
* **Recommended Fix**: Remove the hardcoded fallback string. Retrieve the secret key strictly from environment variables: `os.environ["SECRET_KEY"]` and fail fast at startup if it is missing.

#### 3. Database Write Locking under Concurrent Loads (SQLite Limitation)
* **Description**: The dev database runs on SQLite (`crime_intel.db`), which implements database-level write locking.
* **Impact**: Under concurrent usage (e.g., 5,000+ active users, multiple analysts executing predictions or logging events), write transactions will block each other, raising `sqlite3.OperationalError: database is locked` exceptions.
* **Evidence**: [backend/core/database.py#L6-L10](file:///Users/krishanand/datathon26/backend/core/database.py#L6-L10) instantiates a local SQLite engine.
* **Affected File(s)**: [backend/core/database.py](file:///Users/krishanand/datathon26/backend/core/database.py), [backend/core/config.py](file:///Users/krishanand/datathon26/backend/core/config.py)
* **Recommended Fix**: Migrate database engine to PostgreSQL in production and configure connection pooling.

---

### 🟠 High Findings

#### 1. SQLAlchemy to ZCQL Compatibility Blockers (Catalyst Data Store Migration)
* **Description**: The database access layer is built using SQLAlchemy ORM. However, the target platform, Zoho Catalyst Data Store, does not support ORMs and requires ZCQL (Zoho Catalyst Query Language) strings.
* **Impact**: The application will crash on AppSail if deployed in its current form. ZCQL is restricted to a maximum of 4 JOIN clauses, which will break multi-join relationships.
* **Evidence**: [backend/repositories/*](file:///Users/krishanand/datathon26/backend/repositories/) heavily relies on SQLAlchemy sessions and object querying.
* **Affected File(s)**: All files in [backend/repositories/](file:///Users/krishanand/datathon26/backend/repositories/)
* **Recommended Fix**: Refactor repositories to instantiate the `zcatalyst_sdk` and execute raw query strings via the `zcql` service, denormalizing tables as necessary to respect the 4-JOIN limit.

#### 2. Catalyst Development Environment Row Limits Exceeded
* **Description**: The default Catalyst development environment limits tables to a maximum of 5,000 rows. The seed dataset has 50,000 crime records, 50,000 criminals, and 50,000 victims.
* **Impact**: Seeding the full dataset during deployment will trigger `403 API Limit Reached` errors.
* **Evidence**: Seeding code in [database/seed/seed_crimes.py](file:///Users/krishanand/datathon26/database/seed/seed_crimes.py) imports 50,000 records.
* **Affected File(s)**: [database/seed/seed_crimes.py](file:///Users/krishanand/datathon26/database/seed/seed_crimes.py)
* **Recommended Fix**: Switch to the Catalyst Production Environment, or store the static dataset as CSV files in **Catalyst Stratus** object storage and load them into AppSail cache memory at startup.

#### 3. CPU-Intense Network Graph Traversals in Main Thread (GIL Blocking)
* **Description**: Building the NetworkX graph cache on startup and computing betweenness centrality are CPU-intense operations executed on the main web execution thread.
* **Impact**: Halts the Python Global Interpreter Lock (GIL), blocking all other incoming HTTP REST requests and causing request timeouts.
* **Evidence**: [backend/app/main.py#L182-L188](file:///Users/krishanand/datathon26/backend/app/main.py#L182-L188) and [backend/services/network_analytics_service.py](file:///Users/krishanand/datathon26/backend/services/network_analytics_service.py).
* **Affected File(s)**: [backend/app/main.py](file:///Users/krishanand/datathon26/backend/app/main.py), [backend/services/network_analytics_service.py](file:///Users/krishanand/datathon26/backend/services/network_analytics_service.py)
* **Recommended Fix**: Offload graph centrality calculations to background job routines (**Catalyst Job Pools**) and write results to a distributed cache (**Zoho Catalyst Cache**).

#### 4. Custom JWT Authentication Bypassing Zoho Native Security
* **Description**: User login and role verification are managed locally via custom JWT tokens instead of Zoho Catalyst's native Authentication service.
* **Impact**: Bypasses the Zoho Catalyst native identity verification and dashboard role mapping, causing security audit failures.
* **Evidence**: [backend/api/auth/router.py](file:///Users/krishanand/datathon26/backend/api/auth/router.py) and [backend/core/security.py](file:///Users/krishanand/datathon26/backend/core/security.py).
* **Affected File(s)**: [backend/api/auth/router.py](file:///Users/krishanand/datathon26/backend/api/auth/router.py), [backend/core/security.py](file:///Users/krishanand/datathon26/backend/core/security.py)
* **Recommended Fix**: Replace the custom JWT validation middleware with Zoho Catalyst Hosted Authentication handlers.

---

### 🟡 Medium Findings

#### 1. Transitive Normalization Violations (3NF Failure)
* **Description**: Genders, castes, and occupations are stored as raw strings in the `criminals` and `victims` tables. Similarly, `crime_events` stores `crime_type`, `crime_category`, and `crime_subcategory` directly as text.
* **Impact**: High risk of data anomalies, inconsistent spelling, and inefficient space utilization.
* **Evidence**: [backend/models/criminal.py](file:///Users/krishanand/datathon26/backend/models/criminal.py) and [backend/models/victim.py](file:///Users/krishanand/datathon26/backend/models/victim.py).
* **Affected File(s)**: [backend/models/criminal.py](file:///Users/krishanand/datathon26/backend/models/criminal.py), [backend/models/victim.py](file:///Users/krishanand/datathon26/backend/models/victim.py), [backend/models/crime.py](file:///Users/krishanand/datathon26/backend/models/crime.py)
* **Recommended Fix**: Re-normalize values by mapping them to foreign keys pointing to official master tables (`CasteMaster`, `OccupationMaster`, `ReligionMaster`).

#### 2. Age Attribute Data Type Mismatch (Float vs Integer)
* **Description**: Age is defined as `Float` in the SQLite database and ORM models for `criminals` and `victims`. The official references specify it as `INT` (`AgeYear INT`).
* **Impact**: Permits invalid decimal values (e.g. `25.5`) in the database.
* **Evidence**: [backend/models/criminal.py#L11](file:///Users/krishanand/datathon26/backend/models/criminal.py#L11) (`age = Column(Float, index=True, nullable=True)`) and [backend/models/victim.py#L11](file:///Users/krishanand/datathon26/backend/models/victim.py#L11).
* **Affected File(s)**: [backend/models/criminal.py](file:///Users/krishanand/datathon26/backend/models/criminal.py), [backend/models/victim.py](file:///Users/krishanand/datathon26/backend/models/victim.py)
* **Recommended Fix**: Modify the ORM definitions to use `Integer` type for all age columns.

#### 3. Missing Unique Constraints in Crime Junction Table
* **Description**: The `crime_participation` bridge table joins `crime_events` and `criminals` but lacks a unique index or composite primary key constraint on `(crime_event_id, criminal_id)`.
* **Impact**: Allows duplicate rows associating the same suspect with the same crime incident, leading to duplicate nodes in graph analytics.
* **Evidence**: [backend/models/crime_participation.py](file:///Users/krishanand/datathon26/backend/models/crime_participation.py) lacks a unique constraint or composite key.
* **Affected File(s)**: [backend/models/crime_participation.py](file:///Users/krishanand/datathon26/backend/models/crime_participation.py)
* **Recommended Fix**: Add a composite primary key or a unique constraint on `(crime_event_id, criminal_id)`.

#### 4. N+1 Query Performance Anomalies in Analytical Endpoints
* **Description**: Relationships (e.g. `location`, `police_station`) are defined as lazy-loaded by default.
* **Impact**: Querying lists of crime events triggers multiple sequential SQL SELECT calls to fetch related location or station objects.
* **Evidence**: [backend/models/crime.py#L30-L31](file:///Users/krishanand/datathon26/backend/models/crime.py#L30-L31) uses lazy loading.
* **Affected File(s)**: [backend/models/crime.py](file:///Users/krishanand/datathon26/backend/models/crime.py), [backend/repositories/prediction_repository.py](file:///Users/krishanand/datathon26/backend/repositories/prediction_repository.py)
* **Recommended Fix**: Enforce eager loading (`joinedload` or `selectinload`) in the repository methods.

---

### 🟢 Low Findings

#### 1. Transitive Redundant Columns in Police Stations Table
* **Description**: The `police_stations` table stores both `district` (string) and a `location_id` reference which links to a location that also contains a `district` column.
* **Impact**: Introduces duplicate fields. If a station's `district` is updated but the linked location's `district` remains unchanged, it creates data mismatches.
* **Evidence**: [backend/models/police_station.py#L10-L12](file:///Users/krishanand/datathon26/backend/models/police_station.py#L10-L12).
* **Affected File(s)**: [backend/models/police_station.py](file:///Users/krishanand/datathon26/backend/models/police_station.py)
* **Recommended Fix**: Remove `district` from `police_stations` and resolve the district name dynamically through the `location_id` relationship.

#### 2. Inconsistent Naming and Column Casing
* **Description**: The implemented SQLAlchemy database schema uses `camelCase`/`snake_case` (e.g., `crime_type`, `crime_date`) while the official reference schema uses `PascalCase` (e.g., `CrimeNo`, `CrimeRegisteredDate`).
* **Impact**: Makes raw ZCQL/SQL mapping writing confusing for developers.
* **Evidence**: [backend/models/crime.py](file:///Users/krishanand/datathon26/backend/models/crime.py) columns vs [Police_FIR_Schema.sql](file:///Users/krishanand/datathon26/assets/Police_FIR_Schema.sql).
* **Affected File(s)**: All files in [backend/models/](file:///Users/krishanand/datathon26/backend/models/)
* **Recommended Fix**: Rename ORM model attributes to match the casing of the official SQL schema.

#### 3. Non-Standard Hashing Context for Passwords
* **Description**: Passwords are saved using `sha256_crypt` hashing instead of the modern industry standard `bcrypt`.
* **Impact**: The hashing algorithm is less resilient to modern high-speed brute-force attacks.
* **Evidence**: [backend/core/security.py#L8](file:///Users/krishanand/datathon26/backend/core/security.py#L8): `CryptContext(schemes=["sha256_crypt"])`
* **Affected File(s)**: [backend/core/security.py](file:///Users/krishanand/datathon26/backend/core/security.py)
* **Recommended Fix**: Switch to standard `bcrypt` hashing since the target runtime is Python 3.10, which does not suffer from Python 3.14 preview bugs.

---

## SQL Schema Mismatches

The implemented database deviates substantially from [Police_FIR_Schema.sql](file:///Users/krishanand/datathon26/assets/Police_FIR_Schema.sql).

| Implemented Table | Expected Table (Official SQL Schema) | Schema Mismatch Details |
| :--- | :--- | :--- |
| **`crime_events`** | `CaseMaster` | Lacks columns: `CrimeNo`, `CaseNo`, `PolicePersonID`, `CaseCategoryID`, `GravityOffenceID`, `CrimeMajorHeadID`, `CrimeMinorHeadID`, `CaseStatusID`, `CourtID`, `IncidentFromDate`, `IncidentToDate`, `InfoReceivedPSDate`, `BriefFacts` (LONGTEXT). Implements string type attributes instead of master table lookups. |
| **`locations`** | `State`, `District` | Flattens state and district into one record. |
| **`police_stations`** | `Unit`, `UnitType` | Lacks unit hierarchy, parent units, and unit type mapping. Flattens station attributes. |
| **`criminals`** | `Accused` | Lacks `PersonID` (A1, A2 representation). Adds `risk_score` (not in schema). |
| **`victims`** | `Victim` | Lacks `VictimName` (VARCHAR) and `VictimPolice` (flag). Adds `occupation` and `location_id`. |
| **`crime_participation`** | `Accused` | Replaces direct FK association in `Accused` with a separate M2M junction table. |
| *Missing* | `ComplainantDetails` | Table completely missing in implementation. |
| *Missing* | `ArrestSurrender` | Table completely missing in implementation. |
| *Missing* | `ChargesheetDetails` | Table completely missing in implementation. |
| *Missing* | `Act`, `Section` | Master tables completely missing in implementation. |
| *Missing* | `Employee`, `Rank`, `Designation` | Employee registry and police structure tables missing. |
| *Missing* | `Court` | Court directory table missing. |

---

## ER Diagram Mismatches

The implemented database violates multiple definitions in [Police_FIR_ER_Diagram.pdf](file:///Users/krishanand/datathon26/Project_Documents/Police_FIR_ER_Diagram.pdf).

### Cardinality Mismatches
1. **Accused Representation**: In the ER diagram, `Accused` has a direct One-to-Many association with `CaseMaster` (`CaseMaster` is parent). The implementation uses a Many-to-Many junction table (`crime_participation` bridging `crime_events` and `criminals`), representing a different business cardinality.
2. **Missing Junction Table**: The ER diagram references a junction table `inv_arrestsurrenderaccused` to handle arrests linking to multiple accused. In the SQL schema, `ArrestSurrender` only holds a single `AccusedMasterID` foreign key. The implementation has neither, as the arrest entity is missing entirely.

### Document Inconsistencies (SQL Schema vs ER Diagram)
1. **`Inv_OccuranceTime` Entity**: The ER Diagram lists an entity named `Inv_OccuranceTime` in a One-to-One relationship with `CaseMaster` (ER Diagram Page 7). However, this table is not defined in [Police_FIR_Schema.sql](file:///Users/krishanand/datathon26/assets/Police_FIR_Schema.sql); instead, occurrence columns are defined directly on `CaseMaster`.
2. **Key Type Mismatch**: In the ER diagram, `ActSectionAssociation` lists `ActID` and `SectionID` as `INT` types, while the master tables `Act` and `Section` define `ActCode` and `SectionCode` as `VARCHAR` types.

---

## Missing Components

### Missing Tables
* `CaseCategory`, `GravityOffence`, `CrimeHead`, `CrimeSubHead`, `CaseStatusMaster`, `CasteMaster`, `ReligionMaster`, `OccupationMaster`, `Act`, `Section`, `State`, `District`, `Court`, `UnitType`, `Unit`, `Rank`, `Designation`, `Employee`, `ComplainantDetails`, `ActSectionAssociation`, `ArrestSurrender`, `CrimeHeadActSection`, `ChargesheetDetails`.

### Missing Columns on Main Tables
* **`crime_events`**: `CrimeNo`, `CaseNo`, `PolicePersonID`, `PoliceStationID` (referencing `Unit`), `CaseCategoryID`, `GravityOffenceID`, `CrimeMajorHeadID`, `CrimeMinorHeadID`, `CaseStatusID`, `CourtID`, `BriefFacts`.
* **`victims`**: `VictimName`, `VictimPolice`.

---

## Security Findings

### 1. Hardcoded Credentials and Secrets
* **Vulnerability**: JWT keys are hardcoded in config settings files.
* **Risk**: High. Committed secrets in git repositories compromise session verification.

### 2. Lack of Native Zoho Authentication
* **Vulnerability**: The backend runs custom PyJWT and password hashing middleware instead of routing identity verification through Zoho Catalyst Hosted Authentication.
* **Risk**: High. Bypasses security layers of the target environment.

### 3. Under-Secured Password Hashing Context
* **Vulnerability**: The app uses `sha256_crypt` instead of `bcrypt`.
* **Risk**: Medium. Passwords are vulnerable to offline brute force attacks using modern GPUs.

---

## Performance Findings

### 1. Thread Blocking computations in FastAPI Startup Lifespan
* **Issue**: Generating the 100,000+ node NetworkX graph at startup inside the main thread locks the Python interpreter.
* **Risk**: High. Causes the web workers to stop responding during caching operations.

### 2. N+1 Query Overhead
* **Issue**: Default lazy relationship fetches trigger sequential SQL SELECTs.
* **Risk**: Medium. Multiplies database query latency during analytics sweeps.

### 3. Missing Composite Indexes
* **Issue**: Missing indexes on high-frequency filters:
  - `crime_events(location_id, crime_date)`
  - `crime_participation(criminal_id, crime_event_id)`
  - `criminals(risk_score, status)`

---

## Data Integrity Findings

### 1. Lack of Cascading Constraints on Major Entity Relationships
* **Issue**: `location_id` and `police_station_id` foreign keys in `crime_events` do not specify `ondelete` rules. Deleting locations or stations leaves orphaned crime records.
* **Risk**: High.

### 2. Lack of Unique Constraint on Crime Participation
* **Issue**: `crime_participation` lacks a unique key constraint on the combination of `(crime_event_id, criminal_id)`.
* **Risk**: Medium. Allows duplicate suspect mappings to the same incident.

---

## Final Verdict

#### 1. Does the implementation fully match `assets/Police_FIR_Schema.sql`?
**No**. The implemented database schema is structurally different, featuring a flat, denormalized 14-table layout compared to the official MySQL schema's 26 normalized tables.

#### 2. Does it fully match `Project_Documents/Police_FIR_ER_Diagram.pdf`?
**No**. The implementation lacks critical entities (Complainants, Arrests, Acts, Sections, Courts) and implements different cardinalities (using M2M bridge tables for criminals instead of direct O2M).

#### 3. Is the database production-ready?
**No**. It requires database migration from SQLite to Zoho Catalyst Data Store / PostgreSQL, implementation of eager loading to eliminate N+1 query bottlenecks, and offloading CPU-intensive graph operations to Catalyst Job Pools.

#### 4. Is it suitable for final hackathon submission?
**No**. The database implementation does not match the official schema. Additionally, utilizing local SQLAlchemy models and file-based SQLite will fail deployment checks on Zoho Catalyst.

#### 5. What must be fixed before submission?
1. Replace SQLAlchemy code with raw ZCQL queries in repository files.
2. Replace local custom JWT token routines with Zoho Catalyst native Authentication.
3. Align SQLite engine connections with the Zoho Catalyst Data Store platform.
4. Scale down seed files to respect development tier row limitations or configure Catalyst production configurations.
5. Fix hardcoded secrets in the configurations file.

#### 6. Which issues should be prioritized?
1. **ZCQL & Database Migration (Critical)**: Rewriting ORM logic into ZCQL to enable AppSail data store connections.
2. **Secret key and Native Auth Integration (Critical)**: Eliminating custom JWT and hardcoded keys.
3. **Graph computations caching offload (High)**: Restructuring the NetworkX warmup thread into a background Job Pool to prevent thread blocking.
