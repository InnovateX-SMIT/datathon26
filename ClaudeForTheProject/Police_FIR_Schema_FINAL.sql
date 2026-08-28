-- ============================================================================
-- Police FIR / CrimeNexus — FINAL CORRECTED SCHEMA
-- Reconstructed from: Police_FIR_ER_Diagram.pdf (authority) +
--                      karnataka_crime_dataset_10k_compliant.csv (data reality) +
--                      Police_FIR_Schema2.sql (audited baseline)
-- Every change below is explained in CHANGELOG comments. Nothing here reflects
-- inspection of an application repository — none was provided. See the report
-- for the full list of decisions flagged UNKNOWN / REQUIRES DECISION.
-- ============================================================================

CREATE DATABASE IF NOT EXISTS PoliceFIR;
USE PoliceFIR;

SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------------------------------------------------------
-- MASTER & LOOKUP TABLES
-- ----------------------------------------------------------------------------

CREATE TABLE CaseCategory (
    CaseCategoryID INT PRIMARY KEY,
    LookupValue VARCHAR(255) NOT NULL
    -- Official examples: FIR, UDR, PAR, Zero FIR. CSV sample contains FIR/UDR/PAR only.
);

CREATE TABLE GravityOffence (
    GravityOffenceID INT PRIMARY KEY,
    LookupValue VARCHAR(255) NOT NULL
);

CREATE TABLE CrimeHead (
    CrimeHeadID INT PRIMARY KEY,
    CrimeGroupName VARCHAR(255) NOT NULL,
    Active BIT DEFAULT 1
);

CREATE TABLE CrimeSubHead (
    CrimeSubHeadID INT PRIMARY KEY,
    CrimeHeadID INT NOT NULL,
    CrimeHeadName VARCHAR(255) NOT NULL,  -- kept as officially named, despite being a sub-head display name (see audit note)
    SeqID INT,
    FOREIGN KEY (CrimeHeadID) REFERENCES CrimeHead(CrimeHeadID)
);

CREATE TABLE CaseStatusMaster (
    CaseStatusID INT PRIMARY KEY,
    CaseStatusName VARCHAR(255) NOT NULL
);

CREATE TABLE CasteMaster (
    caste_master_id INT PRIMARY KEY,
    caste_master_name VARCHAR(255)
    -- CSV provides ZERO source values (complainant_caste is 100% null). Structure only.
);

CREATE TABLE ReligionMaster (
    ReligionID INT PRIMARY KEY,
    ReligionName VARCHAR(255)
    -- CSV provides ZERO source values (complainant_religion is 100% null). Structure only.
);

CREATE TABLE OccupationMaster (
    OccupationID INT PRIMARY KEY,
    OccupationName VARCHAR(255)
    -- CSV provides ZERO source values (complainant_occupation is 100% null). Structure only.
);

-- ADDITION vs both PDF and existing SQL: the PDF calls GenderID a "lookup value" on four
-- different tables but never defines the lookup table itself. CSV shows exactly 3 stable
-- string values (Male/Female/Transgender). Flagged UNKNOWN/REQUIRES DECISION in the report.
CREATE TABLE GenderMaster (
    GenderID INT PRIMARY KEY,
    GenderName VARCHAR(50) NOT NULL
);

-- ADDITION, same rationale as GenderMaster. CSV shows 8 stable blood-group strings.
CREATE TABLE BloodGroupMaster (
    BloodGroupID INT PRIMARY KEY,
    BloodGroupName VARCHAR(50) NOT NULL
);

-- ADDITION, same rationale. PDF: "Type of event: arrest or voluntary surrender (lookup value)".
-- CSV only gives numeric codes 1/2; labels below are an assumption, not sourced from data.
CREATE TABLE ArrestSurrenderTypeMaster (
    ArrestSurrenderTypeID INT PRIMARY KEY,
    TypeName VARCHAR(50) NOT NULL
);

CREATE TABLE Act (
    ActCode VARCHAR(255) PRIMARY KEY,
    ActDescription VARCHAR(255),
    ShortName VARCHAR(255),
    Active BIT DEFAULT 1
);

CREATE TABLE Section (
    SectionCode VARCHAR(255),
    ActCode VARCHAR(255),
    SectionDescription VARCHAR(255),
    Active BIT DEFAULT 1,
    PRIMARY KEY (ActCode, SectionCode),
    FOREIGN KEY (ActCode) REFERENCES Act(ActCode)
);

