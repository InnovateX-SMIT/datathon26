// ══════════════════════════════════════════════════════════════════════════════
// FIR Case Management — TypeScript Type Definitions
// Mirrors backend/schemas/fir.py Pydantic models exactly.
// ══════════════════════════════════════════════════════════════════════════════

// ── Lookup / Master DTOs ────────────────────────────────────────────────────

export interface LookupDTO {
  id: number;
  name: string;
  active: boolean;
  sort_order: number;
}

export interface StateDTO extends LookupDTO {
  NationalityID?: number | null;
}

export interface DistrictDTO extends LookupDTO {
  StateID: number;
}

export interface CourtDTO extends LookupDTO {
  DistrictID: number;
  StateID: number;
}

export interface UnitDTO extends LookupDTO {
  TypeID: number;
  ParentUnit?: number | null;
  NationalityID?: number | null;
  StateID: number;
  DistrictID: number;
}

export interface RankDTO extends LookupDTO {
  Hierarchy?: number | null;
}

export interface DesignationDTO extends LookupDTO {
  SortOrder?: number | null;
}

export interface EmployeeDTO {
  id: number;
  DistrictID: number;
  UnitID: number;
  RankID: number;
  DesignationID: number;
  KGID: string;
  FirstName: string;
  EmployeeDOB?: string | null;
  GenderID: number;
  BloodGroupID?: number | null;
  PhysicallyChallenged: boolean;
  AppointmentDate?: string | null;
  active: boolean;
}

export type CaseCategoryDTO = LookupDTO;
export type GravityOffenceDTO = LookupDTO;
export type CaseStatusDTO = LookupDTO;
export type CasteDTO = LookupDTO;
export type ReligionDTO = LookupDTO;
export type OccupationDTO = LookupDTO;
export type GenderDTO = LookupDTO;
export type NationalityDTO = LookupDTO;
export type BloodGroupDTO = LookupDTO;

export interface ActDTO {
  ActCode: string;
  ActDescription?: string | null;
  ShortName?: string | null;
  active: boolean;
}

export interface SectionDTO {
  ActCode: string;
  SectionCode: string;
  SectionDescription?: string | null;
  active: boolean;
}

export interface CrimeHeadDTO {
  id: number;
  CrimeGroupName: string;
  active: boolean;
}

export interface CrimeSubHeadDTO {
  id: number;
  CrimeHeadID: number;
  CrimeHeadName: string;
  SeqID?: number | null;
}

// ── Transactional DTOs — Create Payloads ────────────────────────────────────

export interface InvOccuranceTimeCreate {
  IncidentFromDate?: string | null;
  IncidentToDate?: string | null;
  InfoReceivedPSDate?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  BriefFacts?: string | null;
}

export interface ComplainantDetailsCreate {
  ComplainantName: string;
  AgeYear?: number | null;
  OccupationID?: number | null;
  ReligionID?: number | null;
  CasteID?: number | null;
  GenderID?: number | null;
}

export interface FIRVictimCreate {
  VictimName: string;
  AgeYear?: number | null;
  GenderID?: number | null;
  VictimPolice: string;
}

export interface AccusedCreate {
  AccusedName: string;
  AgeYear?: number | null;
  GenderID?: number | null;
  PersonID?: string | null;
}

export interface ActSectionAssociationCreate {
  ActCode: string;
  SectionCode: string;
  ActOrderID?: number | null;
  SectionOrderID?: number | null;
}

export interface ArrestSurrenderCreate {
  ArrestSurrenderTypeID: number;
  ArrestSurrenderDate: string;
  ArrestSurrenderStateId: number;
  ArrestSurrenderDistrictId: number;
  PoliceStationID: number;
  IOID: number;
  CourtID: number;
  AccusedMasterID: number;
  IsAccused: boolean;
  IsComplainantAccused: boolean;
  associated_accused_ids: number[];
}

export interface ChargesheetDetailsCreate {
  csdate: string;
  cstype: string;
  PolicePersonID: number;
}

