"use client";

import React from "react";
import { AlertCircle, RefreshCw } from "lucide-react";
import type { SystemStatus } from "@/types/dashboard";

interface SystemStatusBarProps {
  status: SystemStatus | null;
  loading?: boolean;
  error?: string;
  onRetry?: () => void;
}

export default function SystemStatusBar({
  status,
  loading = false,
  error,
  onRetry,
}: SystemStatusBarProps) {
  // Format ISO timestamp to readable string
  const formatDateTime = (isoString: string) => {
    if (!isoString || isoString === "N/A") return "N/A";
    try {
      const dateObj = new Date(isoString);
      return dateObj.toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      });
    } catch {
      return isoString;
    }
  };

  const renderHeader = () => (
    <div className="flex items-center gap-2 mb-4">
      <div className="w-1 h-5 bg-indigo-500 rounded" />
      <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">
        System Health Status
      </h3>
    </div>
  );

  if (loading) {
    return (
      <div className="glass-card p-5 rounded-xl border border-slate-800/60 w-full flex flex-col justify-center">
        {renderHeader()}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 w-full">
          {Array.from({ length: 4 }).map((_, idx) => (
            <div key={idx} className="h-8 bg-slate-800/50 rounded-lg animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass-card p-4 rounded-xl border border-slate-800/60 w-full flex items-center justify-between gap-4">
        <div className="flex items-center gap-2.5 text-red-500">
          <AlertCircle className="w-4 h-4 shrink-0 animate-pulse" />
          <span className="text-xs font-medium text-slate-300">
            {error || "Failed to load system status statistics."}
          </span>
        </div>
        {onRetry && (
          <button
            onClick={onRetry}
            className="flex items-center gap-1 text-[10px] uppercase font-bold text-indigo-400 hover:text-indigo-300 transition-colors cursor-pointer"
          >
            <RefreshCw className="w-3 h-3" />
            <span>Retry</span>
          </button>
        )}
      </div>
    );
  }

  if (!status) return null;

  return (
    <div className="glass-card p-5 rounded-xl border border-slate-800/60 w-full flex flex-col md:flex-row justify-between items-stretch md:items-center gap-4 divide-y md:divide-y-0 md:divide-x divide-slate-800/60">
      {/* DB Status */}
      <div className="flex-1 flex items-center gap-3 md:pb-0 pb-3">
        <div className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
        </div>
        <div>
          <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Database Link</p>
          <p className="text-xs font-extrabold text-green-400 tracking-tight">ONLINE</p>
        </div>
      </div>

      {/* Record Volume */}
      <div className="flex-1 flex flex-col justify-center md:pl-6 md:pb-0 py-3">
        <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Data Volume</p>
        <p className="text-xs font-extrabold text-slate-200 mt-0.5 tracking-tight">
          {status.total_records.toLocaleString()}{" "}
          <span className="text-[10px] text-slate-400 font-semibold tracking-wider uppercase ml-0.5">Records</span>
        </p>
      </div>

      {/* Last Seeding/Update */}
      <div className="flex-1 flex flex-col justify-center md:pl-6 md:pb-0 py-3">
        <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Freshness Index</p>
        <p className="text-xs font-bold text-slate-200 mt-0.5 tracking-tight truncate max-w-[200px]" title={formatDateTime(status.last_updated)}>
          {formatDateTime(status.last_updated)}
        </p>
      </div>

      {/* Temporal Coverage */}
      <div className="flex-1 flex flex-col justify-center md:pl-6 md:pt-0 pt-3">
        <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Historical Bounds</p>
        <p className="text-xs font-extrabold text-slate-200 mt-0.5 tracking-tight">
          {status.data_coverage_days}{" "}
          <span className="text-[10px] text-slate-400 font-semibold tracking-wider uppercase ml-0.5">days covered</span>
        </p>
      </div>
    </div>
  );
}
