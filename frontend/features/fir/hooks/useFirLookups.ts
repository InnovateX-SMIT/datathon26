// ══════════════════════════════════════════════════════════════════════════════
// useFirLookups — Fetch and cache all FIR lookup/master data once
// Exposes cascading fetch helpers for dependent dropdowns
// ══════════════════════════════════════════════════════════════════════════════

import { useState, useEffect, useCallback, useRef } from "react";
import {
  fetchStates,
  fetchRanks,
  fetchDesignations,
  fetchCaseCategories,
  fetchGravityOffences,
  fetchCaseStatuses,
  fetchCastes,
  fetchReligions,
  fetchOccupations,
  fetchGenders,
  fetchNationalities,
  fetchBloodGroups,
  fetchActs,
  fetchCrimeHeads,
  fetchDistricts,
  fetchUnits,
  fetchCourts,
  fetchEmployees,
  fetchSections,
  fetchCrimeSubHeads,
} from "../services/firApi";
import type {
  FirLookupData,
  DistrictDTO,
  UnitDTO,
  CourtDTO,
  EmployeeDTO,
  SectionDTO,
  CrimeSubHeadDTO,
} from "../types/fir";

interface UseFirLookupsReturn {
  lookups: FirLookupData | null;
  loading: boolean;
  error: string | null;
  // Cascading fetch helpers
  loadDistricts: (stateId: number) => Promise<DistrictDTO[]>;
  loadUnits: (districtId: number) => Promise<UnitDTO[]>;
  loadCourts: (districtId: number) => Promise<CourtDTO[]>;
  loadEmployees: (unitId: number) => Promise<EmployeeDTO[]>;
  loadSections: (actCode: string) => Promise<SectionDTO[]>;
  loadCrimeSubHeads: (crimeHeadId: number) => Promise<CrimeSubHeadDTO[]>;
}

// Module-level cache to avoid re-fetching on every mount
let _cachedLookups: FirLookupData | null = null;
let _cachePromise: Promise<FirLookupData> | null = null;

export function useFirLookups(): UseFirLookupsReturn {
  const [lookups, setLookups] = useState<FirLookupData | null>(_cachedLookups);
  const [loading, setLoading] = useState(!_cachedLookups);
  const [error, setError] = useState<string | null>(null);
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;
    if (_cachedLookups) {
      setLookups(_cachedLookups);
      setLoading(false);
      return;
    }

    // If another instance is already fetching, reuse the promise
    if (!_cachePromise) {
      _cachePromise = Promise.all([
        fetchStates(),
        fetchRanks(),
        fetchDesignations(),
        fetchCaseCategories(),
        fetchGravityOffences(),
        fetchCaseStatuses(),
        fetchCastes(),
        fetchReligions(),
        fetchOccupations(),
        fetchGenders(),
        fetchNationalities(),
        fetchBloodGroups(),
        fetchActs(),
        fetchCrimeHeads(),
      ]).then(
        ([
          states,
          ranks,
          designations,
          caseCategories,
          gravityOffences,
          caseStatuses,
          castes,
          religions,
          occupations,
          genders,
          nationalities,
          bloodGroups,
          acts,
          crimeHeads,
        ]) => {
          const data: FirLookupData = {
            states,
            ranks,
            designations,
            caseCategories,
            gravityOffences,
            caseStatuses,
            castes,
            religions,
            occupations,
            genders,
            nationalities,
            bloodGroups,
            acts,
            crimeHeads,
          };
          _cachedLookups = data;
          return data;
        }
      );
    }

    setLoading(true);
    _cachePromise
      .then((data) => {
        if (mountedRef.current) {
          setLookups(data);
          setError(null);
        }
      })
      .catch((err) => {
        if (mountedRef.current) {
          setError(err?.message || "Failed to load FIR lookup data");
        }
        _cachePromise = null; // allow retry
      })
      .finally(() => {
        if (mountedRef.current) setLoading(false);
      });

    return () => {
      mountedRef.current = false;
    };
  }, []);

  // Cascading fetch helpers — not cached globally since they depend on parent selection
  const loadDistricts = useCallback(async (stateId: number) => {
    return fetchDistricts(stateId);
  }, []);

  const loadUnits = useCallback(async (districtId: number) => {
    return fetchUnits(districtId);
  }, []);

  const loadCourts = useCallback(async (districtId: number) => {
    return fetchCourts(districtId);
  }, []);

  const loadEmployees = useCallback(async (unitId: number) => {
    return fetchEmployees(unitId);
  }, []);

  const loadSections = useCallback(async (actCode: string) => {
    return fetchSections(actCode);
  }, []);

  const loadCrimeSubHeads = useCallback(async (crimeHeadId: number) => {
    return fetchCrimeSubHeads(crimeHeadId);
  }, []);

  return {
    lookups,
    loading,
    error,
    loadDistricts,
    loadUnits,
    loadCourts,
    loadEmployees,
    loadSections,
    loadCrimeSubHeads,
  };
}