export interface CaseMasterCreate {
  CrimeNo?: string | null;
  CaseNo?: string | null;
  CrimeRegisteredDate?: string | null;
  PolicePersonID: number;
  PoliceStationID: number;
  CaseCategoryID: number;
  GravityOffenceID: number;
  CrimeMajorHeadID: number;
  CrimeMinorHeadID: number;
  CaseStatusID: number;
  CourtID: number;
  BriefFacts?: string | null;
  dataset_id?: number | null;
  occurrence_time?: InvOccuranceTimeCreate | null;
  complainants: ComplainantDetailsCreate[];
  victims: FIRVictimCreate[];
  accused: AccusedCreate[];
  act_sections: ActSectionAssociationCreate[];
  arrest_surrenders: ArrestSurrenderCreate[];
  chargesheets: ChargesheetDetailsCreate[];
}

// ── Transactional DTOs — Response Payloads ──────────────────────────────────

export interface InvOccuranceTimeResponse {
  CaseMasterID: number;
  IncidentFromDate?: string | null;
  IncidentToDate?: string | null;
  InfoReceivedPSDate?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  BriefFacts?: string | null;
  created_at: string;
  updated_at: string;
}

export interface ComplainantDetailsResponse {
  id: number;
  CaseMasterID: number;
  ComplainantName: string;
  AgeYear?: number | null;
  OccupationID?: number | null;
  ReligionID?: number | null;
  CasteID?: number | null;
  GenderID?: number | null;
  created_at: string;
  updated_at: string;
}

export interface FIRVictimResponse {
  id: number;
  CaseMasterID: number;
  VictimName: string;
  AgeYear?: number | null;
  GenderID?: number | null;
  VictimPolice: string;
  created_at: string;
  updated_at: string;
}

export interface AccusedResponse {
  id: number;
  CaseMasterID: number;
  AccusedName: string;
  AgeYear?: number | null;
  GenderID?: number | null;
  PersonID?: string | null;
  created_at: string;
  updated_at: string;
}

export interface ActSectionAssociationResponse {
  CaseMasterID: number;
  ActCode: string;
  SectionCode: string;
  ActOrderID?: number | null;
  SectionOrderID?: number | null;
  created_at: string;
  updated_at: string;
}

export interface ArrestSurrenderResponse {
  id: number;
  CaseMasterID: number;
  ArrestSurrenderTypeID: number;
  ArrestSurrenderDate: string;
  ArrestSurrenderStateId: number;
  ArrestSurrenderDistrictId: number;
  PoliceStationID: number;
  IOID: number;
  CourtID: number;
  AccusedMasterID: number;
  IsAccused: boolean;
  IsComplainantAccused: boolean;
  associated_accused_ids: number[];
  created_at: string;
  updated_at: string;
}

export interface ChargesheetDetailsResponse {
  id: number;
  CaseMasterID: number;
  csdate: string;
  cstype: string;
  PolicePersonID: number;
  created_at: string;
  updated_at: string;
}

export interface CaseMasterResponse {
  id: number;
  CrimeNo?: string | null;
  CaseNo?: string | null;
  CrimeRegisteredDate?: string | null;
  PolicePersonID: number;
  PoliceStationID: number;
  CaseCategoryID: number;
  GravityOffenceID: number;
  CrimeMajorHeadID: number;
  CrimeMinorHeadID: number;
  CaseStatusID: number;
  CourtID: number;
  BriefFacts?: string | null;
  dataset_id?: number | null;
  created_at: string;
  updated_at: string;
  occurrence_time?: InvOccuranceTimeResponse | null;
  complainants: ComplainantDetailsResponse[];
  victims: FIRVictimResponse[];
  accused: AccusedResponse[];
  act_sections: ActSectionAssociationResponse[];
  arrest_surrenders: ArrestSurrenderResponse[];
  chargesheets: ChargesheetDetailsResponse[];
}

// ── Paginated List Response ─────────────────────────────────────────────────

export interface CaseListResponse {
  records: CaseMasterResponse[];
  total: number;
  page: number;
  page_size: number;
}

// ── All lookups combined for caching ────────────────────────────────────────

export interface FirLookupData {
  states: StateDTO[];
  ranks: RankDTO[];
  designations: DesignationDTO[];
  caseCategories: CaseCategoryDTO[];
  gravityOffences: GravityOffenceDTO[];
  caseStatuses: CaseStatusDTO[];
  castes: CasteDTO[];
  religions: ReligionDTO[];
  occupations: OccupationDTO[];
  genders: GenderDTO[];
  nationalities: NationalityDTO[];
  bloodGroups: BloodGroupDTO[];
  acts: ActDTO[];
  crimeHeads: CrimeHeadDTO[];
}