CREATE TABLE CrimeHeadActSection (
    CrimeHeadID INT,
    ActCode VARCHAR(255),
    SectionCode VARCHAR(255),
    PRIMARY KEY (CrimeHeadID, ActCode, SectionCode),
    FOREIGN KEY (CrimeHeadID) REFERENCES CrimeHead(CrimeHeadID),
    FOREIGN KEY (ActCode) REFERENCES Act(ActCode),
    FOREIGN KEY (ActCode, SectionCode) REFERENCES Section(ActCode, SectionCode)
);

CREATE TABLE State (
    StateID INT PRIMARY KEY,
    StateName VARCHAR(255) NOT NULL,
    NationalityID INT,
    Active BIT DEFAULT 1
);

CREATE TABLE District (
    DistrictID INT PRIMARY KEY,
    DistrictName VARCHAR(255) NOT NULL,
    StateID INT,
    Active BIT DEFAULT 1,
    FOREIGN KEY (StateID) REFERENCES State(StateID)
);

CREATE TABLE Court (
    CourtID INT PRIMARY KEY,
    CourtName VARCHAR(255) NOT NULL,
    DistrictID INT NULL,  -- CHANGED to nullable: "High Court of Karnataka" is state-level and
                           -- legitimately appears against 31 different districts in the CSV.
    StateID INT,
    Active BIT DEFAULT 1,
    FOREIGN KEY (DistrictID) REFERENCES District(DistrictID),
    FOREIGN KEY (StateID) REFERENCES State(StateID)
);

CREATE TABLE UnitType (
    UnitTypeID INT PRIMARY KEY,
    UnitTypeName VARCHAR(255) NOT NULL,
    CityDistState VARCHAR(255),
    Hierarchy INT,
    Active BIT DEFAULT 1
);

CREATE TABLE Unit (
    UnitID INT PRIMARY KEY,
    UnitName VARCHAR(255) NOT NULL,
    TypeID INT,
    ParentUnit INT NULL,  -- NOT derivable from CSV (no parent-unit signal in the data); left NULL on import
    NationalityID INT,
    StateID INT,
    DistrictID INT,
    Active BIT DEFAULT 1,
    FOREIGN KEY (TypeID) REFERENCES UnitType(UnitTypeID),
    FOREIGN KEY (ParentUnit) REFERENCES Unit(UnitID),
    FOREIGN KEY (StateID) REFERENCES State(StateID),
    FOREIGN KEY (DistrictID) REFERENCES District(DistrictID)
);

CREATE TABLE `Rank` (
    RankID INT PRIMARY KEY,
    RankName VARCHAR(255) NOT NULL,
    Hierarchy INT,
    Active BIT DEFAULT 1
);

CREATE TABLE Designation (
    DesignationID INT PRIMARY KEY,
    DesignationName VARCHAR(255) NOT NULL,
    Active BIT DEFAULT 1,
    SortOrder INT
);

CREATE TABLE Employee (
    EmployeeID INT PRIMARY KEY,
    DistrictID INT,
    UnitID INT,
    RankID INT,
    DesignationID INT,
    KGID VARCHAR(255) UNIQUE NOT NULL,
    FirstName VARCHAR(255),  -- PDF defines ONLY this one name field (no LastName). CSV's full
                              -- officer_name is stored here as-is. See report: recommend adding
                              -- a LastName column as a future enhancement (UNKNOWN/REQUIRES DECISION).
    EmployeeDOB DATE,
    GenderID INT,
    BloodGroupID INT,
    PhysicallyChallenged BIT DEFAULT 0,
    AppointmentDate DATE,
    FOREIGN KEY (DistrictID) REFERENCES District(DistrictID),
    FOREIGN KEY (UnitID) REFERENCES Unit(UnitID),
    FOREIGN KEY (RankID) REFERENCES `Rank`(RankID),
    FOREIGN KEY (DesignationID) REFERENCES Designation(DesignationID),
    FOREIGN KEY (GenderID) REFERENCES GenderMaster(GenderID),
    FOREIGN KEY (BloodGroupID) REFERENCES BloodGroupMaster(BloodGroupID)
);

-- ----------------------------------------------------------------------------
-- CORE OPERATIONAL TABLES
-- ----------------------------------------------------------------------------

