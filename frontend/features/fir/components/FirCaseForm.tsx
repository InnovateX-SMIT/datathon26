"use client";

import React, { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import {
  Plus,
  Trash2,
  CheckCircle2,
  AlertCircle,
  Loader2,
  ChevronDown,
  ChevronUp,
  Send,
} from "lucide-react";
import SectionHeader from "@/components/layout/section-header";
import { useFirLookups } from "../hooks/useFirLookups";
import { createCase, getCase, updateCase, fetchDistricts, fetchUnits } from "../services/firApi";
import type {
  CaseMasterCreate,
  CaseMasterResponse,
  ComplainantDetailsCreate,
  FIRVictimCreate,
  AccusedCreate,
  ActSectionAssociationCreate,
  DistrictDTO,
  UnitDTO,
  CourtDTO,
  EmployeeDTO,
  SectionDTO,
  CrimeSubHeadDTO,
} from "../types/fir";

// ── Shared input styling ────────────────────────────────────────────────────
const inputCls =
  "w-full bg-slate-900/60 border border-slate-700/60 text-slate-200 text-sm rounded-lg px-3 py-2.5 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/30 transition-colors placeholder:text-slate-600";
const selectCls = `${inputCls} appearance-none cursor-pointer`;
const labelCls = "block text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1.5";
const cardCls =
  "glass-card rounded-xl border border-slate-800/60 p-5 space-y-4";

// ── Helper: empty child factories ───────────────────────────────────────────
function emptyComplainant(): ComplainantDetailsCreate {
  return { ComplainantName: "", AgeYear: null, OccupationID: null, ReligionID: null, CasteID: null, GenderID: null };
}
function emptyVictim(): FIRVictimCreate {
  return { VictimName: "", AgeYear: null, GenderID: null, VictimPolice: "0" };
}
function emptyAccused(index: number): AccusedCreate {
  return { AccusedName: "", AgeYear: null, GenderID: null, PersonID: `A${index + 1}` };
}
function emptyActSection(): ActSectionAssociationCreate {
  return { ActCode: "", SectionCode: "", ActOrderID: null, SectionOrderID: null };
}

// ══════════════════════════════════════════════════════════════════════════════
// Component
// ══════════════════════════════════════════════════════════════════════════════
export default function FirCaseForm({ caseId }: { caseId?: number }) {
  const { lookups, loading: lookupsLoading, error: lookupsError, loadDistricts, loadUnits, loadCourts, loadEmployees, loadSections, loadCrimeSubHeads } = useFirLookups();

  // ── Cascading state ─────────────────────────────────────────────────────
  const [districts, setDistricts] = useState<DistrictDTO[]>([]);
  const [units, setUnits] = useState<UnitDTO[]>([]);
  const [courts, setCourts] = useState<CourtDTO[]>([]);
  const [employees, setEmployees] = useState<EmployeeDTO[]>([]);
  const [crimeSubHeads, setCrimeSubHeads] = useState<CrimeSubHeadDTO[]>([]);
  // Per act-section row: sections keyed by index
  const [sectionsByRow, setSectionsByRow] = useState<Record<number, SectionDTO[]>>({});

  // ── Form state ──────────────────────────────────────────────────────────
  const [selectedStateId, setSelectedStateId] = useState<number | "">("");
  const [selectedDistrictId, setSelectedDistrictId] = useState<number | "">("");
  const [selectedUnitId, setSelectedUnitId] = useState<number | "">("");

  const [crimeRegisteredDate, setCrimeRegisteredDate] = useState(
    new Date().toISOString().slice(0, 10)
  );
  const [policePersonID, setPolicePersonID] = useState<number | "">("");
  const [caseCategoryID, setCaseCategoryID] = useState<number | "">("");
  const [gravityOffenceID, setGravityOffenceID] = useState<number | "">("");
  const [crimeMajorHeadID, setCrimeMajorHeadID] = useState<number | "">("");
  const [crimeMinorHeadID, setCrimeMinorHeadID] = useState<number | "">("");
  const [caseStatusID, setCaseStatusID] = useState<number | "">("");
  const [courtID, setCourtID] = useState<number | "">("");
  const [briefFacts, setBriefFacts] = useState("");

  // Occurrence
  const [incidentFromDate, setIncidentFromDate] = useState("");
  const [incidentToDate, setIncidentToDate] = useState("");
  const [infoReceivedPSDate, setInfoReceivedPSDate] = useState("");
  const [latitude, setLatitude] = useState("");
  const [longitude, setLongitude] = useState("");
  const [occBriefFacts, setOccBriefFacts] = useState("");

  // Children
  const [complainants, setComplainants] = useState<ComplainantDetailsCreate[]>([emptyComplainant()]);
  const [victims, setVictims] = useState<FIRVictimCreate[]>([emptyVictim()]);
  const [accused, setAccused] = useState<AccusedCreate[]>([emptyAccused(0)]);
  const [actSections, setActSections] = useState<ActSectionAssociationCreate[]>([emptyActSection()]);

  // Submission
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [createdCase, setCreatedCase] = useState<CaseMasterResponse | null>(null);

  // Collapsible sections
  const [showArrest, setShowArrest] = useState(false);

  // Schema type gating
  const [schemaType, setSchemaType] = useState<string | null>(null);
  const [schemaLoading, setSchemaLoading] = useState(true);
  const [fetchingCase, setFetchingCase] = useState(!!caseId);

  useEffect(() => {
    if (!caseId) return;

    const fetchAndPopulateCase = async () => {
      setFetchingCase(true);
      try {
        const c = await getCase(caseId);
        
        // Load parent cascade IDs
        const allDistricts = await fetchDistricts(null);
        const allUnits = await fetchUnits(null);
        const matchedUnit = allUnits.find((u) => u.id === c.PoliceStationID);
        
        if (matchedUnit) {
          setSelectedStateId(matchedUnit.StateID);
          setSelectedDistrictId(matchedUnit.DistrictID);
          setSelectedUnitId(c.PoliceStationID);
          
          // Populate cascade lists
          setDistricts(allDistricts.filter((d) => d.StateID === matchedUnit.StateID));
          setUnits(allUnits.filter((u) => u.DistrictID === matchedUnit.DistrictID));
          
          const courtsForDistrict = await loadCourts(matchedUnit.DistrictID);
          setCourts(courtsForDistrict);
          
          const employeesForUnit = await loadEmployees(c.PoliceStationID);
          setEmployees(employeesForUnit);
        }

        // Set other simple fields
        if (c.CrimeRegisteredDate) {
          setCrimeRegisteredDate(c.CrimeRegisteredDate.slice(0, 10));
        }
        setPolicePersonID(c.PolicePersonID || "");
        setCaseCategoryID(c.CaseCategoryID || "");
        setGravityOffenceID(c.GravityOffenceID || "");
        setCrimeMajorHeadID(c.CrimeMajorHeadID || "");
        setCaseStatusID(c.CaseStatusID || "");
        setCourtID(c.CourtID || "");
        setBriefFacts(c.BriefFacts || "");

        // Crime Minor Head and subheads list
        if (c.CrimeMajorHeadID) {
          const subHeads = await loadCrimeSubHeads(c.CrimeMajorHeadID);
          setCrimeSubHeads(subHeads);
          setCrimeMinorHeadID(c.CrimeMinorHeadID || "");
        }

        // Occurrence
        if (c.occurrence_time) {
          const occ = c.occurrence_time;
          setIncidentFromDate(occ.IncidentFromDate?.slice(0, 10) || "");
          setIncidentToDate(occ.IncidentToDate?.slice(0, 10) || "");
          setInfoReceivedPSDate(occ.InfoReceivedPSDate?.slice(0, 10) || "");
          setLatitude(occ.latitude != null ? String(occ.latitude) : "");
          setLongitude(occ.longitude != null ? String(occ.longitude) : "");
          setOccBriefFacts(occ.BriefFacts || "");
        }

        // Children collections
        if (c.complainants && c.complainants.length > 0) {
          setComplainants(c.complainants.map(x => ({
            ComplainantName: x.ComplainantName || "",
            AgeYear: x.AgeYear || null,
            OccupationID: x.OccupationID || null,
            ReligionID: x.ReligionID || null,
            CasteID: x.CasteID || null,
            GenderID: x.GenderID || null
          })));
        } else {
          setComplainants([emptyComplainant()]);
        }

        if (c.victims && c.victims.length > 0) {
          setVictims(c.victims.map(x => ({
            VictimName: x.VictimName || "",
            AgeYear: x.AgeYear || null,
            GenderID: x.GenderID || null,
            VictimPolice: x.VictimPolice || "0"
          })));
        } else {
          setVictims([emptyVictim()]);
        }

        if (c.accused && c.accused.length > 0) {
          setAccused(c.accused.map(x => ({
            AccusedName: x.AccusedName || "",
            AgeYear: x.AgeYear || null,
            GenderID: x.GenderID || null,
            PersonID: x.PersonID || ""
          })));
        } else {
          setAccused([emptyAccused(0)]);
        }

        if (c.act_sections && c.act_sections.length > 0) {
          setActSections(c.act_sections.map(x => ({
            ActCode: x.ActCode || "",
            SectionCode: x.SectionCode || "",
            ActOrderID: x.ActOrderID || null,
            SectionOrderID: x.SectionOrderID || null
          })));

          // Populate sections dropdowns for each row
          const sectionsMap: Record<number, SectionDTO[]> = {};
          for (let i = 0; i < c.act_sections.length; i++) {
            const row = c.act_sections[i];
            if (row.ActCode) {
              const secList = await loadSections(row.ActCode);
              sectionsMap[i] = secList;
            }
          }
          setSectionsByRow(sectionsMap);
        } else {
          setActSections([emptyActSection()]);
        }

      } catch (err: unknown) {
        console.error("Failed to fetch case for editing:", err);
        setSubmitError(err instanceof Error ? err.message : "Failed to load case data");
      } finally {
        setFetchingCase(false);
      }
    };

    fetchAndPopulateCase();
  }, [caseId, loadCourts, loadEmployees, loadSections, loadCrimeSubHeads]);

  useEffect(() => {
    import("@/services/dataset.service").then((s) => {
      s.fetchActiveDatasets()
        .then((activeList) => {
          if (activeList && activeList.length > 0) {
            const active = activeList.find((ds) => ds.is_active);
            if (active) {
              setSchemaType(active.schema_type || "legacy_crime_intel");
            } else {
              setSchemaType("legacy_crime_intel");
            }
          } else {
            setSchemaType("legacy_crime_intel");
          }
        })
        .catch((err) => {
          console.error("Failed to fetch active dataset schema type:", err);
          setSchemaType("legacy_crime_intel");
        })
        .finally(() => {
          setSchemaLoading(false);
        });
    });
  }, []);

  // ── Cascading effects ─────────────────────────────────────────────────────
  useEffect(() => {
    if (selectedStateId !== "") {
      loadDistricts(selectedStateId as number).then(setDistricts).catch(() => setDistricts([]));
      setSelectedDistrictId("");
      setUnits([]);
      setCourts([]);
      setEmployees([]);
      setSelectedUnitId("");
    }
  }, [selectedStateId, loadDistricts]);

  useEffect(() => {
    if (selectedDistrictId !== "") {
      loadUnits(selectedDistrictId as number).then(setUnits).catch(() => setUnits([]));
      loadCourts(selectedDistrictId as number).then(setCourts).catch(() => setCourts([]));
      setSelectedUnitId("");
      setEmployees([]);
    }
  }, [selectedDistrictId, loadUnits, loadCourts]);

  useEffect(() => {
    if (selectedUnitId !== "") {
      loadEmployees(selectedUnitId as number).then(setEmployees).catch(() => setEmployees([]));
    }
  }, [selectedUnitId, loadEmployees]);

  useEffect(() => {
    if (crimeMajorHeadID !== "") {
      loadCrimeSubHeads(crimeMajorHeadID as number).then(setCrimeSubHeads).catch(() => setCrimeSubHeads([]));
      setCrimeMinorHeadID("");
    }
  }, [crimeMajorHeadID, loadCrimeSubHeads]);

  // ── Child array helpers ───────────────────────────────────────────────────
  const addComplainant = () => setComplainants((p) => [...p, emptyComplainant()]);
  const removeComplainant = (i: number) => setComplainants((p) => p.filter((_, idx) => idx !== i));
  const updateComplainant = (i: number, field: keyof ComplainantDetailsCreate, val: string | number | null) =>
    setComplainants((p) => p.map((c, idx) => (idx === i ? { ...c, [field]: val } : c)));

  const addVictim = () => setVictims((p) => [...p, emptyVictim()]);
  const removeVictim = (i: number) => setVictims((p) => p.filter((_, idx) => idx !== i));
  const updateVictim = (i: number, field: keyof FIRVictimCreate, val: string | number | null) =>
    setVictims((p) => p.map((v, idx) => (idx === i ? { ...v, [field]: val } : v)));

  const addAccused = () => setAccused((p) => [...p, emptyAccused(p.length)]);
  const removeAccused = (i: number) => setAccused((p) => p.filter((_, idx) => idx !== i));
  const updateAccused = (i: number, field: keyof AccusedCreate, val: string | number | null) =>
    setAccused((p) => p.map((a, idx) => (idx === i ? { ...a, [field]: val } : a)));

  const addActSection = () => setActSections((p) => [...p, emptyActSection()]);
  const removeActSection = (i: number) => {
    setActSections((p) => p.filter((_, idx) => idx !== i));
    setSectionsByRow((prev) => {
      const next = { ...prev };
      delete next[i];
      return next;
    });
  };
  const updateActSection = (i: number, field: keyof ActSectionAssociationCreate, val: string | number | null) =>
    setActSections((p) => p.map((a, idx) => (idx === i ? { ...a, [field]: val } : a)));

  const handleActChange = useCallback(
    async (rowIndex: number, actCode: string) => {
      updateActSection(rowIndex, "ActCode", actCode);
      updateActSection(rowIndex, "SectionCode", "");
      if (actCode) {
        try {
          const sections = await loadSections(actCode);
          setSectionsByRow((prev) => ({ ...prev, [rowIndex]: sections }));
        } catch {
          setSectionsByRow((prev) => ({ ...prev, [rowIndex]: [] }));
        }
      } else {
        setSectionsByRow((prev) => ({ ...prev, [rowIndex]: [] }));
      }
    },
    [loadSections]
  );

  // ── Submit ────────────────────────────────────────────────────────────────
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setSubmitError(null);
    setCreatedCase(null);

    if (
      !crimeRegisteredDate ||
      policePersonID === "" ||
      selectedUnitId === "" ||
      caseCategoryID === "" ||
      gravityOffenceID === "" ||
      crimeMajorHeadID === "" ||
      crimeMinorHeadID === "" ||
      caseStatusID === "" ||
      courtID === ""
    ) {
      setSubmitError("Please select all required fields (State, District, Police Station, Officer, Category, Gravity, Crime Major Head, Crime Minor Head, Case Status, and Court) before submitting.");
      setSubmitting(false);
      return;
    }

    const payload: CaseMasterCreate = {
      CrimeRegisteredDate: crimeRegisteredDate || null,
      PolicePersonID: policePersonID as number,
      PoliceStationID: selectedUnitId as number,
      CaseCategoryID: caseCategoryID as number,
      GravityOffenceID: gravityOffenceID as number,
      CrimeMajorHeadID: crimeMajorHeadID as number,
      CrimeMinorHeadID: crimeMinorHeadID as number,
      CaseStatusID: caseStatusID as number,
      CourtID: courtID as number,
      BriefFacts: briefFacts || null,
      occurrence_time: {
        IncidentFromDate: incidentFromDate ? `${incidentFromDate}T00:00:00` : null,
        IncidentToDate: incidentToDate ? `${incidentToDate}T00:00:00` : null,
        InfoReceivedPSDate: infoReceivedPSDate ? `${infoReceivedPSDate}T00:00:00` : null,
        latitude: latitude ? parseFloat(latitude) : null,
        longitude: longitude ? parseFloat(longitude) : null,
        BriefFacts: occBriefFacts || null,
      },
      complainants: complainants.filter((c) => c.ComplainantName.trim()),
      victims: victims.filter((v) => v.VictimName.trim()),
      accused: accused.filter((a) => a.AccusedName.trim()),
      act_sections: actSections.filter((a) => a.ActCode && a.SectionCode),
      arrest_surrenders: [],
      chargesheets: [],
    };

    try {
      let result;
      if (caseId) {
        // Pre-fetch original CrimeNo and CaseNo so we preserve them correctly on backend update
        const orig = await getCase(caseId);
        payload.CrimeNo = orig.CrimeNo;
        payload.CaseNo = orig.CaseNo;
        
        result = await updateCase(caseId, payload);
      } else {
        result = await createCase(payload);
      }
      setCreatedCase(result);
      window.dispatchEvent(new Event("activeDatasetChanged"));
    } catch (err: unknown) {
      setSubmitError(err instanceof Error ? err.message : "Failed to save case");
    } finally {
      setSubmitting(false);
    }
  };

  // ── Loading state ─────────────────────────────────────────────────────────
  if (lookupsLoading || fetchingCase) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex items-center gap-3 text-slate-400">
          <Loader2 className="w-5 h-5 animate-spin" />
          <span className="text-sm font-medium">Loading form data...</span>
        </div>
      </div>
    );
  }

  if (lookupsError) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] text-center">
        <AlertCircle className="w-10 h-10 text-red-500 mb-3" />
        <p className="text-sm text-slate-300 mb-4">{lookupsError}</p>
      </div>
    );
  }

  if (!lookups) return null;

  // ── Success state ─────────────────────────────────────────────────────────
  if (createdCase) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="glass-card rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-8 text-center space-y-5 animate-fade-in">
          <CheckCircle2 className="w-16 h-16 text-emerald-400 mx-auto" />
          <h2 className="text-xl font-bold text-slate-100 uppercase tracking-tight">
            FIR Case {caseId ? "Updated" : "Created"} Successfully
          </h2>
          <div className="grid grid-cols-2 gap-4 text-left max-w-sm mx-auto">
            <div>
              <span className={labelCls}>Crime No</span>
              <p className="text-sm font-mono text-emerald-400 font-bold">
                {createdCase.CrimeNo}
              </p>
            </div>
            <div>
              <span className={labelCls}>Case No</span>
              <p className="text-sm font-mono text-emerald-400 font-bold">
                {createdCase.CaseNo}
              </p>
            </div>
            <div>
              <span className={labelCls}>Case ID</span>
              <p className="text-sm font-mono text-slate-300">
                #{createdCase.id}
              </p>
            </div>
            <div>
              <span className={labelCls}>Registered</span>
              <p className="text-sm font-mono text-slate-300">
                {createdCase.CrimeRegisteredDate}
              </p>
            </div>
          </div>
          <div className="flex items-center justify-center gap-3 pt-2">
            <Link
              href={`/fir/cases/${createdCase.id}`}
              className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs uppercase tracking-wider rounded-xl transition-colors"
            >
              View Case Details
            </Link>
            {caseId ? (
              <Link
                href="/fir/cases"
                className="px-5 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold text-xs uppercase tracking-wider rounded-xl transition-colors border border-slate-700 cursor-pointer"
              >
                Back to List
              </Link>
            ) : (
              <button
                onClick={() => window.location.reload()}
                className="px-5 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold text-xs uppercase tracking-wider rounded-xl transition-colors border border-slate-700 cursor-pointer"
              >
                Register Another
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  // ── Render helper for select ──────────────────────────────────────────────
  const renderSelect = (
    value: number | string,
    onChange: (v: string) => void,
    options: { value: string | number; label: string }[],
    placeholder = "Select..."
  ) => (
    <select className={selectCls} value={value} onChange={(e) => onChange(e.target.value)}>
      <option value="">{placeholder}</option>
      {options.map((o) => (
        <option key={o.value} value={o.value}>
          {o.label}
        </option>
      ))}
    </select>
  );

  return (
    <form onSubmit={handleSubmit} className="space-y-8 animate-fade-in">
      {/* ── Section 1: Case Registration ──────────────────────────────────── */}
      <div className={cardCls}>
        <SectionHeader title="Case Registration" accentColor="bg-indigo-500" />

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {/* Crime Registered Date */}
          <div>
            <label className={labelCls}>Crime Registered Date</label>
            <input
              type="date"
              className={inputCls}
              value={crimeRegisteredDate}
              onChange={(e) => setCrimeRegisteredDate(e.target.value)}
              required
            />
          </div>

          {/* State → District → Unit (cascading) */}
          <div>
            <label className={labelCls}>State</label>
            {renderSelect(
              selectedStateId,
              (v) => setSelectedStateId(v ? Number(v) : ""),
              lookups.states.map((s) => ({ value: s.id, label: s.name })),
              "Select State..."
            )}
          </div>
          <div>
            <label className={labelCls}>District</label>
            {renderSelect(
              selectedDistrictId,
              (v) => setSelectedDistrictId(v ? Number(v) : ""),
              districts.map((d) => ({ value: d.id, label: d.name })),
              selectedStateId ? "Select District..." : "Select State first"
            )}
          </div>
          <div>
            <label className={labelCls}>Police Station (Unit)</label>
            {renderSelect(
              selectedUnitId,
              (v) => setSelectedUnitId(v ? Number(v) : ""),
              units.map((u) => ({ value: u.id, label: u.name })),
              selectedDistrictId ? "Select Unit..." : "Select District first"
            )}
          </div>

          {/* Officer (Employee, cascading by unit) */}
          <div>
            <label className={labelCls}>Investigating Officer</label>
            {renderSelect(
              policePersonID,
              (v) => setPolicePersonID(v ? Number(v) : ""),
              employees.map((e) => ({ value: e.id, label: `${e.FirstName} (${e.KGID})` })),
              selectedUnitId ? "Select Officer..." : "Select Unit first"
            )}
          </div>

          {/* Case Category */}
          <div>
            <label className={labelCls}>Case Category</label>
            {renderSelect(
              caseCategoryID,
              (v) => setCaseCategoryID(v ? Number(v) : ""),
              lookups.caseCategories.map((c) => ({ value: c.id, label: c.name }))
            )}
          </div>

          {/* Gravity Offence */}
          <div>
            <label className={labelCls}>Gravity of Offence</label>
            {renderSelect(
              gravityOffenceID,
              (v) => setGravityOffenceID(v ? Number(v) : ""),
              lookups.gravityOffences.map((g) => ({ value: g.id, label: g.name }))
            )}
          </div>

          {/* Crime Head → Crime Sub Head (cascading) */}
          <div>
            <label className={labelCls}>Crime Major Head</label>
            {renderSelect(
              crimeMajorHeadID,
              (v) => setCrimeMajorHeadID(v ? Number(v) : ""),
              lookups.crimeHeads.map((h) => ({ value: h.id, label: h.CrimeGroupName }))
            )}
          </div>
          <div>
            <label className={labelCls}>Crime Minor Head</label>
            {renderSelect(
              crimeMinorHeadID,
              (v) => setCrimeMinorHeadID(v ? Number(v) : ""),
              crimeSubHeads.map((s) => ({ value: s.id, label: s.CrimeHeadName })),
              crimeMajorHeadID ? "Select Sub-Head..." : "Select Major Head first"
            )}
          </div>

          {/* Case Status */}
          <div>
            <label className={labelCls}>Case Status</label>
            {renderSelect(
              caseStatusID,
              (v) => setCaseStatusID(v ? Number(v) : ""),
              lookups.caseStatuses.map((s) => ({ value: s.id, label: s.name }))
            )}
          </div>

          {/* Court (cascading by district) */}
          <div>
            <label className={labelCls}>Court</label>
            {renderSelect(
              courtID,
              (v) => setCourtID(v ? Number(v) : ""),
              courts.map((c) => ({ value: c.id, label: c.name })),
              selectedDistrictId ? "Select Court..." : "Select District first"
            )}
          </div>
        </div>

        {/* Brief Facts */}
        <div>
          <label className={labelCls}>Brief Facts</label>
          <textarea
            className={`${inputCls} min-h-[80px] resize-y`}
            value={briefFacts}
            onChange={(e) => setBriefFacts(e.target.value)}
            placeholder="Enter brief facts of the case..."
          />
        </div>
      </div>

      {/* ── Section 2: Occurrence Details ─────────────────────────────────── */}
      <div className={cardCls}>
        <SectionHeader title="Occurrence Details" accentColor="bg-cyan-500" />

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div>
            <label className={labelCls}>Incident From Date</label>
            <input type="date" className={inputCls} value={incidentFromDate} onChange={(e) => setIncidentFromDate(e.target.value)} />
          </div>
          <div>
            <label className={labelCls}>Incident To Date</label>
            <input type="date" className={inputCls} value={incidentToDate} onChange={(e) => setIncidentToDate(e.target.value)} />
          </div>
          <div>
            <label className={labelCls}>Info Received at PS Date</label>
            <input type="date" className={inputCls} value={infoReceivedPSDate} onChange={(e) => setInfoReceivedPSDate(e.target.value)} />
          </div>
          <div>
            <label className={labelCls}>Latitude</label>
            <input type="number" step="any" className={inputCls} value={latitude} onChange={(e) => setLatitude(e.target.value)} placeholder="e.g. 12.9716" />
          </div>
          <div>
            <label className={labelCls}>Longitude</label>
            <input type="number" step="any" className={inputCls} value={longitude} onChange={(e) => setLongitude(e.target.value)} placeholder="e.g. 77.5946" />
          </div>
        </div>
        <div>
          <label className={labelCls}>Occurrence Brief Facts</label>
          <textarea
            className={`${inputCls} min-h-[80px] resize-y`}
            value={occBriefFacts}
            onChange={(e) => setOccBriefFacts(e.target.value)}
            placeholder="Describe the occurrence details..."
          />
        </div>
      </div>

      {/* ── Section 3: Complainants ──────────────────────────────────────── */}
      <div className={cardCls}>
        <div className="flex items-center justify-between">
          <SectionHeader title="Complainant(s)" accentColor="bg-amber-500" className="mb-0" />
          <button type="button" onClick={addComplainant} className="flex items-center gap-1.5 text-xs font-bold text-indigo-400 hover:text-indigo-300 transition-colors cursor-pointer">
            <Plus className="w-3.5 h-3.5" /> Add
          </button>
        </div>
        <div className="space-y-4">
          {complainants.map((comp, i) => (
            <div key={i} className="grid grid-cols-1 md:grid-cols-6 gap-3 items-end bg-slate-900/30 rounded-lg p-3 border border-slate-800/40">
              <div className="md:col-span-2">
                <label className={labelCls}>Name</label>
                <input className={inputCls} value={comp.ComplainantName} onChange={(e) => updateComplainant(i, "ComplainantName", e.target.value)} placeholder="Complainant name" />
              </div>
              <div>
                <label className={labelCls}>Age</label>
                <input type="number" min={0} max={125} className={inputCls} value={comp.AgeYear ?? ""} onChange={(e) => updateComplainant(i, "AgeYear", e.target.value ? Number(e.target.value) : null)} />
              </div>
              <div>
                <label className={labelCls}>Gender</label>
                {renderSelect(comp.GenderID ?? "", (v) => updateComplainant(i, "GenderID", v ? Number(v) : null), lookups.genders.map((g) => ({ value: g.id, label: g.name })))}
              </div>
              <div>
                <label className={labelCls}>Caste</label>
                {renderSelect(comp.CasteID ?? "", (v) => updateComplainant(i, "CasteID", v ? Number(v) : null), lookups.castes.map((c) => ({ value: c.id, label: c.name })))}
              </div>
              <div className="flex items-end gap-2">
                <div className="flex-1">
                  <label className={labelCls}>Religion</label>
                  {renderSelect(comp.ReligionID ?? "", (v) => updateComplainant(i, "ReligionID", v ? Number(v) : null), lookups.religions.map((r) => ({ value: r.id, label: r.name })))}
                </div>
                {complainants.length > 1 && (
                  <button type="button" onClick={() => removeComplainant(i)} className="p-2 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-lg transition-colors cursor-pointer">
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ── Section 4: Victims ───────────────────────────────────────────── */}
      <div className={cardCls}>
        <div className="flex items-center justify-between">
          <SectionHeader title="Victim(s)" accentColor="bg-red-500" className="mb-0" />
          <button type="button" onClick={addVictim} className="flex items-center gap-1.5 text-xs font-bold text-indigo-400 hover:text-indigo-300 transition-colors cursor-pointer">
            <Plus className="w-3.5 h-3.5" /> Add
          </button>
        </div>
        <div className="space-y-4">
          {victims.map((vic, i) => (
            <div key={i} className="grid grid-cols-1 md:grid-cols-5 gap-3 items-end bg-slate-900/30 rounded-lg p-3 border border-slate-800/40">
              <div className="md:col-span-2">
                <label className={labelCls}>Name</label>
                <input className={inputCls} value={vic.VictimName} onChange={(e) => updateVictim(i, "VictimName", e.target.value)} placeholder="Victim name" />
              </div>
              <div>
                <label className={labelCls}>Age</label>
                <input type="number" min={0} max={125} className={inputCls} value={vic.AgeYear ?? ""} onChange={(e) => updateVictim(i, "AgeYear", e.target.value ? Number(e.target.value) : null)} />
              </div>
              <div>
                <label className={labelCls}>Gender</label>
                {renderSelect(vic.GenderID ?? "", (v) => updateVictim(i, "GenderID", v ? Number(v) : null), lookups.genders.map((g) => ({ value: g.id, label: g.name })))}
              </div>
              <div className="flex items-end gap-2">
                <div className="flex-1">
                  <label className={labelCls}>Victim is Police</label>
                  <select className={selectCls} value={vic.VictimPolice} onChange={(e) => updateVictim(i, "VictimPolice", e.target.value)}>
                    <option value="0">No</option>
                    <option value="1">Yes</option>
                  </select>
                </div>
                {victims.length > 1 && (
                  <button type="button" onClick={() => removeVictim(i)} className="p-2 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-lg transition-colors cursor-pointer">
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ── Section 5: Accused ───────────────────────────────────────────── */}
      <div className={cardCls}>
        <div className="flex items-center justify-between">
          <SectionHeader title="Accused Person(s)" accentColor="bg-violet-500" className="mb-0" />
          <button type="button" onClick={addAccused} className="flex items-center gap-1.5 text-xs font-bold text-indigo-400 hover:text-indigo-300 transition-colors cursor-pointer">
            <Plus className="w-3.5 h-3.5" /> Add
          </button>
        </div>
        <div className="space-y-4">
          {accused.map((acc, i) => (
            <div key={i} className="grid grid-cols-1 md:grid-cols-5 gap-3 items-end bg-slate-900/30 rounded-lg p-3 border border-slate-800/40">
              <div className="md:col-span-2">
                <label className={labelCls}>Name</label>
                <input className={inputCls} value={acc.AccusedName} onChange={(e) => updateAccused(i, "AccusedName", e.target.value)} placeholder="Accused name" />
              </div>
              <div>
                <label className={labelCls}>Age</label>
                <input type="number" min={0} max={125} className={inputCls} value={acc.AgeYear ?? ""} onChange={(e) => updateAccused(i, "AgeYear", e.target.value ? Number(e.target.value) : null)} />
              </div>
              <div>
                <label className={labelCls}>Gender</label>
                {renderSelect(acc.GenderID ?? "", (v) => updateAccused(i, "GenderID", v ? Number(v) : null), lookups.genders.map((g) => ({ value: g.id, label: g.name })))}
              </div>
              <div className="flex items-end gap-2">
                <div className="flex-1">
                  <label className={labelCls}>Person ID</label>
                  <input className={inputCls} value={acc.PersonID ?? ""} onChange={(e) => updateAccused(i, "PersonID", e.target.value || null)} placeholder={`A${i + 1}`} />
                </div>
                {accused.length > 1 && (
                  <button type="button" onClick={() => removeAccused(i)} className="p-2 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-lg transition-colors cursor-pointer">
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ── Section 6: Act/Section Associations ──────────────────────────── */}
      <div className={cardCls}>
        <div className="flex items-center justify-between">
          <SectionHeader title="Act & Section" accentColor="bg-emerald-500" className="mb-0" />
          <button type="button" onClick={addActSection} className="flex items-center gap-1.5 text-xs font-bold text-indigo-400 hover:text-indigo-300 transition-colors cursor-pointer">
            <Plus className="w-3.5 h-3.5" /> Add
          </button>
        </div>
        <div className="space-y-4">
          {actSections.map((as, i) => (
            <div key={i} className="grid grid-cols-1 md:grid-cols-5 gap-3 items-end bg-slate-900/30 rounded-lg p-3 border border-slate-800/40">
              <div className="md:col-span-2">
                <label className={labelCls}>Act</label>
                {renderSelect(
                  as.ActCode,
                  (v) => handleActChange(i, v),
                  lookups.acts.map((a) => ({ value: a.ActCode, label: a.ShortName || a.ActDescription || a.ActCode })),
                  "Select Act..."
                )}
              </div>
              <div className="md:col-span-2">
                <label className={labelCls}>Section</label>
                {renderSelect(
                  as.SectionCode,
                  (v) => updateActSection(i, "SectionCode", v),
                  (sectionsByRow[i] || []).map((s) => ({ value: s.SectionCode, label: s.SectionDescription || s.SectionCode })),
                  as.ActCode ? "Select Section..." : "Select Act first"
                )}
              </div>
              <div className="flex items-end gap-2">
                <div className="flex-1">
                  <label className={labelCls}>Order</label>
                  <input type="number" className={inputCls} value={as.ActOrderID ?? ""} onChange={(e) => updateActSection(i, "ActOrderID", e.target.value ? Number(e.target.value) : null)} placeholder="#" />
                </div>
                {actSections.length > 1 && (
                  <button type="button" onClick={() => removeActSection(i)} className="p-2 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-lg transition-colors cursor-pointer">
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ── Section 7: Arrest/Surrender (Optional, Collapsible) ──────────── */}
      <div className={cardCls}>
        <button
          type="button"
          onClick={() => setShowArrest(!showArrest)}
          className="flex items-center justify-between w-full cursor-pointer"
        >
          <SectionHeader title="Arrest / Surrender (Optional)" accentColor="bg-slate-500" className="mb-0" />
          {showArrest ? <ChevronUp className="w-4 h-4 text-slate-500" /> : <ChevronDown className="w-4 h-4 text-slate-500" />}
        </button>
        {showArrest && (
          <p className="text-xs text-slate-500 mt-2">
            Arrest/surrender records can be added after the case is created via the Case Detail view. This section is optional at initial filing.
          </p>
        )}
      </div>

      {/* ── Submit ───────────────────────────────────────────────────────── */}
      {submitError && (
        <div className="flex items-center gap-3 bg-red-500/10 border border-red-500/20 rounded-xl p-4 animate-shake">
          <AlertCircle className="w-5 h-5 text-red-500 shrink-0" />
          <p className="text-sm text-red-400">{submitError}</p>
        </div>
      )}

      {/* ── Schema Gating Warning Banner ── */}
      {schemaType === "legacy_crime_intel" && !schemaLoading && (
        <div className="flex items-start gap-3 bg-amber-500/10 border border-amber-500/20 rounded-xl p-4">
          <AlertCircle className="w-5 h-5 text-amber-500 shrink-0 mt-0.5 animate-pulse" />
          <div>
            <h4 className="text-sm font-bold text-amber-400">FIR Case Registration Restricted</h4>
            <p className="text-xs text-amber-500/90 mt-1 leading-relaxed">
              New FIR case registration is only supported under standard schemas (e.g. Standard FIR v1). 
              The currently active dataset uses a Legacy/Unvalidated schema, which restricts data modification to protect database consistency.
            </p>
          </div>
        </div>
      )}

      <div className="flex justify-end">
        <button
          type="submit"
          disabled={submitting || schemaType === "legacy_crime_intel" || schemaLoading}
          className="flex items-center gap-2.5 px-8 py-3 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-800 disabled:cursor-not-allowed text-white font-bold text-sm uppercase tracking-wider rounded-xl transition-all duration-200 shadow-lg shadow-indigo-600/20 cursor-pointer"
        >
          {submitting ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Registering Case...
            </>
          ) : (
            <>
              <Send className="w-4 h-4" />
              Register FIR Case
            </>
          )}
        </button>
      </div>
    </form>
  );
}
