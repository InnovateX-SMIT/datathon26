// ══════════════════════════════════════════════════════════════════════════════
// FIR API Service — Typed functions for every FIR endpoint
// Pattern follows features/analytics/services/analyticsService.ts
// ══════════════════════════════════════════════════════════════════════════════

import type {
  CaseMasterCreate,
  CaseMasterResponse,
  CaseListResponse,
  StateDTO,
  DistrictDTO,
  CourtDTO,
  UnitDTO,
  RankDTO,
  DesignationDTO,
  EmployeeDTO,
  CaseCategoryDTO,
  GravityOffenceDTO,
  CaseStatusDTO,
  CasteDTO,
  ReligionDTO,
  OccupationDTO,
  GenderDTO,
  NationalityDTO,
  BloodGroupDTO,
  ActDTO,
  SectionDTO,
  CrimeHeadDTO,
  CrimeSubHeadDTO,
} from "../types/fir";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const FIR_PREFIX = "/api/v1/fir";

function getAuthHeaders(): HeadersInit {
  return { "Content-Type": "application/json" };
}

async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "GET",
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `API error ${res.status}: ${path}`);
  }
  return res.json() as Promise<T>;
}

async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `API error ${res.status}: ${path}`);
  }
  return res.json() as Promise<T>;
}

// ── Case CRUD ───────────────────────────────────────────────────────────────

export async function createCase(payload: CaseMasterCreate): Promise<CaseMasterResponse> {
  return apiPost<CaseMasterResponse>(`${FIR_PREFIX}/`, payload);
}

export async function getCase(caseId: number): Promise<CaseMasterResponse> {
  return apiGet<CaseMasterResponse>(`${FIR_PREFIX}/${caseId}`);
}

export interface ListCasesParams {
  page?: number;
  page_size?: number;
  district_id?: number | null;
  case_status_id?: number | null;
  start_date?: string | null;
  end_date?: string | null;
}

export async function listCases(params: ListCasesParams = {}): Promise<CaseListResponse> {
  const qs = new URLSearchParams();
  if (params.page) qs.set("page", String(params.page));
  if (params.page_size) qs.set("page_size", String(params.page_size));
  if (params.district_id) qs.set("district_id", String(params.district_id));
  if (params.case_status_id) qs.set("case_status_id", String(params.case_status_id));
  if (params.start_date) qs.set("start_date", params.start_date);
  if (params.end_date) qs.set("end_date", params.end_date);
  const qsStr = qs.toString();
  return apiGet<CaseListResponse>(`${FIR_PREFIX}/${qsStr ? `?${qsStr}` : ""}`);
}

// ── Lookup Endpoints ────────────────────────────────────────────────────────

export async function fetchStates(): Promise<StateDTO[]> {
  return apiGet<StateDTO[]>(`${FIR_PREFIX}/lookups/states`);
}

export async function fetchDistricts(stateId?: number | null): Promise<DistrictDTO[]> {
  const qs = stateId ? `?state_id=${stateId}` : "";
  return apiGet<DistrictDTO[]>(`${FIR_PREFIX}/lookups/districts${qs}`);
}

export async function fetchCourts(districtId?: number | null): Promise<CourtDTO[]> {
  const qs = districtId ? `?district_id=${districtId}` : "";
  return apiGet<CourtDTO[]>(`${FIR_PREFIX}/lookups/courts${qs}`);
}

export async function fetchUnits(districtId?: number | null): Promise<UnitDTO[]> {
  const qs = districtId ? `?district_id=${districtId}` : "";
  return apiGet<UnitDTO[]>(`${FIR_PREFIX}/lookups/units${qs}`);
}

export async function fetchRanks(): Promise<RankDTO[]> {
  return apiGet<RankDTO[]>(`${FIR_PREFIX}/lookups/ranks`);
}

export async function fetchDesignations(): Promise<DesignationDTO[]> {
  return apiGet<DesignationDTO[]>(`${FIR_PREFIX}/lookups/designations`);
}

export async function fetchEmployees(unitId?: number | null): Promise<EmployeeDTO[]> {
  const qs = unitId ? `?unit_id=${unitId}` : "";
  return apiGet<EmployeeDTO[]>(`${FIR_PREFIX}/lookups/employees${qs}`);
}

export async function fetchCaseCategories(): Promise<CaseCategoryDTO[]> {
  return apiGet<CaseCategoryDTO[]>(`${FIR_PREFIX}/lookups/case-categories`);
}

export async function fetchGravityOffences(): Promise<GravityOffenceDTO[]> {
  return apiGet<GravityOffenceDTO[]>(`${FIR_PREFIX}/lookups/gravity-offences`);
}

export async function fetchCaseStatuses(): Promise<CaseStatusDTO[]> {
  return apiGet<CaseStatusDTO[]>(`${FIR_PREFIX}/lookups/case-statuses`);
}

export async function fetchCastes(): Promise<CasteDTO[]> {
  return apiGet<CasteDTO[]>(`${FIR_PREFIX}/lookups/castes`);
}

export async function fetchReligions(): Promise<ReligionDTO[]> {
  return apiGet<ReligionDTO[]>(`${FIR_PREFIX}/lookups/religions`);
}

export async function fetchOccupations(): Promise<OccupationDTO[]> {
  return apiGet<OccupationDTO[]>(`${FIR_PREFIX}/lookups/occupations`);
}

export async function fetchGenders(): Promise<GenderDTO[]> {
  return apiGet<GenderDTO[]>(`${FIR_PREFIX}/lookups/genders`);
}

export async function fetchNationalities(): Promise<NationalityDTO[]> {
  return apiGet<NationalityDTO[]>(`${FIR_PREFIX}/lookups/nationalities`);
}

export async function fetchBloodGroups(): Promise<BloodGroupDTO[]> {
  return apiGet<BloodGroupDTO[]>(`${FIR_PREFIX}/lookups/blood-groups`);
}

export async function fetchActs(): Promise<ActDTO[]> {
  return apiGet<ActDTO[]>(`${FIR_PREFIX}/lookups/acts`);
}

export async function fetchSections(actCode?: string | null): Promise<SectionDTO[]> {
  const qs = actCode ? `?act_code=${encodeURIComponent(actCode)}` : "";
  return apiGet<SectionDTO[]>(`${FIR_PREFIX}/lookups/sections${qs}`);
}

export async function fetchCrimeHeads(): Promise<CrimeHeadDTO[]> {
  return apiGet<CrimeHeadDTO[]>(`${FIR_PREFIX}/lookups/crime-heads`);
}

export async function fetchCrimeSubHeads(crimeHeadId?: number | null): Promise<CrimeSubHeadDTO[]> {
  const qs = crimeHeadId ? `?crime_head_id=${crimeHeadId}` : "";
  return apiGet<CrimeSubHeadDTO[]>(`${FIR_PREFIX}/lookups/crime-sub-heads${qs}`);
}