-- CHANGED vs existing SQL: IncidentFromDate, IncidentToDate, InfoReceivedPSDate, latitude,
-- longitude and the occurrence-location narrative are MOVED OUT to Inv_OccuranceTime below.
-- Justification: (1) the PDF's own relationship matrix declares a 1:1 CaseMaster ->
-- Inv_OccuranceTime table that the existing SQL never created; (2) the CSV independently
-- carries TWO distinct free-text fields -- "brief_facts" (case-level summary) and
-- "occurrence_brief_facts" (location/occurrence narrative) -- which is real evidence these
-- are two different pieces of information, not one. BriefFacts (the case summary) stays here.
CREATE TABLE CaseMaster (
    CaseMasterID INT PRIMARY KEY,
    CrimeNo VARCHAR(255) UNIQUE NOT NULL,
    CaseNo VARCHAR(255) NOT NULL,
    CrimeRegisteredDate DATE,
    PolicePersonID INT,
    PoliceStationID INT,
    CaseCategoryID INT,
    GravityOffenceID INT,
    CrimeMajorHeadID INT,
    CrimeMinorHeadID INT,
    CaseStatusID INT,
    CourtID INT,
    BriefFacts LONGTEXT,
    FOREIGN KEY (PolicePersonID) REFERENCES Employee(EmployeeID),
    FOREIGN KEY (PoliceStationID) REFERENCES Unit(UnitID),
    FOREIGN KEY (CaseCategoryID) REFERENCES CaseCategory(CaseCategoryID),
    FOREIGN KEY (GravityOffenceID) REFERENCES GravityOffence(GravityOffenceID),
    FOREIGN KEY (CrimeMajorHeadID) REFERENCES CrimeHead(CrimeHeadID),
    FOREIGN KEY (CrimeMinorHeadID) REFERENCES CrimeSubHead(CrimeSubHeadID),
    FOREIGN KEY (CaseStatusID) REFERENCES CaseStatusMaster(CaseStatusID),
    FOREIGN KEY (CourtID) REFERENCES Court(CourtID)
);

