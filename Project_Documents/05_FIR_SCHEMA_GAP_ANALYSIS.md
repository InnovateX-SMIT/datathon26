# Karnataka Police FIR Schema Gap Analysis

## Scope
This audit compares the current workspace database layer against the strict FIR specification in `Karnataka_Police_FIR_Schema_Implementation_Guide.md`.

Current implementation source of truth:
- `backend/core/database.py`
- `backend/models/*.py`
- `backend/schemas/*.py`
- `backend/services/database_management_service.py`

## Executive Summary
The current project does **not** implement the FIR schema defined in the guide. It implements a separate, flatter crime-intelligence schema centered on:
- `crime_events`
- `criminals`
- `victims`
- `locations`
- `police_stations`
- `crime_participation`

The FIR spec requires a normalized relational model with master tables, legal classification tables, case lifecycle tables, and police organization hierarchy tables. Most of those tables do not exist yet.

## What Already Exists
The following ORM tables currently exist:
- `users`
- `audit_logs`
- `datasets`
- `dataset_configs`
- `locations`
- `police_stations`
- `crime_events`
- `criminals`
- `victims`
- `crime_participation`
- `predictions`
- `alerts`
- `recommendations`
- `resource_allocations`
- `recommendation_history`
- `reports`
- `ml_models`

These are useful for the current analytics platform, but they are not the FIR schema required by the guide.

## Missing Tables
The following FIR tables are missing completely from the current implementation:

### Core case and incident
- `CaseMaster`
- `Inv_OccuranceTime`

### People involved
- `ComplainantDetails`
- `Accused`
- `ArrestSurrender`
- `ChargesheetDetails`
- `inv_arrestsurrenderaccused` junction table

### Legal classification
- `Act`
- `Section`
- `ActSectionAssociation`
- `CrimeHead`
- `CrimeSubHead`
- `CrimeHeadActSection`

### Geography and organization
- `State`
- `District`
- `Court`
- `UnitType`
- `Unit`
- `Rank`
- `Designation`
- `Employee`

### Lookup / master tables
- `CaseCategory`
- `GravityOffence`
- `CaseStatusMaster`
- `CasteMaster`
- `ReligionMaster`
- `OccupationMaster`

## Missing or Mismatched Columns

### 1. `crime_events` is not `CaseMaster`
The current `crime_events` table is a denormalized incident model. It is missing the columns that the FIR spec treats as mandatory case-level fields:
- `CrimeNo`
- `CaseNo`
- `PolicePersonID`
- `PoliceStationID` should point to `Unit.UnitID`, not `police_stations.id`
- `CaseCategoryID`
- `GravityOffenceID`
- `CrimeMajorHeadID`
- `CrimeMinorHeadID`
- `CaseStatusID`
- `CourtID`
- `BriefFacts`

It also uses fields that are not part of the FIR schema:
- `crime_type`
- `crime_category`
- `crime_subcategory`
- `severity`
- `status` as free text
- `victim_count`
- `accused_count`

### 2. Occurrence data is flattened
The spec requires a one-to-one `Inv_OccuranceTime` table with:
- `IncidentFromDate`
- `IncidentToDate`
- `InfoReceivedPSDate`
- `latitude`
- `longitude`
- `BriefFacts`

The current implementation spreads occurrence/location data across `crime_events`, `locations`, and `police_stations` instead of keeping the FIR-specific 1:1 structure.

### 3. `victims` does not match `Victim`
The current `Victim` model is missing FIR-required columns:
- `VictimName`
- `VictimPolice`

Current mismatches:
- `age` is `Float`; spec wants `AgeYear INT`
- `occupation` and `location_id` are extra, non-spec fields
- `crime_event_id` exists, but the target schema uses `CaseMasterID`

### 4. `criminals` does not match `Accused`
The current `Criminal` model does not correspond to the spec's `Accused` entity.
Missing or mismatched items:
- `AccusedMasterID` identity field
- `CaseMasterID`
- `AccusedName`
- `AgeYear INT` instead of `Float`
- `GenderID` lookup instead of free-text gender
- `PersonID` sorting field such as `A1`, `A2`, etc.

The current model also includes non-spec analytics fields like `risk_score`.

### 5. `crime_participation` is the wrong relation shape
The current project uses `crime_participation` as a many-to-many bridge between `crime_events` and `criminals`.
The FIR spec expects:
- `CaseMaster -> Accused` as one-to-many
- `ArrestSurrender -> inv_arrestsurrenderaccused` as the actual many-to-many junction

So the current junction table is not a match for the required cardinality.

### 6. `police_stations` does not match `Unit` / `UnitType`
The current model is flattened and lacks hierarchy.
Missing FIR fields and concepts:
- `UnitTypeID`
- `ParentUnit`
- `StateID`
- `DistrictID`
- `NationalityID`
- separate `UnitType` table

The current `district` text column is not a normalized foreign key.

### 7. `locations` does not match `State` / `District`
The current `Location` table combines state, district, latitude, and longitude into one entity.
The spec wants separate lookup tables:
- `State`
- `District`
- `Court` linked to `District` and `State`

### 8. Lookup columns are free-text instead of foreign keys
The current implementation stores domain values as text where the FIR spec requires master-table references.
Examples:
- `crime_type`, `crime_category`, `crime_subcategory`
- `status`
- `gender`
- `occupation`
- `caste`
- `availability`

The spec requires normalized lookup masters and foreign keys for these values.

### 9. Date/time types are not aligned
The spec requires `DATETIME` for occurrence and receipt timestamps.
The current model uses:
- `Date` for `crime_date`
- `Time` for `crime_time`
- `DateTime(timezone=True)` for audit timestamps only

This is not equivalent to the FIR schema's occurrence model.

