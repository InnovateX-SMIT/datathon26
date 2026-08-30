import { useState, useEffect, useCallback, useRef } from "react";
import {
  fetchDemographics,
  fetchSociologicalRisk,
  fetchSocioEconomicCorrelation,
} from "../services/analyticsService";
import type {
  DemographicsResponse,
  SociologicalRiskResponse,
  SocioEconomicCorrelationResponse,
} from "../types/analytics";

export function useSociologicalIntel() {
  const [demographics, setDemographics] = useState<DemographicsResponse | null>(null);
  const [sociologicalRisk, setSociologicalRisk] = useState<SociologicalRiskResponse | null>(null);
  const [socioEconomic, setSocioEconomic] = useState<SocioEconomicCorrelationResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const initialLoadDone = useRef(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [demoData, riskData, seData] = await Promise.all([
        fetchDemographics(),
        fetchSociologicalRisk(),
        fetchSocioEconomicCorrelation(),
      ]);
      setDemographics(demoData);
      setSociologicalRisk(riskData);
      setSocioEconomic(seData);
      initialLoadDone.current = true;
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || err.message || "Failed to fetch sociological intelligence data.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!initialLoadDone.current) {
      loadData();
    }
  }, [loadData]);

  useEffect(() => {
    const handleDatasetChange = () => {
      initialLoadDone.current = false;
      loadData();
    };
    window.addEventListener("activeDatasetChanged", handleDatasetChange);
    return () => {
      window.removeEventListener("activeDatasetChanged", handleDatasetChange);
    };
  }, [loadData]);

  const retry = () => {
    initialLoadDone.current = false;
    loadData();
  };

  return {
    demographics,
    sociologicalRisk,
    socioEconomic,
    loading,
    error,
    retry,
  };
}