-- NEW TABLE — present in the PDF relationship matrix ("One FIR has one occurrence
-- time/location record") but absent from the existing SQL entirely. See CHANGELOG above.
CREATE TABLE Inv_OccuranceTime (
    CaseMasterID INT PRIMARY KEY,
    IncidentFromDate DATETIME,
    IncidentToDate DATETIME,
    InfoReceivedPSDate DATETIME,
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    OccurrenceBriefFacts LONGTEXT,
    FOREIGN KEY (CaseMasterID) REFERENCES CaseMaster(CaseMasterID)
);

CREATE TABLE ComplainantDetails (
    ComplainantID INT PRIMARY KEY,
    CaseMasterID INT,
    ComplainantName VARCHAR(255),
    AgeYear INT,
    OccupationID INT,
    ReligionID INT,
    CasteID INT,
    GenderID INT,
    FOREIGN KEY (CaseMasterID) REFERENCES CaseMaster(CaseMasterID),
    FOREIGN KEY (OccupationID) REFERENCES OccupationMaster(OccupationID),
    FOREIGN KEY (ReligionID) REFERENCES ReligionMaster(ReligionID),
    FOREIGN KEY (CasteID) REFERENCES CasteMaster(caste_master_id),
    FOREIGN KEY (GenderID) REFERENCES GenderMaster(GenderID)
);

-- ActID/SectionID kept as VARCHAR (not INT). The PDF's own column list says "ActID INT"
-- but then FKs it to Act.ActCode, which the PDF's own Act table defines as VARCHAR PK.
-- The existing SQL had this right; the PDF text has the inconsistency. See report.
CREATE TABLE ActSectionAssociation (
    CaseMasterID INT,
    ActID VARCHAR(255),
    SectionID VARCHAR(255),
    ActOrderID INT,
    SectionOrderID INT,
    PRIMARY KEY (CaseMasterID, ActID, SectionID),
    FOREIGN KEY (CaseMasterID) REFERENCES CaseMaster(CaseMasterID),
    FOREIGN KEY (ActID) REFERENCES Act(ActCode),
    FOREIGN KEY (ActID, SectionID) REFERENCES Section(ActCode, SectionCode)
);

CREATE TABLE Victim (
    VictimMasterID INT PRIMARY KEY,
    CaseMasterID INT,
    VictimName VARCHAR(255),
    AgeYear INT,
    GenderID INT,
    VictimPolice BIT,
    FOREIGN KEY (CaseMasterID) REFERENCES CaseMaster(CaseMasterID),
    FOREIGN KEY (GenderID) REFERENCES GenderMaster(GenderID)
);

CREATE TABLE Accused (
    AccusedMasterID INT PRIMARY KEY,
    CaseMasterID INT,
    AccusedName VARCHAR(255),
    AgeYear INT,
    GenderID INT,
    PersonID VARCHAR(255),  -- business/display key, e.g. A1, A2 -- unique per CASE, not globally
    FOREIGN KEY (CaseMasterID) REFERENCES CaseMaster(CaseMasterID),
    FOREIGN KEY (GenderID) REFERENCES GenderMaster(GenderID),
    UNIQUE KEY uq_case_person (CaseMasterID, PersonID)
);

-- CHANGED vs existing SQL: added AccusedMasterID as a direct FK. The PDF's own column list
-- for ArrestSurrender explicitly includes "AccusedMasterID INT FK -> Accused.AccusedMasterID"
-- (the primary accused for that arrest event) and the existing SQL never had this column at
-- all -- a real gap, not a stylistic choice. The many-accused-per-arrest case (joint arrests)
-- is still covered by the junction table below.
CREATE TABLE ArrestSurrender (
    ArrestSurrenderID INT PRIMARY KEY,
    CaseMasterID INT,
    ArrestSurrenderTypeID INT,
    ArrestSurrenderDate DATE,
    ArrestSurrenderStateId INT,
    ArrestSurrenderDistrictId INT,
    PoliceStationID INT,
    IOID INT,
    CourtID INT,
    AccusedMasterID INT,       -- ADDED: primary accused for this arrest/surrender event
    IsAccused BIT,
    IsComplainantAccused BIT,
    FOREIGN KEY (CaseMasterID) REFERENCES CaseMaster(CaseMasterID),
    FOREIGN KEY (ArrestSurrenderTypeID) REFERENCES ArrestSurrenderTypeMaster(ArrestSurrenderTypeID),
    FOREIGN KEY (ArrestSurrenderStateId) REFERENCES State(StateID),
    FOREIGN KEY (ArrestSurrenderDistrictId) REFERENCES District(DistrictID),
    FOREIGN KEY (PoliceStationID) REFERENCES Unit(UnitID),
    FOREIGN KEY (IOID) REFERENCES Employee(EmployeeID),
    FOREIGN KEY (CourtID) REFERENCES Court(CourtID),
    FOREIGN KEY (AccusedMasterID) REFERENCES Accused(AccusedMasterID)
);

-- Junction table for the many-accused-per-arrest case (joint arrests). Contains the primary
-- accused too, so this table is the authoritative "who was part of this arrest event" list.
CREATE TABLE inv_arrestsurrenderaccused (
    ArrestSurrenderID INT,
    AccusedMasterID INT,
    PRIMARY KEY (ArrestSurrenderID, AccusedMasterID),
    FOREIGN KEY (ArrestSurrenderID) REFERENCES ArrestSurrender(ArrestSurrenderID),
    FOREIGN KEY (AccusedMasterID) REFERENCES Accused(AccusedMasterID)
);

CREATE TABLE ChargesheetDetails (
    CSID INT PRIMARY KEY,
    CaseMasterID INT,
    csdate DATETIME,
    cstype CHAR(1),  -- A=Chargesheet, B=False Case, C=Undetected (per PDF)
    PolicePersonID INT,
    FOREIGN KEY (CaseMasterID) REFERENCES CaseMaster(CaseMasterID),
    FOREIGN KEY (PolicePersonID) REFERENCES Employee(EmployeeID)
);

SET FOREIGN_KEY_CHECKS = 1;

-- ----------------------------------------------------------------------------
-- INDEXES justified by actual query patterns implied by the ER diagram / dataset
-- ----------------------------------------------------------------------------
CREATE INDEX idx_casemaster_category   ON CaseMaster(CaseCategoryID);
CREATE INDEX idx_casemaster_status     ON CaseMaster(CaseStatusID);
CREATE INDEX idx_casemaster_station    ON CaseMaster(PoliceStationID);
CREATE INDEX idx_casemaster_crimehead  ON CaseMaster(CrimeMajorHeadID, CrimeMinorHeadID);
CREATE INDEX idx_victim_case           ON Victim(CaseMasterID);
CREATE INDEX idx_accused_case          ON Accused(CaseMasterID);
CREATE INDEX idx_arrest_case           ON ArrestSurrender(CaseMasterID);
CREATE INDEX idx_chargesheet_case      ON ChargesheetDetails(CaseMasterID);
CREATE INDEX idx_employee_kgid         ON Employee(KGID);
