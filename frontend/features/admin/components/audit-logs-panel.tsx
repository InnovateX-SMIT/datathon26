"use client";

import React, { useState, useEffect, useCallback } from "react";
import { 
  FileText, Filter, ChevronLeft, ChevronRight, Search, 
  Download, ArrowUpDown, ShieldCheck, Activity, Key, Eye, AlertTriangle 
} from "lucide-react";
import { fetchAuditLogs } from "../services/admin-service";
import type { AuditLogResponse } from "../types/admin";

const ACTION_OPTIONS = [
  "ALL",
  "USER_CREATED",
  "USER_UPDATED",
  "USER_DEACTIVATED",
  "USER_ACTIVATED",
  "FAILED_LOGIN_ATTEMPT",
  "LOGIN_SUCCESS",
  "LOGOUT",
  "PASSWORD_CHANGED",
  "PROFILE_UPDATED",
  "FIR_VIEWED",
  "FIR_EXPORTED",
  "DATASET_UPLOADED",
  "DATASET_IMPORTED",
  "DATASET_ACTIVATED",
  "DATASET_DEACTIVATED",
  "DATASET_DELETED",
  "PREDICTION_REPEAT_OFFENDER",
  "PREDICTION_CRIME_RISK",
  "PREDICTION_CRIME_TYPE",
  "PREDICTION_EMERGING_HOTSPOT",
  "REPORT_GENERATED",
  "REPORT_DOWNLOADED",
  "REPORT_SHARED",
  "SYSTEM_HEALTH_CHECKED",
  "AUDIT_LOGS_VIEWED"
];

const MODULE_OPTIONS = [
  "ALL",
  "user",
  "dataset",
  "fir",
  "prediction",
  "report",
  "system"
];

const ACTION_BADGE_COLORS: Record<string, string> = {
  USER_CREATED: "text-green-400 bg-green-500/10 border-green-500/20",
  USER_DEACTIVATED: "text-red-400 bg-red-500/10 border-red-500/20",
  USER_ACTIVATED: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
  USER_UPDATED: "text-blue-400 bg-blue-500/10 border-blue-500/20",
  LOGIN_SUCCESS: "text-teal-400 bg-teal-500/10 border-teal-500/20",
  FAILED_LOGIN_ATTEMPT: "text-orange-400 bg-orange-500/10 border-orange-500/20",
  LOGOUT: "text-slate-400 bg-slate-500/10 border-slate-500/20",
  PASSWORD_CHANGED: "text-yellow-400 bg-yellow-500/10 border-yellow-500/20",
  PROFILE_UPDATED: "text-purple-400 bg-purple-500/10 border-purple-500/20",
  FIR_VIEWED: "text-cyan-400 bg-cyan-500/10 border-cyan-500/20",
  FIR_EXPORTED: "text-indigo-400 bg-indigo-500/10 border-indigo-500/20",
  DATASET_IMPORTED: "text-rose-400 bg-rose-500/10 border-rose-500/20",
  DATASET_ACTIVATED: "text-pink-400 bg-pink-500/10 border-pink-500/20",
  DATASET_DEACTIVATED: "text-amber-400 bg-amber-500/10 border-amber-500/20",
  PREDICTION_REPEAT_OFFENDER: "text-violet-400 bg-violet-500/10 border-violet-500/20",
  PREDICTION_CRIME_RISK: "text-fuchsia-400 bg-fuchsia-500/10 border-fuchsia-500/20",
  PREDICTION_CRIME_TYPE: "text-purple-400 bg-purple-500/10 border-purple-500/20",
  PREDICTION_EMERGING_HOTSPOT: "text-orange-400 bg-orange-500/10 border-orange-500/20",
  REPORT_GENERATED: "text-sky-400 bg-sky-500/10 border-sky-500/20",
  REPORT_DOWNLOADED: "text-lime-400 bg-lime-500/10 border-lime-500/20",
  REPORT_SHARED: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
  SYSTEM_HEALTH_CHECKED: "text-slate-400 bg-slate-500/10 border-slate-500/20",
  AUDIT_LOGS_VIEWED: "text-violet-400 bg-violet-500/10 border-violet-500/20",
};

