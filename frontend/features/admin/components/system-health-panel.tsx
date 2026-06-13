"use client";

import React from "react";
import {
  Activity,
  Database,
  Server,
  Cpu,
  RefreshCw,
  CheckCircle2,
  XCircle,
  Package,
} from "lucide-react";
import type { SystemHealth, ModelStatusResponse } from "@/features/admin/types/admin";

interface SystemHealthPanelProps {
  health: SystemHealth | null;
  modelStatus: ModelStatusResponse | null;
  healthLoading: boolean;
  modelsLoading: boolean;
  onRefreshHealth: () => void;
  onRefreshModels: () => void;
}

function SkeletonCard() {
  return (
    <div className="bg-slate-950/40 border border-slate-900/80 rounded-2xl p-5 backdrop-blur-md space-y-3 animate-pulse">
      <div className="h-3 bg-slate-800 rounded w-24" />
      <div className="h-6 bg-slate-800 rounded w-16" />
      <div className="h-3 bg-slate-800 rounded w-32" />
    </div>
  );
}

function SkeletonRow() {
  return (
    <tr>
      <td className="px-4 py-3"><div className="h-3 bg-slate-800 rounded w-32 animate-pulse" /></td>
      <td className="px-4 py-3"><div className="h-3 bg-slate-800 rounded w-16 animate-pulse" /></td>
    </tr>
  );
}

