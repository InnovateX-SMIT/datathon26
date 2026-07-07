# SYSTEM INSTRUCTION: FIR SYSTEM INTEGRATION PROTOCOL

**TARGET AGENT INSTRUCTIONS:** You are an AI programming assistant evaluating a user's codebase. The user has provided this specification document detailing the database schema, entity relationships, and architectural requirements for a Police FIR System (specifically for the Karnataka Police Department). 

**Your tasks upon receiving this document are as follows:**
1. **Audit:** Scan the current codebase to check if these database structures (SQL schemas, ORM models like Prisma/TypeORM for Node.js, or JPA/Hibernate for Java) currently exist.
2. **Gap Analysis:** Identify exactly which tables, columns, constraints, or relationships are missing. Report this gap analysis back to the user clearly.
3. **Implementation:** If requested by the user, automatically generate and inject the missing code (Migrations, Entities, Models) adhering strictly to the **DRY (Don't Repeat Yourself)** principle. Avoid redundant code by using abstract base classes or reusable traits where possible.

---

## 1. ARCHITECTURE AND DATABASE CONVENTIONS

### 1.1 General Information
* **Domain:** Karnataka Police Department FIR System.
* **Architecture Impact:** This is a heavily relational SQL-based structure requiring strong Foreign Key (FK) constraints.
* **Key Convention:** * `PK` = Primary Key (Uniquely identifies records).
    * `FK` = Foreign Key (References a Primary Key in another table).

### 1.2 Specialized Formatting Rules
* **Crime Number (CrimeNo):** This follows a highly structured format that must be validated at the application/API level. Format: `1 digit Case Category Code + 4 digit District ID + 4 digit Police Station ID + 4 digit Year + 5 digit Running Serial Number`.
* **Case Number (CaseNo):** Last 9 digits of the CrimeNo (YYYY + 5-digit running serial number).

---

## 2. EXHAUSTIVE DATABASE SCHEMA

*Target Agent: Ensure the following tables and columns are defined in the application's database layer with the exact data types and foreign key constraints.*

### 2.1 Core Case & Incident Tables

| Table Name | Column Name | Type | Key | Description |
| :--- | :--- | :--- | :--- | :--- |
| **CaseMaster** | CaseMaster ID | INT | PK | Unique identifier for each FIR/case. |
| | CrimeNo | VARCHAR | - | Structured crime number. |
| | CaseNo | VARCHAR | - | Generated at police station level (YYYY + 5-digit serial). |
| | CrimeRegistered Date | DATE | - | Date when FIR was registered. |
| | Police PersonID | INT | FK | Officer who registered (Refs `Employee.EmployeeID`). |
| | PoliceStationID | INT | FK | Station where registered (Refs `Unit.UnitID`). |
| | CaseCategoryID | INT | FK | Category (Refs `CaseCategory.CaseCategoryID`). |
| | Gravity OffenceID | INT | FK | Gravity level (Refs `GravityOffence.GravityOffenceID`). |
| | CrimeMajor HeadID | INT | FK | Major crime head (Refs `CrimeHead.CrimeHeadID`). |
| | CrimeMinorHeadID | INT | FK | Minor crime sub-head (Refs `CrimeSubHead.CrimeSubHeadID`). |
| | CaseStatusID | INT | FK | Current status (Refs `CaseStatusMaster.CaseStatusID`). |
| | CourtID | INT | FK | Court hearing the case (Refs `Court.CourtID`). |
| **Inv_OccuranceTime** | IncidentFromDate | DATETIME | - | Start date and time of the incident. |
| (1:1 with CaseMaster) | IncidentToDate | DATETIME | - | End date and time of the incident. |
| | InfoReceivedPSDate | DATETIME | - | Date/time station received information. |
| | latitude | DECIMAL | - | GPS latitude coordinate. |
| | longitude | DECIMAL | - | GPS longitude coordinate. |
| | BriefFacts | NVARCHAR(MAX) | - | Summary of the case. |

### 2.2 People Involved (Complainant, Victim, Accused)

| Table Name | Column Name | Type | Key | Description |
| :--- | :--- | :--- | :--- | :--- |
| **ComplainantDetails**| ComplainantID | INT | PK | Unique identifier for complainant. |
| | CaseMasterID | INT | FK | (Refs `CaseMaster.CaseMasterID`). |
| | ComplainantName | VARCHAR | - | Full name. |
| | AgeYear | INT | - | Age in years. |
| | OccupationID | INT | FK | (Refs `Occupation Master.OccupationID`). |
| | ReligionID | INT | FK | (Refs `ReligionMaster.ReligionID`). |
| | CasteID | INT | FK | (Refs `CasteMaster.caste_master_id`). |
| | GenderID | INT | - | Gender lookup value. |
| **Victim** | VictimMasterID | INT | PK | Unique identifier for each victim. |
| | CaseMasterID | INT | FK | (Refs `CaseMaster.CaseMasterID`). |
| | VictimName | VARCHAR | - | Full name. |
| | AgeYear | INT | - | Age in years. |
| | GenderID | INT | - | Gender (m, f, t). |
| | Victim Police | VARCHAR | - | If Victim is police, `1`, else `0`. |
| **Accused** | AccusedMasterID | INT | PK | Unique identifier for accused person. |
| | CaseMasterID | INT | FK | (Refs `CaseMaster.CaseMasterID`). |
| | AccusedName | VARCHAR | - | Full name. |
| | AgeYear | INT | - | Age in years. |
| | GenderID | INT | - | Gender (M/F/T). |
| | PersonID | VARCHAR | - | Accused Sorting (A1, A2, A3...). |

### 2.3 Legal & Crime Classification (Acts & Sections)

| Table Name | Column Name | Type | Key | Description |
| :--- | :--- | :--- | :--- | :--- |
| **ActSectionAssociation**| CaseMasterID | INT | FK | (Refs `CaseMaster.CaseMasterID`). |
| | ActID | INT | FK | (Refs `Act.ActCode`). |
| | SectionID | INT | FK | (Refs `Section.SectionCode`). |
| | ActOrderID | INT | - | Display order of act. |
| | SectionOrderID | INT | - | Display order of section. |
| **Act** | ActCode | VARCHAR | PK | Code for legal act (e.g., IPC). |
| | ActDescription | VARCHAR | - | Full official name. |
| | ShortName | VARCHAR | - | Abbreviated name. |
| | Active | BIT | - | 1=Active, 0=Inactive. |
| **Section** | ActCode | VARCHAR | FK | (Refs `Act.ActCode`). |
| | SectionCode | VARCHAR | PK(Assumed)| Section number (e.g., 302). |
| | Section Description | VARCHAR | - | Full description. |
| | Active | BIT | - | 1=Active, 0=Inactive. |
| **CrimeHeadActSection**| CrimeHeadID | INT | FK | (Refs `CrimeHead.CrimeHeadID`). |
| | ActCode | VARCHAR | FK | (Refs `Act.ActCode`). |
| | SectionCode | VARCHAR | FK | Section code applicable. |
| **CrimeHead** | CrimeHeadID | INT | PK | Identifier for major crime head. |
| | CrimeGroupName | VARCHAR | - | Name of group (e.g., Crimes Against Body). |
| | Active | BIT | - | 1=Active, 0=Inactive. |
| **CrimeSubHead** | Crime SubHeadID | INT | PK | Identifier for crime sub-head. |
| | CrimeHeadID | INT | FK | (Refs `CrimeHead.CrimeHeadID`). |
| | CrimeHeadName | VARCHAR | - | Sub-head name (e.g., Murder). |
| | SeqID | INT | - | Display sequence order. |

### 2.4 Events & Proceedings (Arrest & Chargesheet)

| Table Name | Column Name | Type | Key | Description |
| :--- | :--- | :--- | :--- | :--- |
| **ArrestSurrender** | ArrestSurrenderID | INT | PK | Unique identifier for event. |
| | CaseMasterID | INT | FK | (Refs `CaseMaster.CaseMasterID`). |
| | ArrestSurrender TypeID| INT | - | Event type (arrest/surrender). |
| | Arrest SurrenderDate | DATE | - | Date of event. |
| | ArrestSurrenderStateId| INT | FK | (Refs `State.StateID`). |
| | ArrestSurrenderDistrictId| INT | FK | (Refs `District.DistrictID`). |
| | Police StationID | INT | FK | (Refs `Unit.UnitID`). |
| | IOID | INT | FK | Investigating Officer (Refs `Employee.EmployeeID`). |
| | CourtID | INT | FK | (Refs `Court.CourtID`). |
| | AccusedMasterID | INT | FK | (Refs `Accused.AccusedMasterID`). |
| | IsAccused | BIT | - | 1 if primary accused. |
| | IsComplainantAccused | BIT | - | 1 if complainant is also accused. |
| **Chargesheet Details**| CSID | INT | PK | Identifier for chargesheet. |
| | CaseMasterID | INT | FK | (Refs `CaseMaster.CaseMasterID`). |
| | csdate | DATETIME | - | Chargesheet date. |
| | cstype | CHAR | - | A->Chargesheet, B->False Case, C->Undetected. |
| | Police PersonID | INT | FK | (Refs `Employee.EmployeeID`). |

### 2.5 Geographical & Organizational Hierarchy (Units & Courts)

| Table Name | Column Name | Type | Key | Description |
| :--- | :--- | :--- | :--- | :--- |
| **State** | StateID | INT | PK | Unique state ID. |
| | StateName | VARCHAR | - | Name of state. |
| | NationalityID | INT | - | Nationality ID. |
| | Active | BIT | - | 1=Active, 0=Inactive. |
| **District** | DistrictID | INT | PK | Unique district ID. |
| | DistrictName | VARCHAR | - | Name of district. |
| | StateID | INT | FK | (Refs `State.StateID`). |
| | Active | BIT | - | 1=Active, 0=Inactive. |
| **Court** | CourtID | INT | PK | Unique court ID. |
| | CourtName | VARCHAR | - | Full name of court. |
| | DistrictID | INT | FK | (Refs `District.DistrictID`). |
| | StateID | INT | FK | (Refs `State.StateID`). |
| | Active | BIT | - | 1=Active, 0=Inactive. |
| **Unit** | UnitID | INT | PK | Unique police unit/station ID. |
| | UnitName | VARCHAR | - | Name of unit. |
| | TypeID | INT | FK | (Refs `UnitType.UnitTypeID`). |
| | ParentUnit | INT | FK | Self-reference to UnitID. |
| | NationalityID | INT | - | Reference ID. |
| | StateID | INT | FK | (Refs `State.StateID`). |
| | DistrictID | INT | FK | (Refs `District.DistrictID`). |
| | Active | BIT | - | 1=Active, 0=Inactive. |
| **UnitType** | Unit TypeID | INT | PK | Unique ID. |
| | Unit TypeName | VARCHAR | - | E.g., Police Station. |
| | City Dist State | VARCHAR | - | Operational level. |
| | Hierarchy | INT | - | Level (lower = higher authority). |
| | Active | BIT | - | 1=Active, 0=Inactive. |

### 2.6 Department Personnel (Employees)

| Table Name | Column Name | Type | Key | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Rank** | RankID | INT | PK | E.g., Constable, Inspector. |
| | RankName | VARCHAR | - | Name of rank. |
| | Hierarchy | INT | - | Rank hierarchy level. |
| | Active | BIT | - | 1=Active, 0=Inactive. |
| **Designation** | DesignationID | INT | PK | E.g., SHO. |
| | Designation Name | VARCHAR | - | Name of designation. |
| | Active | BIT | - | 1=Active, 0=Inactive. |
| | SortOrder | INT | - | UI display order. |
| **Employee** | EmployeeID | INT | PK | Unique employee ID. |
| | DistrictID | INT | FK | (Refs `District.DistrictID`). |
| | UnitID | INT | FK | (Refs `Unit.UnitID`). |
| | RankID | INT | FK | (Refs `Rank.RankID`). |
| | DesignationID | INT | FK | (Refs `Designation.DesignationID`). |
| | KGID | VARCHAR | - | Karnataka Government ID. |
| | FirstName | VARCHAR | - | Employee First Name. |
| | EmployeeDOB | DATE | - | Date of birth. |
| | GenderID | INT | - | Gender lookup. |
| | Blood GroupID | INT | - | Blood group lookup. |
| | Physically Challenged| BIT | - | 1=Yes, 0=No. |
| | AppointmentDate | DATE | - | Date of appointment. |

### 2.7 Lookup & Master Tables (Dictionaries)

| Table Name | Column Name | Type | Key | Description |
| :--- | :--- | :--- | :--- | :--- |
| **CasteMaster** | caste_master_id | INT | PK | Unique caste ID. |
| | caste_master_name | VARCHAR | - | Name of caste. |
| **ReligionMaster** | ReligionID | INT | PK | Unique religion ID. |
| | ReligionName | VARCHAR | - | Name of religion. |
| **OccupationMaster**| OccupationID | INT | PK | Unique occupation ID. |
| | OccupationName | VARCHAR | - | Name of occupation. |
| **CaseStatusMaster**| CaseStatusID | INT | PK | Unique case status ID. |
| | CaseStatus Name | VARCHAR | - | Status (e.g., Under Investigation). |
| **CaseCategory** | CaseCategoryID | INT | PK | Category ID. |
| | Lookup Value | VARCHAR | - | Name (FIR, UDR, PAR...). |
| **GravityOffence** | Gravity OffenceID | INT | PK | Gravity level ID. |
| | LookupValue | VARCHAR | - | Description (Heinous/Non-Heinous). |

---

## 3. STRICT RELATIONSHIP MATRIX & CARDINALITY

*Target Agent Instructions: Enforce these relationships precisely. If using an ORM (e.g. Java Spring Data JPA or Express TypeORM/Prisma), map these explicitly using `@OneToMany`, `@ManyToOne`, or equivalent relation arrays/fields.*

**One-to-One (1:1):**
* `CaseMaster` <-> `Inv_OccuranceTime` (One FIR has exactly one occurrence time/location record).

**One-to-Many (1:M):**
* `CaseMaster` -> `Victim` (One FIR can have multiple victims).
* `CaseMaster` -> `Accused` (One FIR can have multiple accused).
* `CaseMaster` -> `ArrestSurrender` (One FIR can have multiple arrest/surrender events).
* `CaseMaster` -> `ComplainantDetails` (One FIR can have multiple complainants).
* `CaseMaster` -> `ActSectionAssociation` (One FIR can invoke multiple act-sections).
* `CrimeHead` -> `CrimeHeadActSection` (One crime head can map to multiple act-sections).
* `Act` -> `CrimeHeadActSection` (One act links to multiple crime heads).
* `Act` -> `Section` (One act contains multiple sections).

**Many-to-One (M:1):**
* `CaseMaster` -> `CaseCategory`
* `CaseMaster` -> `GravityOffence`
* `CaseMaster` -> `CrimeHead`
* `CaseMaster` -> `CrimeSubHead`
* `CaseMaster` -> `CaseStatusMaster`
* `CaseMaster` -> `Court`
* `CaseMaster` -> `Employee` (Registering Officer)
* `ArrestSurrender` -> `State`, `District`, `Court`, `Employee` (Investigating Officer).
* `ComplainantDetails` -> `OccupationMaster`, `ReligionMaster`, `CasteMaster`.
* `ActSectionAssociation` -> `Act`, `Section`.
* `CrimeSubHead` -> `CrimeHead`.
* `Court` -> `District`.
* `District` -> `State`.
* `Unit` -> `UnitType`, `State`, `District`.
* `Employee` -> `District`, `Unit`, `Rank`, `Designation`.

**Many-to-Many via Junction Table:**
* The relationship between `ArrestSurrender` and `AccusedMaster` has a specific junction table mapped as:
    * `ArrestSurrender` (1:M) -> `inv_arrestsurrenderaccused` (Junction Table)
    * `inv_arrestsurrenderaccused` (M:1) -> `ArrestSurrender`
    *(Note: This junction handles cases where one arrest event involves multiple accused individuals).*

---

## 4. INTEGRATION & IMPLEMENTATION GUIDELINES FOR THE TARGET AGENT

*Target Agent: Follow these steps when generating the code:*

1. **Initialization:** * Begin by reading the existing database ORM schemas (Java Entities / Node.js Prisma or Mongoose schemas). 
   * Acknowledge what tables already exist.
2. **DRY Principle Execution:** * Create an abstract base schema/class for common fields like `Active`, `SeqID`, or standard lookup fields to prevent repetitive boilerplate across the Master Tables (e.g., `ReligionMaster`, `CasteMaster`, `CaseStatusMaster`).
3. **Data Type Mapping:** * Ensure `BIT` maps correctly to `Boolean` in Java/Node.js.
   * Ensure `DATETIME` maps to timezone-aware date objects (`Date` in JS, `Instant` or `LocalDateTime` in Java).
   * Ensure string lengths for constraints like `CrimeNo` are strictly validated at the DTO (Data Transfer Object) layer.
4. **Output Format:**
   * After checking the codebase, respond to the user with a step-by-step checklist of what is missing.
   * Propose the specific code required to fulfill the schema (e.g., SQL migration scripts, ORM model files, or Java entity classes) so they can be easily pasted or auto-integrated into their development environment.

