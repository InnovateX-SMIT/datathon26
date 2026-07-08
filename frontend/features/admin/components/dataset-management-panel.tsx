"use client";

import React from "react";
import { HardDrive, RefreshCw } from "lucide-react";
import type { DatasetStatusResponse } from "@/features/admin/types/admin";

interface DatasetManagementPanelProps {
  datasetStatus: DatasetStatusResponse | null;
  loading: boolean;
  onRefresh: () => void;
}

function SkeletonRow() {
  return (
    <tr>
      <td className="px-4 py-3"><div className="h-3 bg-slate-800 rounded w-32 animate-pulse" /></td>
      <td className="px-4 py-3"><div className="h-3 bg-slate-800 rounded w-16 animate-pulse" /></td>
      <td className="px-4 py-3"><div className="h-3 bg-slate-800 rounded w-full animate-pulse" /></td>
    </tr>
  );
}

export default function DatasetManagementPanel({
  datasetStatus,
  loading,
  onRefresh,
}: DatasetManagementPanelProps) {
  const tables = datasetStatus?.tables ?? [];
  const maxCount = Math.max(...tables.map((t) => t.record_count), 1);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-indigo-500/10 border border-indigo-500/20 rounded-xl">
            <HardDrive className="w-5 h-5 text-indigo-400" />
          </div>
          <div>
            <h2 className="text-lg font-black text-slate-100 uppercase tracking-tight">
              Dataset Overview
            </h2>
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => {
              import("@/features/admin/services/admin-service").then(s => {
                s.refreshModels().then(() => alert("Models refreshed")).catch(e => alert(e.response?.data?.detail || e.message));
              });
            }}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold text-amber-400 bg-amber-500/10 hover:bg-amber-500/15 border border-amber-500/20 rounded-xl transition-all cursor-pointer disabled:opacity-50"
          >
            Refresh Models
          </button>
          <button
            onClick={() => {
              if (confirm("Are you sure you want to securely re-seed the database? This will truncate crime and location data.")) {
                import("@/features/admin/services/admin-service").then(s => {
                  s.triggerReimport().then(() => {
                    alert("Database re-seeded successfully");
                    onRefresh();
                  }).catch(e => alert(e.response?.data?.detail || e.message));
                });
              }
            }}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold text-red-400 bg-red-500/10 hover:bg-red-500/15 border border-red-500/20 rounded-xl transition-all cursor-pointer disabled:opacity-50"
          >
            Re-Seed Database
          </button>
          <button
            onClick={() => {
              import("@/features/admin/services/admin-service").then(s => {
                s.optimizeIndexes().then(() => alert("Database indexes optimized successfully")).catch(e => alert(e.response?.data?.detail || e.message));
              });
            }}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold text-cyan-400 bg-cyan-500/10 hover:bg-cyan-500/15 border border-cyan-500/20 rounded-xl transition-all cursor-pointer disabled:opacity-50"
          >
            Optimize Indexes
          </button>
          <button
            onClick={() => {
              import("@/features/admin/services/admin-service").then(s => {
                s.backupDatabase().then(() => alert("Database backup created successfully")).catch(e => alert(e.response?.data?.detail || e.message));
              });
            }}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold text-emerald-400 bg-emerald-500/10 hover:bg-emerald-500/15 border border-emerald-500/20 rounded-xl transition-all cursor-pointer disabled:opacity-50"
          >
            Backup Database
          </button>
          <button
            onClick={onRefresh}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold text-indigo-400 bg-indigo-500/10 hover:bg-indigo-500/15 border border-indigo-500/20 rounded-xl transition-all cursor-pointer disabled:opacity-50"
          >
            <RefreshCw className={`w-3 h-3 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* Total Records Summary */}
      <div className="bg-slate-950/40 border border-indigo-500/20 rounded-2xl p-6 backdrop-blur-md">
        <p className="text-[9px] font-bold text-slate-500 uppercase tracking-widest mb-1">
          Total Records
        </p>
        {loading ? (
          <div className="h-10 bg-slate-800 rounded w-32 animate-pulse" />
        ) : (
          <p className="text-5xl font-black text-indigo-400 font-mono">
            {(datasetStatus?.total_records ?? 0).toLocaleString()}
          </p>
        )}
      </div>

      {/* Table Breakdown */}
      <div className="bg-slate-950/40 border border-slate-900/80 rounded-2xl overflow-hidden backdrop-blur-md">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-900">
                <th className="px-4 py-3 text-left text-[9px] font-bold text-slate-500 uppercase tracking-wider w-1/4">
                  Table
                </th>
                <th className="px-4 py-3 text-right text-[9px] font-bold text-slate-500 uppercase tracking-wider w-1/6">
                  Record Count
                </th>
                <th className="px-4 py-3 text-left text-[9px] font-bold text-slate-500 uppercase tracking-wider">
                  Distribution
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-900/60">
              {loading ? (
                [...Array(8)].map((_, i) => <SkeletonRow key={i} />)
              ) : tables.length === 0 ? (
                <tr>
                  <td
                    colSpan={3}
                    className="text-center py-12 text-slate-600 text-xs uppercase tracking-widest"
                  >
                    No data — click Refresh
                  </td>
                </tr>
              ) : (
                tables.map((row) => {
                  const pct =
                    maxCount > 0
                      ? Math.round((row.record_count / maxCount) * 100)
                      : 0;
                  return (
                    <tr
                      key={row.table}
                      className="hover:bg-slate-900/30 transition-colors"
                    >
                      <td className="px-4 py-2.5 font-mono text-xs text-slate-300">
                        {row.table}
                      </td>
                      <td className="px-4 py-2.5 text-right font-mono text-xs font-bold text-indigo-400">
                        {row.record_count.toLocaleString()}
                      </td>
                      <td className="px-4 py-2.5 pr-6">
                        <div className="w-full bg-slate-900 rounded-full h-2">
                          <div
                            className="bg-indigo-500/70 h-2 rounded-full transition-all duration-500"
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Last checked */}
      {datasetStatus?.checked_at && (
        <p className="text-[10px] text-slate-700 font-mono">
          Last checked:{" "}
          {new Date(datasetStatus.checked_at).toLocaleString("en-IN")}
        </p>
      )}
    </div>
  );
}
