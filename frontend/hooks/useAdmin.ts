import { useState, useEffect, useCallback } from "react";
import type {
  AuditLogListResponse,
  SystemHealth,
  ModelStatusResponse,
  DatasetStatusResponse,
} from "@/features/admin/types/admin";
import {
  fetchSystemHealth,
  fetchModelStatus,
  fetchAuditLogs,
  fetchDatasetStatus,
} from "@/features/admin/services/admin-service";

export function useAdmin() {
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [modelStatus, setModelStatus] = useState<ModelStatusResponse | null>(null);
  const [auditLogs, setAuditLogs] = useState<AuditLogListResponse | null>(null);
  const [datasetStatus, setDatasetStatus] = useState<DatasetStatusResponse | null>(null);

  const [healthLoading, setHealthLoading] = useState(false);
  const [modelsLoading, setModelsLoading] = useState(false);
  const [auditLoading, setAuditLoading] = useState(false);
  const [datasetLoading, setDatasetLoading] = useState(false);

  const [error, setError] = useState<string | null>(null);
  const [auditPage, setAuditPage] = useState(1);
  const [auditPageSize] = useState(50);
  const [auditActionFilter, setAuditActionFilter] = useState("ALL");

  const loadSystemHealth = useCallback(async () => {
    setHealthLoading(true);
    setError(null);
    try {
      const data = await fetchSystemHealth();
      setSystemHealth(data);
    } catch {
      setError("Failed to load system health.");
    } finally {
      setHealthLoading(false);
    }
  }, []);

  const loadModelStatus = useCallback(async () => {
    setModelsLoading(true);
    setError(null);
    try {
      const data = await fetchModelStatus();
      setModelStatus(data);
    } catch {
      setError("Failed to load model status.");
    } finally {
      setModelsLoading(false);
    }
  }, []);

  const loadAuditLogs = useCallback(async () => {
    setAuditLoading(true);
    setError(null);
    try {
      const data = await fetchAuditLogs(
        auditPage,
        auditPageSize,
        auditActionFilter !== "ALL" ? auditActionFilter : undefined
      );
      setAuditLogs(data);
    } catch {
      setError("Failed to load audit logs.");
    } finally {
      setAuditLoading(false);
    }
  }, [auditPage, auditPageSize, auditActionFilter]);

  const loadDatasetStatus = useCallback(async () => {
    setDatasetLoading(true);
    setError(null);
    try {
      const data = await fetchDatasetStatus();
      setDatasetStatus(data);
    } catch {
      setError("Failed to load dataset status.");
    } finally {
      setDatasetLoading(false);
    }
  }, []);

  useEffect(() => {
    if (auditLogs !== null) {
      loadAuditLogs();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [auditPage, auditActionFilter]);

  return {
    systemHealth,
    modelStatus,
    auditLogs,
    datasetStatus,
    healthLoading,
    modelsLoading,
    auditLoading,
    datasetLoading,
    error,
    auditPage,
    auditPageSize,
    auditActionFilter,
    setAuditPage,
    setAuditActionFilter,
    loadSystemHealth,
    loadModelStatus,
    loadAuditLogs,
    loadDatasetStatus,
  };
}
