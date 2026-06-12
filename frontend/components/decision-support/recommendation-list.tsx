import React from "react";
import {
  Compass,
  CheckCircle2,
  XCircle,
  RefreshCw,
  AlertTriangle,
  AlertCircle,
  Info,
  Clock,
} from "lucide-react";
import type { Recommendation } from "@/types/recommendation";

interface RecommendationListProps {
  recommendations: Recommendation[];
  recsLoading: boolean;
  statusFilter: string;
  setStatusFilter: (val: string) => void;
  priorityFilter: string;
  setPriorityFilter: (val: string) => void;
  updateStatus: (id: number, status: "resolved" | "dismissed") => void;
  triggerRefresh: () => void;
}

export default function RecommendationList({
  recommendations,
  recsLoading,
  statusFilter,
  setStatusFilter,
  priorityFilter,
  setPriorityFilter,
  updateStatus,
  triggerRefresh,
}: RecommendationListProps) {
  return (
    <div className="space-y-6 animate-fade-in">
      {/* Filters Toolbar */}
      <div className="flex flex-col sm:flex-row gap-4 justify-between items-start sm:items-center bg-slate-950/40 border border-slate-900/80 rounded-2xl p-4 backdrop-blur-xl">
        <div className="flex flex-wrap items-center gap-3">
          {/* Status filter dropdown */}
          <div className="flex flex-col gap-1">
            <span className="text-[8px] font-bold text-slate-500 uppercase tracking-widest pl-1">Status</span>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-300 outline-none focus:border-indigo-500/40 cursor-pointer font-semibold"
            >
              <option value="">All Statuses</option>
              <option value="pending">Pending</option>
              <option value="resolved">Resolved</option>
              <option value="dismissed">Dismissed</option>
            </select>
          </div>

          {/* Priority filter dropdown */}
          <div className="flex flex-col gap-1">
            <span className="text-[8px] font-bold text-slate-500 uppercase tracking-widest pl-1">Priority</span>
            <select
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(e.target.value)}
              className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-300 outline-none focus:border-indigo-500/40 cursor-pointer font-semibold"
            >
              <option value="">All Priorities</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
        </div>

        <button
          onClick={triggerRefresh}
          disabled={recsLoading}
          className="w-full sm:w-auto px-4 py-2 bg-slate-900 hover:bg-slate-850 border border-slate-800 hover:border-slate-700 text-slate-300 hover:text-slate-100 rounded-lg text-xs font-bold uppercase tracking-wider flex items-center justify-center gap-2 transition-all disabled:opacity-50 cursor-pointer"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${recsLoading ? "animate-spin text-indigo-400" : ""}`} />
          Refresh Engine
        </button>
      </div>

      {/* Recommendations Cards List */}
      {recsLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((n) => (
            <div key={n} className="bg-slate-950/20 border border-slate-900/60 rounded-3xl h-[120px] animate-pulse" />
          ))}
        </div>
      ) : recommendations.length === 0 ? (
        <div className="bg-slate-950/20 border border-dashed border-slate-900 rounded-3xl p-12 text-center flex flex-col items-center justify-center min-h-[200px]">
          <div className="p-4 bg-slate-900/40 rounded-2xl border border-slate-850 mb-3 text-slate-500">
            <Compass className="w-6 h-6" />
          </div>
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">No suggestions found</h4>
          <p className="text-[11px] text-slate-600 mt-1.5">
            Try resetting your filters or click Refresh Engine to fetch fresh insights from backend services.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {recommendations.map((rec) => {
            // Check priority styles
            const priorityStyles =
              rec.priority === "high"
                ? { border: "border-l-4 border-l-red-500", badgeBg: "bg-red-500/10 border-red-500/20 text-red-400", icon: AlertCircle }
                : rec.priority === "medium"
                  ? { border: "border-l-4 border-l-yellow-500", badgeBg: "bg-yellow-500/10 border-yellow-500/20 text-yellow-400", icon: AlertTriangle }
                  : { border: "border-l-4 border-l-sky-500", badgeBg: "bg-sky-500/10 border-sky-500/20 text-sky-400", icon: Info };

            const PriorityIcon = priorityStyles.icon;

            return (
              <div
                key={rec.id}
                className={`bg-slate-950/40 border border-slate-900/80 rounded-2xl p-5 relative overflow-hidden flex flex-col md:flex-row md:items-center justify-between gap-5 transition-all hover:border-slate-800 ${priorityStyles.border}`}
              >
                {/* Info Block */}
                <div className="space-y-2.5 max-w-3xl">
                  <div className="flex flex-wrap items-center gap-2">
                    {/* Priority badge */}
                    <span className={`px-2 py-0.5 border text-[9px] font-bold rounded-md uppercase tracking-wider ${priorityStyles.badgeBg} flex items-center gap-1`}>
                      <PriorityIcon className="w-3 h-3" />
                      {rec.priority}
                    </span>
                    
                    {/* Status badge */}
                    <span
                      className={`px-2 py-0.5 border text-[9px] font-bold rounded-md uppercase tracking-wider ${
                        rec.status === "pending"
                          ? "bg-amber-500/10 border-amber-500/20 text-amber-400"
                          : rec.status === "resolved"
                            ? "bg-green-500/10 border-green-500/20 text-green-400"
                            : "bg-slate-800 border-slate-700 text-slate-500"
                      }`}
                    >
                      {rec.status}
                    </span>
                  </div>

                  {/* Recommendation Text */}
                  <h4 className="text-slate-200 font-extrabold text-sm md:text-md leading-snug">
                    {rec.recommendation_text}
                  </h4>

                  {/* Analytical Cause */}
                  <p className="text-slate-400 text-xs leading-relaxed font-medium">
                    <strong className="text-slate-500 font-bold uppercase tracking-wide text-[9px] block mb-0.5">Analytical Rationale:</strong>
                    {rec.reason || "Generated by the platform decision intelligence engine."}
                  </p>

                  {/* Timestamp */}
                  <div className="flex items-center gap-1.5 text-[10px] font-mono text-slate-600">
                    <Clock className="w-3 h-3" />
                    <span>Logged at {new Date(rec.created_at).toLocaleString()}</span>
                  </div>
                </div>

                {/* Actions Block */}
                {rec.status === "pending" && (
                  <div className="flex items-center gap-2.5 shrink-0">
                    <button
                      onClick={() => updateStatus(rec.id, "resolved")}
                      className="px-3.5 py-2.5 bg-green-500/10 hover:bg-green-500/20 border border-green-500/20 hover:border-green-500/40 text-green-400 hover:text-green-300 text-xs font-bold rounded-xl flex items-center gap-1.5 transition-all cursor-pointer"
                    >
                      <CheckCircle2 className="w-4 h-4" />
                      Resolve
                    </button>
                    <button
                      onClick={() => updateStatus(rec.id, "dismissed")}
                      className="px-3.5 py-2.5 bg-slate-900 hover:bg-slate-850 border border-slate-800 hover:border-slate-700 text-slate-400 hover:text-slate-200 text-xs font-bold rounded-xl flex items-center gap-1.5 transition-all cursor-pointer"
                    >
                      <XCircle className="w-4 h-4" />
                      Dismiss
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