export default function SystemHealthPanel({
  health,
  modelStatus,
  healthLoading,
  modelsLoading,
  onRefreshHealth,
  onRefreshModels,
}: SystemHealthPanelProps) {
  const dbHealthy = health?.database?.status === "healthy";

  // Sort tables: crime_events first, then alphabetical
  const sortedTables = health?.tables
    ? Object.entries(health.tables).sort(([a], [b]) => {
        if (a === "crime_events") return -1;
        if (b === "crime_events") return 1;
        return a.localeCompare(b);
      })
    : [];

  return (
    <div className="space-y-8">

      {/* ── Section 1: Status Cards ──────────────────────────────────────── */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-black text-slate-300 uppercase tracking-widest flex items-center gap-2">
            <Activity className="w-4 h-4 text-emerald-400" />
            System Status
          </h3>
          <button
            onClick={onRefreshHealth}
            disabled={healthLoading}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold text-emerald-400 bg-emerald-500/10 hover:bg-emerald-500/15 border border-emerald-500/20 rounded-xl transition-all cursor-pointer disabled:opacity-50"
          >
            <RefreshCw className={`w-3 h-3 ${healthLoading ? "animate-spin" : ""}`} />
            Refresh
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {healthLoading ? (
            [...Array(4)].map((_, i) => <SkeletonCard key={i} />)
          ) : (
            <>
              {/* Database Status */}
              <div className="bg-slate-950/40 border border-slate-900/80 rounded-2xl p-5 backdrop-blur-md">
                <div className="flex items-center gap-2 mb-2">
                  <Database className="w-4 h-4 text-slate-400" />
                  <span className="text-[9px] font-bold text-slate-500 uppercase tracking-wider">Database</span>
                </div>
                <div className="flex items-center gap-2">
                  {dbHealthy ? (
                    <CheckCircle2 className="w-5 h-5 text-green-400" />
                  ) : (
                    <XCircle className="w-5 h-5 text-red-400" />
                  )}
                  <span className={`text-lg font-black uppercase ${dbHealthy ? "text-green-400" : "text-red-400"}`}>
                    {health?.database?.status ?? "—"}
                  </span>
                </div>
                <p className="text-[10px] text-slate-600 mt-1 font-mono">
                  {health?.database?.dialect ?? "—"}
                </p>
                <p className="text-[9px] text-slate-700 mt-0.5 font-mono truncate">
                  {health?.database?.url_masked ?? "—"}
                </p>
              </div>

              {/* API Status */}
              <div className="bg-slate-950/40 border border-slate-900/80 rounded-2xl p-5 backdrop-blur-md">
                <div className="flex items-center gap-2 mb-2">
                  <Activity className="w-4 h-4 text-slate-400" />
                  <span className="text-[9px] font-bold text-slate-500 uppercase tracking-wider">API</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-5 h-5 text-green-400" />
                  <span className="text-lg font-black text-green-400 uppercase">
                    {health?.api?.status ?? "—"}
                  </span>
                </div>
                <p className="text-[10px] text-slate-600 mt-1">
                  v{health?.api?.version ?? "—"}
                </p>
              </div>

              {/* Environment */}
              <div className="bg-slate-950/40 border border-slate-900/80 rounded-2xl p-5 backdrop-blur-md">
                <div className="flex items-center gap-2 mb-2">
                  <Server className="w-4 h-4 text-slate-400" />
                  <span className="text-[9px] font-bold text-slate-500 uppercase tracking-wider">Environment</span>
                </div>
                <span className="text-lg font-black text-amber-400 uppercase">
                  {health?.api?.environment ?? "—"}
                </span>
              </div>

              {/* Server */}
              <div className="bg-slate-950/40 border border-slate-900/80 rounded-2xl p-5 backdrop-blur-md">
                <div className="flex items-center gap-2 mb-2">
                  <Cpu className="w-4 h-4 text-slate-400" />
                  <span className="text-[9px] font-bold text-slate-500 uppercase tracking-wider">Server</span>
                </div>
                <p className="text-xs font-mono text-slate-300 mt-1">
                  Python {health?.server?.python_version ?? "—"}
                </p>
                <p className="text-xs font-mono text-slate-500 mt-0.5">
                  FastAPI {health?.server?.fastapi_version ?? "—"}
                </p>
              </div>
            </>
          )}
        </div>
      </div>

      {/* ── Section 2: Table Record Counts ──────────────────────────────── */}
      <div>
        <h3 className="text-sm font-black text-slate-300 uppercase tracking-widest flex items-center gap-2 mb-4">
          <Database className="w-4 h-4 text-blue-400" />
          Table Record Counts
        </h3>

        <div className="bg-slate-950/40 border border-slate-900/80 rounded-2xl overflow-hidden backdrop-blur-md">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-900">
                <th className="px-4 py-3 text-left text-[9px] font-bold text-slate-500 uppercase tracking-wider">
                  Table Name
                </th>
                <th className="px-4 py-3 text-right text-[9px] font-bold text-slate-500 uppercase tracking-wider">
                  Record Count
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-900/60">
              {healthLoading ? (
                [...Array(6)].map((_, i) => <SkeletonRow key={i} />)
              ) : sortedTables.length === 0 ? (
                <tr>
                  <td colSpan={2} className="text-center py-8 text-slate-600 text-xs">
                    No data available
                  </td>
                </tr>
              ) : (
                sortedTables.map(([tableName, count]) => (
                  <tr key={tableName} className="hover:bg-slate-900/30 transition-colors">
                    <td className="px-4 py-2.5 font-mono text-xs text-slate-300">
                      {tableName}
                    </td>
                    <td className="px-4 py-2.5 text-right font-mono text-xs font-bold text-blue-400">
                      {count.toLocaleString()}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* ── Section 3: ML Model Status ───────────────────────────────────── */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-black text-slate-300 uppercase tracking-widest flex items-center gap-2">
            <Package className="w-4 h-4 text-indigo-400" />
            ML Model Status
          </h3>
          <button
            onClick={onRefreshModels}
            disabled={modelsLoading}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold text-indigo-400 bg-indigo-500/10 hover:bg-indigo-500/15 border border-indigo-500/20 rounded-xl transition-all cursor-pointer disabled:opacity-50"
          >
            <RefreshCw className={`w-3 h-3 ${modelsLoading ? "animate-spin" : ""}`} />
            Refresh
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {modelsLoading ? (
            [...Array(4)].map((_, i) => <SkeletonCard key={i} />)
          ) : !modelStatus ? (
            <p className="text-slate-500 text-xs col-span-2 text-center py-8">
              Click Refresh to check model status.
            </p>
          ) : (
            modelStatus.models.map((model) => (
              <div
                key={model.path}
                className={`bg-slate-950/40 border rounded-2xl p-5 backdrop-blur-md ${
                  model.status === "loaded"
                    ? "border-green-500/20"
                    : "border-red-500/20"
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <p className="text-sm font-black text-slate-200">{model.name}</p>
                    <p className="text-[10px] font-mono text-slate-600">{model.path}</p>
                  </div>
                  <span
                    className={`inline-flex items-center px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider border rounded-lg ${
                      model.status === "loaded"
                        ? "text-green-400 bg-green-500/10 border-green-500/20"
                        : "text-red-400 bg-red-500/10 border-red-500/20"
                    }`}
                  >
                    {model.status}
                  </span>
                </div>
                {model.size_kb !== null && (
                  <p className="text-xs text-slate-500 mt-2 font-mono">
                    {model.size_kb.toLocaleString()} KB
                  </p>
                )}
              </div>
            ))
          )}
        </div>
        {modelStatus?.checked_at && (
          <p className="text-[10px] text-slate-700 mt-3">
            Last checked:{" "}
            {new Date(modelStatus.checked_at).toLocaleString("en-IN")}
          </p>
        )}
      </div>
    </div>
  );
}
