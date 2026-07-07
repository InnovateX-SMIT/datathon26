// ══════════════════════════════════════════════════════════════════════════════
// useFirCases — Paginated case list fetching with filters
// Follows the useAnalytics.ts pattern for data fetching + dataset change events
// ══════════════════════════════════════════════════════════════════════════════

import { useState, useEffect, useCallback, useRef } from "react";
import { listCases } from "../services/firApi";
import type { CaseMasterResponse } from "../types/fir";

export interface CaseFilters {
  district_id?: number | null;
  case_status_id?: number | null;
  start_date?: string | null;
  end_date?: string | null;
}

interface UseFirCasesReturn {
  cases: CaseMasterResponse[];
  total: number;
  page: number;
  pageSize: number;
  loading: boolean;
  error: string | null;
  setPage: (page: number) => void;
  setPageSize: (size: number) => void;
  setFilters: (filters: CaseFilters) => void;
  filters: CaseFilters;
  retry: () => void;
}

export function useFirCases(initialPageSize = 10): UseFirCasesReturn {
  const [cases, setCases] = useState<CaseMasterResponse[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(initialPageSize);
  const [filters, setFilters] = useState<CaseFilters>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const mountedRef = useRef(true);

  const fetchCases = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await listCases({
        page,
        page_size: pageSize,
        district_id: filters.district_id,
        case_status_id: filters.case_status_id,
        start_date: filters.start_date,
        end_date: filters.end_date,
      });
      if (mountedRef.current) {
        setCases(result.records);
        setTotal(result.total);
      }
    } catch (err: unknown) {
      if (mountedRef.current) {
        setError(err instanceof Error ? err.message : "Failed to load FIR cases");
      }
    } finally {
      if (mountedRef.current) setLoading(false);
    }
  }, [page, pageSize, filters]);

  useEffect(() => {
    mountedRef.current = true;
    fetchCases();
    return () => {
      mountedRef.current = false;
    };
  }, [fetchCases]);

  // Re-fetch when active dataset changes
  useEffect(() => {
    const handler = () => {
      setPage(1);
      fetchCases();
    };
    window.addEventListener("activeDatasetChanged", handler);
    return () => window.removeEventListener("activeDatasetChanged", handler);
  }, [fetchCases]);

  const updateFilters = useCallback((newFilters: CaseFilters) => {
    setFilters(newFilters);
    setPage(1); // reset to first page on filter change
  }, []);

  return {
    cases,
    total,
    page,
    pageSize,
    loading,
    error,
    setPage,
    setPageSize,
    setFilters: updateFilters,
    filters,
    retry: fetchCases,
  };
}