### 10. Crime number validation is missing
The guide requires strict application-layer validation for `CrimeNo` and `CaseNo`:
- `CrimeNo` = 1 digit category code + 4 digit district ID + 4 digit police station ID + 4 digit year + 5 digit running serial
- `CaseNo` = last 9 digits of the crime number

There is no such field or validation in the current schemas.

## Broken Relationship Matrix

### Missing relationships
- `CaseMaster -> Inv_OccuranceTime` 1:1 missing
- `CaseMaster -> ComplainantDetails` 1:M missing
- `CaseMaster -> Accused` 1:M missing
- `CaseMaster -> ArrestSurrender` 1:M missing
- `CaseMaster -> ActSectionAssociation` 1:M missing
- `CrimeHead -> CrimeHeadActSection` 1:M missing
- `Act -> CrimeHeadActSection` 1:M missing
- `Act -> Section` 1:M missing
- `District -> State` missing
- `Court -> District / State` missing
- `Unit -> UnitType / State / District / ParentUnit` missing
- `Employee -> District / Unit / Rank / Designation` missing

### Current relationships that do not match the spec
- `CrimeEvent -> Victim` is implemented, but the entity shape is wrong
- `CrimeEvent -> Criminal` is modeled through `CrimeParticipation`, which does not match the required case/accused relationship
- `PoliceStation -> Location` is implemented as a flat reference, not the normalized unit hierarchy
- `Alert -> User` and `Prediction -> CrimeEvent` are platform-specific and not part of the FIR spec

## Data Type and Constraint Mismatches
- `AgeYear` is modeled as `Float` in current code; spec requires `INT`
- `gender` is modeled as text; spec expects lookup-based or constrained values
- `latitude` / `longitude` are `Float`; spec says `DECIMAL`
- `BriefFacts` is missing entirely; spec expects `NVARCHAR(MAX)` or equivalent long text
- `Active` flags are absent from the master tables because the master tables themselves are missing
- `BIT`-style fields are not represented in the FIR-specific model layer yet
- `CrimeNo` and `CaseNo` are missing, so length/format constraints cannot currently be enforced

## What We Are Going To Add
### Phase 1: Normalized FIR foundation
- Add all lookup/master tables
- Add `CaseMaster`
- Add `Inv_OccuranceTime`
- Add `Victim`, `Accused`, `ComplainantDetails`, `ArrestSurrender`, and `ChargesheetDetails`
- Add legal classification tables: `Act`, `Section`, `CrimeHead`, `CrimeSubHead`, `ActSectionAssociation`, `CrimeHeadActSection`
- Add police hierarchy tables: `State`, `District`, `Court`, `UnitType`, `Unit`, `Rank`, `Designation`, `Employee`

### Phase 2: Relationship cleanup
- Replace text-based lookups with foreign keys
- Replace flattened station/location modeling with normalized geography and org hierarchy
- Add the arrest-to-accused junction table required by the spec
- Enforce one-to-one and one-to-many cardinalities as defined in the guide

### Phase 3: Validation and DTO rules
- Add DTO validation for `CrimeNo` and `CaseNo`
- Add validation for integer years, bit fields, and datetime inputs
- Add required-field validation for master and transactional tables

### Phase 4: DRY refactor
- Introduce reusable SQLAlchemy mixins for common fields like timestamps and active flags
- Introduce a base lookup mixin for master tables with `id`, `name`, `active`, and `sort_order`-style fields where appropriate
- Centralize common Pydantic validation patterns for lookup IDs, timestamp parsing, and constrained enums

## What We Are Going To Remove or Retire
This should be done only after the FIR schema replacement is introduced.

- Retire the generic crime-intelligence core tables as the primary source of truth for FIR data:
  - `crime_events`
  - `criminals`
  - `victims`
  - `crime_participation`
  - `locations`
  - `police_stations`
- Remove free-text classification columns from the FIR path:
  - `crime_type`
  - `crime_category`
  - `crime_subcategory`
  - `status` as an unbounded string
  - `gender`, `occupation`, `caste` as raw strings where lookups are required
- Remove the incorrect many-to-many accused bridge from the FIR path if the spec is followed literally
- Keep analytics tables only as platform extensions, not as substitutes for FIR master data

## What We Should Keep
These tables are not part of the FIR schema, but they are still useful for the broader platform:
- `users`
- `audit_logs`
- `datasets`
- `dataset_configs`
- `predictions`
- `alerts`
- `recommendations`
- `resource_allocations`
- `recommendation_history`
- `reports`
- `ml_models`

They should be connected to FIR cases only where that relationship is truly needed.

## DRY Refactor Plan
To avoid repeating the same audit, status, and timestamp columns in many master tables:
- Use a reusable timestamp mixin for `created_at` and `updated_at`
- Use an active-flag mixin for master tables that require `Active`
- Use a base lookup mixin for common master-table shape
- Use shared enum/value objects for constrained flags like `gender`, `case status`, and `chargesheet type`
- Use shared validators for date/time parsing and code-format validation

## Recommended Sequence of Work
1. Add the missing lookup tables first.
2. Add `CaseMaster` and `Inv_OccuranceTime` next.
3. Add people and event tables after the case master exists.
4. Add legal classification tables and junction tables.
5. Add police organization hierarchy tables.
6. Refactor current models to use foreign keys instead of free-text columns.
7. Add DTO validation for all code/format constraints.
8. Retire or remap the current generic crime-event schema.

## Bottom Line
The current codebase has a workable analytics backbone, but it does **not** satisfy the Karnataka FIR schema. The largest gaps are the missing master tables, missing case master tables, normalized hierarchy tables, and the incorrect use of free-text fields where the guide requires foreign keys.
