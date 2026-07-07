import { useState, useEffect, useCallback } from "react";
import {
  Recommendation,
  BeatAllocation,
  AllocationPayload,
  ResourceAllocation,
  DecisionSupportMetrics,
} from "@/types/recommendation";
import {
  fetchRecommendations,
  updateRecommendationStatus,
  generateRecommendations,
  solveResourceAllocation,
  fetchResourceAllocationHistory,
  fetchRecommendationHistory,
  triggerPipelineSync,
  RecommendationHistoryItem,
} from "@/services/recommendation.service";

export function useDecisionSupport() {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [history, setHistory] = useState<ResourceAllocation[]>([]);
  const [syncHistory, setSyncHistory] = useState<RecommendationHistoryItem[]>([]);
  const [solverResult, setSolverResult] = useState<BeatAllocation[] | null>(null);
  
  const [recsLoading, setRecsLoading] = useState(false);
  const [solverLoading, setSolverLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [syncHistoryLoading, setSyncHistoryLoading] = useState(false);
  const [syncPipelineLoading, setSyncPipelineLoading] = useState(false);
  
  const [error, setError] = useState<string | null>(null);
  const [solverError, setSolverError] = useState<string | null>(null);

  const [statusFilter, setStatusFilter] = useState<string>("");
  const [priorityFilter, setPriorityFilter] = useState<string>("");

  const [metrics, setMetrics] = useState<DecisionSupportMetrics>({
    totalCount: 0,
    pendingCount: 0,
    resolvedCount: 0,
    dismissedCount: 0,
  });

  // Load recommendations
  const loadRecommendations = useCallback(async () => {
    setRecsLoading(true);
    setError(null);
    try {
      const data = await fetchRecommendations(
        statusFilter || undefined,
        priorityFilter || undefined
      );
      setRecommendations(data);

      const stats: DecisionSupportMetrics = {
        totalCount: data.length,
        pendingCount: data.filter((r) => r.status === "pending").length,
        resolvedCount: data.filter((r) => r.status === "resolved").length,
        dismissedCount: data.filter((r) => r.status === "dismissed").length,
      };
      setMetrics(stats);
    } catch (err: unknown) {
      console.error("Error loading recommendations:", err);
      setError("Failed to load recommendations from backend.");
    } finally {
      setRecsLoading(false);
    }
  }, [statusFilter, priorityFilter]);

  // Load history
  const loadHistory = useCallback(async () => {
    setHistoryLoading(true);
    try {
      const data = await fetchResourceAllocationHistory();
      setHistory(data);
    } catch (err: unknown) {
      console.error("Error loading history:", err);
    } finally {
      setHistoryLoading(false);
    }
  }, []);

  // Load Sync History
  const loadSyncHistory = useCallback(async () => {
    setSyncHistoryLoading(true);
    try {
      const data = await fetchRecommendationHistory();
      setSyncHistory(data);
    } catch (err: unknown) {
      console.error("Error loading sync history:", err);
    } finally {
      setSyncHistoryLoading(false);
    }
  }, []);

  // Run solver
  const runSolver = useCallback(async (payload: AllocationPayload) => {
    setSolverLoading(true);
    setSolverError(null);
    setSolverResult(null);
    try {
      const response = await solveResourceAllocation(payload);
      if (response.status === "success" && response.solved_allocation) {
        setSolverResult(response.solved_allocation);
        await loadHistory();
      } else {
        setSolverError("Solver returned failure status.");
      }
    } catch (err: unknown) {
      console.error("Error running solver:", err);
      setSolverError("Resource optimizer failed. Ensure SciPy or fallback solver runs properly.");
    } finally {
      setSolverLoading(false);
    }
  }, [loadHistory]);

  // Update recommendation status
  const updateStatus = useCallback(async (id: number, newStatus: "resolved" | "dismissed") => {
    try {
      await updateRecommendationStatus(id, newStatus);
      setRecommendations((prev) =>
        prev.map((r) => (r.id === id ? { ...r, status: newStatus } : r))
      );
      await loadRecommendations();
    } catch (err: unknown) {
      console.error("Error updating status:", err);
      setError("Failed to update status.");
    }
  }, [loadRecommendations]);

  // Trigger dynamic recommendation generation
  const triggerRefresh = useCallback(async () => {
    setRecsLoading(true);
    setError(null);
    try {
      const data = await generateRecommendations();
      setRecommendations(data);
      await loadRecommendations();
    } catch (err: unknown) {
      console.error("Error generating recommendations:", err);
      setError("Failed to refresh decision suggestions.");
    } finally {
      setRecsLoading(false);
    }
  }, [loadRecommendations]);

  // Trigger end-to-end synchronization pipeline
  const runPipelineSync = useCallback(async () => {
    setSyncPipelineLoading(true);
    setError(null);
    try {
      await triggerPipelineSync();
      // Reload everything
      await Promise.all([
        loadRecommendations(),
        loadSyncHistory(),
        loadHistory()
      ]);
    } catch (err: any) {
      console.error("Error synchronizing pipeline:", err);
      setError(err.response?.data?.detail || "Failed to trigger end-to-end intelligence synchronization.");
    } finally {
      setSyncPipelineLoading(false);
    }
  }, [loadRecommendations, loadSyncHistory, loadHistory]);

  // Load initial data
  useEffect(() => {
    loadRecommendations();
    loadHistory();
    loadSyncHistory();
  }, [loadRecommendations, loadHistory, loadSyncHistory]);

  return {
    recommendations,
    history,
    syncHistory,
    solverResult,
    recsLoading,
    solverLoading,
    historyLoading,
    syncHistoryLoading,
    syncPipelineLoading,
    error,
    solverError,
    statusFilter,
    setStatusFilter,
    priorityFilter,
    setPriorityFilter,
    metrics,
    runSolver,
    updateStatus,
    triggerRefresh,
    runPipelineSync,
    setSolverResult,
  };
}
