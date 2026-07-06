import { useState, useEffect, useCallback } from "react";
import type { Alert, AlertSummary } from "@/types/alert";
import {
  fetchAlerts,
  fetchAlertSummary,
  generateAlerts,
  updateAlertStatus,
} from "@/services/alert.service";

export function useAlerts() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [summary, setSummary] = useState<AlertSummary>({
    total_active: 0,
    critical_count: 0,
    resolved_count: 0,
    today_count: 0,
    by_source: [],
    by_severity: [],
  });

  const [alertsLoading, setAlertsLoading] = useState(false);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [statusFilter, setStatusFilter] = useState<string>("");
  const [severityFilter, setSeverityFilter] = useState<string>("");
  const [sourceFilter, setSourceFilter] = useState<string>("");

  // Load alerts
  const loadAlerts = useCallback(async () => {
    setAlertsLoading(true);
    setError(null);
    try {
      const data = await fetchAlerts(
        statusFilter || undefined,
        severityFilter || undefined,
        sourceFilter || undefined
      );
      setAlerts(data);
    } catch (err: unknown) {
      console.error("Error loading alerts:", err);
      setError("Failed to load operational alerts.");
    } finally {
      setAlertsLoading(false);
    }
  }, [statusFilter, severityFilter, sourceFilter]);

  // Load summary stats
  const loadSummary = useCallback(async () => {
    setSummaryLoading(true);
    try {
      const data = await fetchAlertSummary();
      setSummary(data);
    } catch (err: unknown) {
      console.error("Error loading alert summary:", err);
    } finally {
      setSummaryLoading(false);
    }
  }, []);

  // Trigger alert generation engine
  const triggerRefresh = useCallback(async () => {
    setAlertsLoading(true);
    setError(null);
    try {
      await generateAlerts();
      await loadAlerts();
      await loadSummary();
    } catch (err: unknown) {
      console.error("Error generating alerts:", err);
      setError("Failed to generate new alerts from engine.");
    } finally {
      setAlertsLoading(false);
    }
  }, [loadAlerts, loadSummary]);

  // Update alert status
  const updateStatus = useCallback(
    async (id: number, newStatus: string, assignedUserId?: number | null) => {
      setActionLoading(true);
      try {
        const updatedAlert = await updateAlertStatus(id, newStatus, assignedUserId);
        
        // Optimistic UI state update
        setAlerts((prev) =>
          prev.map((a) => (a.id === id ? updatedAlert : a))
        );
        
        // Sync summary statistics
        await loadSummary();
      } catch (err: unknown) {
        console.error("Error updating alert status:", err);
        setError("Failed to update alert lifecycle status.");
      } finally {
        setActionLoading(false);
      }
    },
    [loadSummary]
  );

  // Load initial data
  useEffect(() => {
    loadAlerts();
    loadSummary();
  }, [loadAlerts, loadSummary]);

  useEffect(() => {
    const handleDatasetChange = () => {
      loadAlerts();
      loadSummary();
    };
    window.addEventListener("activeDatasetChanged", handleDatasetChange);
    return () => {
      window.removeEventListener("activeDatasetChanged", handleDatasetChange);
    };
  }, [loadAlerts, loadSummary]);

  return {
    alerts,
    summary,
    alertsLoading,
    summaryLoading,
    actionLoading,
    error,
    statusFilter,
    setStatusFilter,
    severityFilter,
    setSeverityFilter,
    sourceFilter,
    setSourceFilter,
    loadAlerts,
    loadSummary,
    triggerRefresh,
    updateStatus,
  };
}
