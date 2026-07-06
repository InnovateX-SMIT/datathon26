import { useState, useEffect, useCallback, useRef } from "react";
import {
  fetchOverview,
  fetchTrends,
  fetchCategories,
  fetchComparison,
} from "../services/analyticsService";
import type {
  OverviewResponse,
  TrendResponse,
  CategoryResponse,
  ComparisonResponse,
} from "../types/analytics";

export function useAnalytics() {
  const [overview, setOverview] = useState<OverviewResponse | null>(null);
  const [trends, setTrends] = useState<TrendResponse[]>([]);
  const [granularity, setGranularity] = useState<string>("daily");
  const [categories, setCategories] = useState<CategoryResponse | null>(null);
  const [comparison, setComparison] = useState<ComparisonResponse | null>(null);

  const [loading, setLoading] = useState<boolean>(true);
  const [loadingTrends, setLoadingTrends] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const initialLoadDone = useRef(false);

  const loadInitialData = useCallback(async (gran: string) => {
    setLoading(true);
    setError(null);
    try {
      const [over, trend, cat, comp] = await Promise.all([
        fetchOverview(),
        fetchTrends(gran),
        fetchCategories(),
        fetchComparison(),
      ]);
      setOverview(over);
      setTrends(trend);
      setCategories(cat);
      setComparison(comp);
      initialLoadDone.current = true;
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || "Failed to fetch crime analytics data. Please try again.");
    } finally {
      setLoading(false);
    }
  }, []);

  const loadTrendsOnly = useCallback(async (gran: string) => {
    setLoadingTrends(true);
    try {
      const trend = await fetchTrends(gran);
      setTrends(trend);
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || "Failed to fetch crime trends. Please try again.");
    } finally {
      setLoadingTrends(false);
    }
  }, []);

  useEffect(() => {
    if (!initialLoadDone.current) {
      loadInitialData(granularity);
    } else {
      loadTrendsOnly(granularity);
    }
  }, [granularity, loadInitialData, loadTrendsOnly]);

  useEffect(() => {
    const handleDatasetChange = () => {
      initialLoadDone.current = false;
      loadInitialData(granularity);
    };
    window.addEventListener("activeDatasetChanged", handleDatasetChange);
    return () => {
      window.removeEventListener("activeDatasetChanged", handleDatasetChange);
    };
  }, [granularity, loadInitialData]);

  const changeGranularity = (newGran: string) => {
    setGranularity(newGran);
  };

  const retry = () => {
    initialLoadDone.current = false;
    loadInitialData(granularity);
  };

  return {
    overview,
    trends,
    granularity,
    categories,
    comparison,
    loading: loading || loadingTrends,
    error,
    changeGranularity,
    retry,
  };
}
