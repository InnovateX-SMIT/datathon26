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
} from "@/services/recommendation.service";

export function useDecisionSupport() {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [history, setHistory] = useState<ResourceAllocation[]>([]);
  const [solverResult, setSolverResult] = useState<BeatAllocation[] | null>(null);
  
  const [recsLoading, setRecsLoading] = useState(false);
  const [solverLoading, setSolverLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);
  
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

      // Compute simple metrics on the loaded set
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

  // Run solver
  const runSolver = useCallback(async (payload: AllocationPayload) => {
    setSolverLoading(true);
    setSolverError(null);
    setSolverResult(null);
    try {
      const response = await solveResourceAllocation(payload);
      if (response.status === "success" && response.solved_allocation) {
        setSolverResult(response.solved_allocation);
        // Reload history to show the latest run
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
      // Optimistic state update in list
      setRecommendations((prev) =>
        prev.map((r) => (r.id === id ? { ...r, status: newStatus } : r))
      );
      // Re-trigger load to sync calculations
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

  // Load initial data
  useEffect(() => {
    loadRecommendations();
    loadHistory();
  }, [loadRecommendations, loadHistory]);

  return {
    recommendations,
    history,
    solverResult,
    recsLoading,
    solverLoading,
    historyLoading,
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
    setSolverResult,
  };
}