function formatTimestamp(iso: string) {
  const d = new Date(iso);
  return d.toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit"
  });
}

export default function AuditLogsPanel() {
  const [logs, setLogs] = useState<AuditLogResponse[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);

  // Filter and Sorting states
  const [action, setAction] = useState("ALL");
  const [moduleFilter, setModuleFilter] = useState("ALL");
  const [search, setSearch] = useState("");
  const [userFilter, setUserFilter] = useState<string>("ALL");
  const [startDate, setStartDate] = useState("");
  const [endDate] = useState("");
  const [sortBy, setSortBy] = useState("created_at");
  const [sortOrder, setSortOrder] = useState("desc");
  const [expandedLogId, setExpandedLogId] = useState<number | null>(null);

  // Load audit logs from backend APIs
  const loadLogs = useCallback(async () => {
    setLoading(true);
    try {
      const uId = userFilter !== "ALL" ? parseInt(userFilter, 10) : undefined;
      const data = await fetchAuditLogs(
        page,
        50,
        action !== "ALL" ? action : undefined,
        search || undefined,
        uId,
        moduleFilter !== "ALL" ? moduleFilter : undefined,
        startDate || undefined,
        endDate || undefined,
        sortBy,
        sortOrder
      );
      setLogs(data.logs);
      setTotal(data.total);
    } catch (err) {
      console.error("Failed to load audit logs", err);
    } finally {
      setLoading(false);
    }
  }, [page, action, search, userFilter, moduleFilter, startDate, endDate, sortBy, sortOrder]);

  useEffect(() => {
    loadLogs();
  }, [loadLogs]);

  const handleExport = (format: "csv" | "excel" | "pdf") => {
    const params = new URLSearchParams();
    params.append("export_format", format);
    if (action !== "ALL") params.append("action", action);
    if (search) params.append("search", search);
    if (userFilter !== "ALL") params.append("user_id", userFilter);
    if (moduleFilter !== "ALL") params.append("module", moduleFilter);
    if (startDate) params.append("start_date", startDate);
    if (endDate) params.append("end_date", endDate);
    if (sortBy) params.append("sort_by", sortBy);
    if (sortOrder) params.append("sort_order", sortOrder);

    const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    window.open(`${apiBase}/api/v1/admin/audit-logs/export?${params.toString()}`, "_blank");
  };

  const toggleSort = (field: string) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === "desc" ? "asc" : "desc");
    } else {
      setSortBy(field);
      setSortOrder("desc");
    }
    setPage(1);
  };

  const totalPages = Math.ceil(total / 50) || 1;

  // Calculate Metrics from loaded logs
  const securityCount = logs.filter(l => ["LOGIN_SUCCESS", "FAILED_LOGIN_ATTEMPT", "PASSWORD_CHANGED", "PROFILE_UPDATED"].includes(l.action)).length;
  const predictionCount = logs.filter(l => l.action.startsWith("PREDICTION_")).length;
  const viewCount = logs.filter(l => l.action.endsWith("_VIEWED")).length;

  return (
    <div className="space-y-6">
      {/* ── KPI Summary Cards ────────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-4 bg-slate-950/40 border border-slate-900/60 rounded-2xl flex items-center justify-between">
          <div>
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block">Total Audits</span>
            <span className="text-xl font-black text-slate-100">{total.toLocaleString()}</span>
          </div>
          <div className="p-2 bg-violet-500/10 border border-violet-500/20 rounded-xl">
            <Activity className="w-5 h-5 text-violet-400" />
          </div>
        </div>
        <div className="p-4 bg-slate-950/40 border border-slate-900/60 rounded-2xl flex items-center justify-between">
          <div>
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block">Security logs</span>
            <span className="text-xl font-black text-slate-100">{securityCount}</span>
          </div>
          <div className="p-2 bg-yellow-500/10 border border-yellow-500/20 rounded-xl">
            <Key className="w-5 h-5 text-yellow-400" />
          </div>
        </div>
        <div className="p-4 bg-slate-950/40 border border-slate-900/60 rounded-2xl flex items-center justify-between">
          <div>
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block">Prediction Calls</span>
            <span className="text-xl font-black text-slate-100">{predictionCount}</span>
          </div>
          <div className="p-2 bg-teal-500/10 border border-teal-500/20 rounded-xl">
            <ShieldCheck className="w-5 h-5 text-teal-400" />
          </div>
        </div>
        <div className="p-4 bg-slate-950/40 border border-slate-900/60 rounded-2xl flex items-center justify-between">
          <div>
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block">Dossier Views</span>
            <span className="text-xl font-black text-slate-100">{viewCount}</span>
          </div>
          <div className="p-2 bg-cyan-500/10 border border-cyan-500/20 rounded-xl">
            <Eye className="w-5 h-5 text-cyan-400" />
          </div>
        </div>
      </div>

      {/* ── Search & Filter Controls ─────────────────────────────────────────── */}
      <div className="p-5 bg-slate-950/40 border border-slate-900/60 rounded-3xl space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          {/* Search bar */}
          <div className="relative">
            <Search className="absolute left-3 top-2.5 w-4 h-4 text-slate-500" />
            <input
              type="text"
              placeholder="Search logs details, IP, URL..."
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1); }}
              className="w-full bg-slate-900 border border-slate-800 text-slate-200 text-xs rounded-xl pl-9 pr-3 py-2.5 focus:outline-none focus:border-violet-500/50"
            />
          </div>

          {/* Module Filter */}
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-slate-500 shrink-0" />
            <select
              value={moduleFilter}
              onChange={(e) => { setModuleFilter(e.target.value); setPage(1); }}
              className="w-full bg-slate-900 border border-slate-800 text-slate-200 text-xs rounded-xl px-3 py-2.5 focus:outline-none focus:border-violet-500/50 cursor-pointer"
            >
              {MODULE_OPTIONS.map(mod => (
                <option key={mod} value={mod}>Module: {mod.toUpperCase()}</option>
              ))}
            </select>
          </div>

          {/* Action Filter */}
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-slate-500 shrink-0" />
            <select
              value={action}
              onChange={(e) => { setAction(e.target.value); setPage(1); }}
              className="w-full bg-slate-900 border border-slate-800 text-slate-200 text-xs rounded-xl px-3 py-2.5 focus:outline-none focus:border-violet-500/50 cursor-pointer"
            >
              {ACTION_OPTIONS.map(opt => (
                <option key={opt} value={opt}>{opt.replace(/_/g, " ")}</option>
              ))}
            </select>
          </div>

          {/* User Filter */}
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-slate-500 shrink-0" />
            <select
              value={userFilter}
              onChange={(e) => { setUserFilter(e.target.value); setPage(1); }}
              className="w-full bg-slate-900 border border-slate-800 text-slate-200 text-xs rounded-xl px-3 py-2.5 focus:outline-none focus:border-violet-500/50 cursor-pointer"
            >
              <option value="ALL">User: All users</option>
              <option value="0">User: System / Public Analyst (0)</option>
              <option value="1">User: Administrator (1)</option>
            </select>
          </div>
        </div>

        {/* Date Filter & Export Row */}
        <div className="flex items-center justify-between gap-3 flex-wrap border-t border-slate-900/60 pt-4">
          <div className="flex items-center gap-3">
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Start Date:</span>
            <input
              type="date"
              value={startDate}
              onChange={(e) => { setStartDate(e.target.value); setPage(1); }}
              className="bg-slate-900 border border-slate-800 text-slate-200 text-xs rounded-xl px-3 py-2 focus:outline-none focus:border-violet-500/50"
            />
          </div>

          {/* Export Actions */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => handleExport("csv")}
              className="flex items-center gap-1.5 px-3 py-2 bg-slate-900 border border-slate-800 hover:bg-slate-800/80 text-slate-300 font-black text-[10px] uppercase tracking-wider rounded-xl transition-all cursor-pointer"
            >
              <Download className="w-3.5 h-3.5" />
              CSV
            </button>
            <button
              onClick={() => handleExport("excel")}
              className="flex items-center gap-1.5 px-3 py-2 bg-slate-900 border border-slate-800 hover:bg-slate-800/80 text-slate-300 font-black text-[10px] uppercase tracking-wider rounded-xl transition-all cursor-pointer"
            >
              <Download className="w-3.5 h-3.5" />
              Excel
            </button>
            <button
              onClick={() => handleExport("pdf")}
              className="flex items-center gap-1.5 px-3 py-2 bg-slate-900 border border-slate-800 hover:bg-slate-800/80 text-slate-300 font-black text-[10px] uppercase tracking-wider rounded-xl transition-all cursor-pointer"
            >
              <Download className="w-3.5 h-3.5" />
              PDF
            </button>
          </div>
        </div>
      </div>

      {/* ── Table view ───────────────────────────────────────────────────────── */}
      <div className="bg-slate-950/40 border border-slate-900/60 rounded-2xl overflow-hidden backdrop-blur-md">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-900/80 bg-slate-900/20">
                <th 
                  onClick={() => toggleSort("id")}
                  className="px-4 py-3 text-left text-[9px] font-bold text-slate-400 uppercase tracking-wider cursor-pointer hover:bg-slate-800/20"
                >
                  <span className="flex items-center gap-1">ID <ArrowUpDown className="w-3 h-3 text-slate-500" /></span>
                </th>
                <th className="px-4 py-3 text-left text-[9px] font-bold text-slate-400 uppercase tracking-wider">Action</th>
                <th className="px-4 py-3 text-left text-[9px] font-bold text-slate-400 uppercase tracking-wider">Module</th>
                <th className="px-4 py-3 text-left text-[9px] font-bold text-slate-400 uppercase tracking-wider">Operator</th>
                <th className="px-4 py-3 text-left text-[9px] font-bold text-slate-400 uppercase tracking-wider">Client IP</th>
                <th className="px-4 py-3 text-left text-[9px] font-bold text-slate-400 uppercase tracking-wider">Details</th>
                <th 
                  onClick={() => toggleSort("created_at")}
                  className="px-4 py-3 text-left text-[9px] font-bold text-slate-400 uppercase tracking-wider cursor-pointer hover:bg-slate-800/20"
                >
                  <span className="flex items-center gap-1">Timestamp <ArrowUpDown className="w-3 h-3 text-slate-500" /></span>
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-900/40">
              {loading ? (
                [...Array(6)].map((_, i) => (
                  <tr key={i} className="animate-pulse">
                    {[...Array(7)].map((_, td) => (
                      <td key={td} className="px-4 py-3.5"><div className="h-3 bg-slate-800 rounded w-16" /></td>
                    ))}
                  </tr>
                ))
              ) : logs.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center py-12 text-slate-500 text-xs uppercase tracking-widest">
                    No matching audit records found
                  </td>
                </tr>
              ) : (
                logs.map((log) => {
                  const isExpanded = expandedLogId === log.id;
                  return (
                    <React.Fragment key={log.id}>
                      <tr 
                        onClick={() => setExpandedLogId(isExpanded ? null : log.id)}
                        className="hover:bg-slate-900/30 transition-colors cursor-pointer"
                      >
                        <td className="px-4 py-3 font-mono text-xs text-slate-500">#{log.id}</td>
                        <td className="px-4 py-3">
                          <span className={`inline-flex items-center px-2 py-0.5 text-[9px] font-bold uppercase tracking-wider border rounded-lg ${ACTION_BADGE_COLORS[log.action] ?? "text-slate-400 bg-slate-500/10 border-slate-500/20"}`}>
                            {log.action}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-xs text-slate-400 capitalize">{log.module || log.entity_type || "system"}</td>
                        <td className="px-4 py-3 text-xs text-slate-400">
                          <div className="font-semibold text-slate-200">{log.user_name || "System"}</div>
                          <div className="text-[10px] text-slate-500 font-bold uppercase">{log.user_role || "INTERNAL"}</div>
                        </td>
                        <td className="px-4 py-3 font-mono text-xs text-slate-500">{log.ip_address || "127.0.0.1"}</td>
                        <td className="px-4 py-3 text-xs text-slate-500 max-w-[240px] truncate" title={log.details || ""}>
                          {log.details || "—"}
                        </td>
                        <td className="px-4 py-3 text-xs text-slate-500 whitespace-nowrap">
                          {formatTimestamp(log.created_at)}
                        </td>
                      </tr>
                      {/* Expandable row showing HTTP/API details and state values */}
                      {isExpanded && (
                        <tr className="bg-slate-950/60">
                          <td colSpan={7} className="px-6 py-4 border-l-2 border-violet-500/40 space-y-3">
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
                              <div>
                                <span className="font-bold text-slate-400 uppercase text-[9px] block mb-1">API Endpoint</span>
                                <span className="font-mono text-slate-300 bg-slate-900 px-2 py-1 rounded-md block border border-slate-800/40">
                                  <span className="text-violet-400 font-bold mr-2">{log.request_method || "GET"}</span>
                                  {log.api_endpoint || "N/A"}
                                </span>
                              </div>
                              <div>
                                <span className="font-bold text-slate-400 uppercase text-[9px] block mb-1">Response status</span>
                                <span className={`font-mono px-2.5 py-1 rounded-md inline-block border ${log.response_status && log.response_status >= 400 ? "text-red-400 bg-red-500/10 border-red-500/20" : "text-emerald-400 bg-emerald-500/10 border-emerald-500/20"}`}>
                                  {log.response_status || 200}
                                </span>
                              </div>
                              <div>
                                <span className="font-bold text-slate-400 uppercase text-[9px] block mb-1">User Agent</span>
                                <span className="font-mono text-[10px] text-slate-500 truncate block" title={log.user_agent || "None"}>
                                  {log.user_agent || "None"}
                                </span>
                              </div>
                            </div>

                            {/* Masked details / state diffs */}
                            {log.details && log.details.startsWith("{") && (
                              <div className="p-3.5 bg-slate-900/60 border border-slate-900 rounded-xl">
                                <span className="font-bold text-slate-400 uppercase text-[9px] block mb-2">Payload State metadata</span>
                                <pre className="text-[10px] text-slate-400 font-mono overflow-x-auto">
                                  {JSON.stringify(JSON.parse(log.details), null, 2)}
                                </pre>
                              </div>
                            )}
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* ── Pagination controls ──────────────────────────────────────────────── */}
      <div className="flex items-center justify-between text-xs text-slate-500">
        <span>
          Page <span className="font-bold text-slate-300">{page}</span> of{" "}
          <span className="font-bold text-slate-300">{totalPages}</span> ({total} items)
        </span>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setPage(p => Math.max(p - 1, 1))}
            disabled={page <= 1 || loading}
            className="flex items-center gap-1 px-3 py-1.5 bg-slate-900 border border-slate-800 text-slate-400 rounded-xl hover:bg-slate-800 transition-all cursor-pointer disabled:opacity-40"
          >
            <ChevronLeft className="w-3.5 h-3.5" />
            Previous
          </button>
          <button
            onClick={() => setPage(p => Math.min(p + 1, totalPages))}
            disabled={page >= totalPages || loading}
            className="flex items-center gap-1 px-3 py-1.5 bg-slate-900 border border-slate-800 text-slate-400 rounded-xl hover:bg-slate-800 transition-all cursor-pointer disabled:opacity-40"
          >
            Next
            <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
}
