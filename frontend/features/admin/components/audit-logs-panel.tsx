"use client";

import React from "react";
import { FileText, Filter, ChevronLeft, ChevronRight } from "lucide-react";
import type { AuditLogListResponse } from "@/features/admin/types/admin";

interface AuditLogsPanelProps {
  auditLogs: AuditLogListResponse | null;
  loading: boolean;
  auditPage: number;
  auditPageSize: number;
  auditActionFilter: string;
  onPageChange: (page: number) => void;
  onActionFilterChange: (action: string) => void;
  onLoad: () => void;
}

const ACTION_OPTIONS = [
  "ALL",
  "USER_CREATED",
  "USER_UPDATED",
  "USER_DEACTIVATED",
  "USER_ACTIVATED",
  "SYSTEM_HEALTH_CHECKED",
  "DATASET_STATUS_VIEWED",
  "AUDIT_LOGS_VIEWED",
];

const ACTION_BADGE_COLORS: Record<string, string> = {
  USER_CREATED: "text-green-400 bg-green-500/10 border-green-500/20",
  USER_DEACTIVATED: "text-red-400 bg-red-500/10 border-red-500/20",
  USER_ACTIVATED: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
  USER_UPDATED: "text-blue-400 bg-blue-500/10 border-blue-500/20",
  SYSTEM_HEALTH_CHECKED: "text-slate-400 bg-slate-500/10 border-slate-500/20",
  DATASET_STATUS_VIEWED: "text-amber-400 bg-amber-500/10 border-amber-500/20",
  AUDIT_LOGS_VIEWED: "text-violet-400 bg-violet-500/10 border-violet-500/20",
};

function SkeletonRow() {
  return (
    <tr>
      {[...Array(6)].map((_, i) => (
        <td key={i} className="px-4 py-3">
          <div className="h-3 bg-slate-800 rounded animate-pulse w-20" />
        </td>
      ))}
    </tr>
  );
}

function formatTimestamp(iso: string) {
  const d = new Date(iso);
  return d.toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function truncate(str: string | null, max: number) {
  if (!str) return "—";
  return str.length > max ? str.slice(0, max) + "…" : str;
}

export default function AuditLogsPanel({
  auditLogs,
  loading,
  auditPage,
  auditPageSize,
  auditActionFilter,
  onPageChange,
  onActionFilterChange,
  onLoad,
}: AuditLogsPanelProps) {
  const total = auditLogs?.total ?? 0;
  const totalPages = Math.ceil(total / auditPageSize) || 1;
  const logs = auditLogs?.logs ?? [];

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="p-2 bg-amber-500/10 border border-amber-500/20 rounded-xl">
          <FileText className="w-4 h-4 text-amber-400" />
        </div>
        <div>
          <h2 className="text-lg font-black text-slate-100 uppercase tracking-tight">
            Audit Logs
          </h2>
          <p className="text-xs text-slate-500">
            {total.toLocaleString()} total log{total !== 1 ? "s" : ""}
          </p>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="flex items-center gap-3 flex-wrap">
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-slate-500" />
          <select
            value={auditActionFilter}
            onChange={(e) => onActionFilterChange(e.target.value)}
            className="bg-slate-900 border border-slate-800 text-slate-200 text-xs rounded-xl px-3 py-2 focus:outline-none focus:border-amber-500/50 cursor-pointer"
          >
            {ACTION_OPTIONS.map((opt) => (
              <option key={opt} value={opt}>
                {opt}
              </option>
            ))}
          </select>
        </div>
        <button
          onClick={onLoad}
          disabled={loading}
          className="px-4 py-2 bg-amber-500/10 hover:bg-amber-500/15 border border-amber-500/20 text-amber-400 font-bold text-xs uppercase tracking-wider rounded-xl transition-all cursor-pointer disabled:opacity-50"
        >
          Apply
        </button>
      </div>

      {/* Logs Table */}
      <div className="bg-slate-950/40 border border-slate-900/80 rounded-2xl overflow-hidden backdrop-blur-md">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-900">
                {["ID", "Action", "Entity Type", "Entity ID", "Details", "Timestamp"].map(
                  (h) => (
                    <th
                      key={h}
                      className="px-4 py-3 text-left text-[9px] font-bold text-slate-500 uppercase tracking-wider"
                    >
                      {h}
                    </th>
                  )
                )}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-900/60">
              {loading ? (
                [...Array(8)].map((_, i) => <SkeletonRow key={i} />)
              ) : logs.length === 0 ? (
                <tr>
                  <td
                    colSpan={6}
                    className="text-center py-12 text-slate-600 text-xs uppercase tracking-widest"
                  >
                    No audit logs found
                  </td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr
                    key={log.id}
                    className="hover:bg-slate-900/30 transition-colors"
                  >
                    <td className="px-4 py-2.5 font-mono text-xs text-slate-600">
                      #{log.id}
                    </td>
                    <td className="px-4 py-2.5">
                      <span
                        className={`inline-flex items-center px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider border rounded-lg ${ACTION_BADGE_COLORS[log.action] ?? "text-slate-400 bg-slate-500/10 border-slate-500/20"}`}
                      >
                        {log.action}
                      </span>
                    </td>
                    <td className="px-4 py-2.5 text-xs text-slate-400">
                      {log.entity_type ?? "—"}
                    </td>
                    <td className="px-4 py-2.5 font-mono text-xs text-slate-500">
                      {log.entity_id ?? "—"}
                    </td>
                    <td
                      className="px-4 py-2.5 text-xs text-slate-500 max-w-[180px]"
                      title={log.details ?? ""}
                    >
                      {truncate(log.details, 60)}
                    </td>
                    <td className="px-4 py-2.5 text-xs text-slate-500 whitespace-nowrap">
                      {formatTimestamp(log.created_at)}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between text-xs text-slate-500">
        <span>
          Page <span className="font-bold text-slate-300">{auditPage}</span> of{" "}
          <span className="font-bold text-slate-300">{totalPages}</span>
        </span>
        <div className="flex items-center gap-2">
          <button
            onClick={() => onPageChange(auditPage - 1)}
            disabled={auditPage <= 1 || loading}
            className="flex items-center gap-1 px-3 py-1.5 bg-slate-900 border border-slate-800 text-slate-400 rounded-xl hover:bg-slate-800 transition-all cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <ChevronLeft className="w-3 h-3" />
            Previous
          </button>
          <button
            onClick={() => onPageChange(auditPage + 1)}
            disabled={auditPage >= totalPages || loading}
            className="flex items-center gap-1 px-3 py-1.5 bg-slate-900 border border-slate-800 text-slate-400 rounded-xl hover:bg-slate-800 transition-all cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
          >
            Next
            <ChevronRight className="w-3 h-3" />
          </button>
        </div>
      </div>
    </div>
  );
}
