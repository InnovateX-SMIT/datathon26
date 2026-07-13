"use client";

import React, { useEffect, useState } from "react";
import { AlertCircle, RefreshCw, ChevronLeft, ChevronRight, Search, X } from "lucide-react";
import { useFirCases, type CaseFilters } from "../hooks/useFirCases";
import { useFirLookups } from "../hooks/useFirLookups";
import type { DistrictDTO } from "../types/fir";

const inputCls =
  "w-full bg-slate-900/60 border border-slate-700/60 text-slate-200 text-sm rounded-lg px-3 py-2 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/30 transition-colors placeholder:text-slate-600";
const selectCls = `${inputCls} appearance-none cursor-pointer`;

export default function FirCaseList() {
  const {
    cases,
    total,
    page,
    pageSize,
    loading,
    error,
    setPage,
    setFilters,
    filters,
    retry,
  } = useFirCases(15);

  const { lookups, loadDistricts } = useFirLookups();

  // Local filter state (applied on search)
  const [localDistrictId, setLocalDistrictId] = useState<string>("");
  const [localStatusId, setLocalStatusId] = useState<string>("");
  const [localStartDate, setLocalStartDate] = useState("");
  const [localEndDate, setLocalEndDate] = useState("");
  const [localSearchQuery, setLocalSearchQuery] = useState("");
  const [districts, setDistricts] = useState<DistrictDTO[]>([]);

  // Load districts for filter if a state exists
  useEffect(() => {
    if (lookups && lookups.states.length > 0) {
      // Load all districts (no state filter) for the filter bar
      loadDistricts(lookups.states[0]?.id).then(setDistricts).catch(() => {});
    }
  }, [lookups, loadDistricts]);

  const applyFilters = () => {
    const f: CaseFilters = {};
    if (localDistrictId) f.district_id = Number(localDistrictId);
    if (localStatusId) f.case_status_id = Number(localStatusId);
    if (localStartDate) f.start_date = localStartDate;
    if (localEndDate) f.end_date = localEndDate;
    if (localSearchQuery.trim()) f.q = localSearchQuery.trim();
    setFilters(f);
  };

  const clearFilters = () => {
    setLocalDistrictId("");
    setLocalStatusId("");
    setLocalStartDate("");
    setLocalEndDate("");
    setLocalSearchQuery("");
    setFilters({});
  };

  const hasActiveFilters =
    filters.district_id || filters.case_status_id || filters.start_date || filters.end_date || filters.q;

  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  const formatDate = (dateStr: string | null | undefined) => {
    if (!dateStr) return "—";
    try {
      return new Date(dateStr).toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric",
      });
    } catch {
      return dateStr;
    }
  };

  const getStatusBadge = (statusId: number) => {
    const status = lookups?.caseStatuses.find((s) => s.id === statusId);
    const label = status?.name || `Status ${statusId}`;
    // Use different colors based on common status patterns
    const lower = label.toLowerCase();
    if (lower.includes("closed") || lower.includes("convicted")) {
      return { label, className: "bg-green-500/20 text-green-400 border border-green-500/30" };
    }
    if (lower.includes("investigation") || lower.includes("pending")) {
      return { label, className: "bg-amber-500/20 text-amber-400 border border-amber-500/30" };
    }
    if (lower.includes("chargesheet") || lower.includes("filed")) {
      return { label, className: "bg-cyan-500/20 text-cyan-400 border border-cyan-500/30" };
    }
    return { label, className: "bg-indigo-500/20 text-indigo-400 border border-indigo-500/30" };
  };

  // ── Error State ─────────────────────────────────────────────────────────
  if (error && !loading) {
    return (
      <div className="glass-card p-8 rounded-2xl border border-slate-800/60 text-center space-y-4">
        <AlertCircle className="w-10 h-10 text-red-500 mx-auto animate-pulse" />
        <p className="text-sm text-slate-300">{error}</p>
        <button
          onClick={retry}
          className="flex items-center gap-2 mx-auto px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs uppercase tracking-wider rounded-xl transition-colors cursor-pointer"
        >
          <RefreshCw className="w-3.5 h-3.5" /> Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-5 animate-fade-in">
      {/* ── Filter Bar ─────────────────────────────────────────────────────── */}
      <div className="glass-card rounded-xl border border-slate-800/60 p-4 space-y-4">
        {/* Primary Search Input */}
        <div className="relative">
          <Search className="absolute left-3.5 top-3 w-4 h-4 text-slate-500" />
          <input
            type="text"
            placeholder="Search by FIR / Crime No or Case No (e.g. 200060009202600001)..."
            value={localSearchQuery}
            onChange={(e) => setLocalSearchQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && applyFilters()}
            className="w-full bg-slate-900/60 border border-slate-700/60 text-slate-200 text-sm rounded-lg pl-10 pr-3 py-2.5 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/30 transition-colors placeholder:text-slate-600 focus:outline-none"
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 items-end">
          <div>
            <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">
              District
            </label>
            <select
              className={selectCls}
              value={localDistrictId}
              onChange={(e) => setLocalDistrictId(e.target.value)}
            >
              <option value="">All Districts</option>
              {districts.map((d) => (
                <option key={d.id} value={d.id}>{d.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">
              Case Status
            </label>
            <select
              className={selectCls}
              value={localStatusId}
              onChange={(e) => setLocalStatusId(e.target.value)}
            >
              <option value="">All Statuses</option>
              {lookups?.caseStatuses.map((s) => (
                <option key={s.id} value={s.id}>{s.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">
              From Date
            </label>
            <input
              type="date"
              className={inputCls}
              value={localStartDate}
              onChange={(e) => setLocalStartDate(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">
              To Date
            </label>
            <input
              type="date"
              className={inputCls}
              value={localEndDate}
              onChange={(e) => setLocalEndDate(e.target.value)}
            />
          </div>
          <div className="flex items-end gap-2">
            <button
              onClick={applyFilters}
              className="flex-1 flex items-center justify-center gap-1.5 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs uppercase tracking-wider rounded-lg transition-colors cursor-pointer"
            >
              <Search className="w-3.5 h-3.5" /> Search
            </button>
            {hasActiveFilters && (
              <button
                onClick={clearFilters}
                className="p-2.5 text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 rounded-lg transition-colors cursor-pointer border border-slate-700/50"
                title="Clear filters"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
      </div>

      {/* ── Table ──────────────────────────────────────────────────────────── */}
      <div className="glass-card rounded-2xl border border-slate-800/60 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-900/60 border-b border-slate-800">
                <th className="px-4 py-3 text-xs font-bold text-slate-400 uppercase tracking-wider w-12">#</th>
                <th className="px-4 py-3 text-xs font-bold text-slate-400 uppercase tracking-wider">Crime No</th>
                <th className="px-4 py-3 text-xs font-bold text-slate-400 uppercase tracking-wider">Case No</th>
                <th className="px-4 py-3 text-xs font-bold text-slate-400 uppercase tracking-wider">Registered</th>
                <th className="px-4 py-3 text-xs font-bold text-slate-400 uppercase tracking-wider">Status</th>
                <th className="px-4 py-3 text-xs font-bold text-slate-400 uppercase tracking-wider w-24">Complainants</th>
                <th className="px-4 py-3 text-xs font-bold text-slate-400 uppercase tracking-wider w-24">Accused</th>
                <th className="px-4 py-3 text-xs font-bold text-slate-400 uppercase tracking-wider w-24">Victims</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/40">
              {loading ? (
                Array.from({ length: 8 }).map((_, idx) => (
                  <tr key={idx} className="border-b border-slate-800/40">
                    <td className="px-4 py-3.5"><div className="h-4 w-6 bg-slate-800/50 rounded animate-pulse" /></td>
                    <td className="px-4 py-3.5"><div className="h-4 w-36 bg-slate-800/50 rounded animate-pulse" /></td>
                    <td className="px-4 py-3.5"><div className="h-4 w-20 bg-slate-800/50 rounded animate-pulse" /></td>
                    <td className="px-4 py-3.5"><div className="h-4 w-24 bg-slate-800/50 rounded animate-pulse" /></td>
                    <td className="px-4 py-3.5"><div className="h-6 w-20 bg-slate-800/50 rounded-full animate-pulse" /></td>
                    <td className="px-4 py-3.5"><div className="h-4 w-8 bg-slate-800/50 rounded animate-pulse" /></td>
                    <td className="px-4 py-3.5"><div className="h-4 w-8 bg-slate-800/50 rounded animate-pulse" /></td>
                    <td className="px-4 py-3.5"><div className="h-4 w-8 bg-slate-800/50 rounded animate-pulse" /></td>
                  </tr>
                ))
              ) : cases.length === 0 ? (
                <tr>
                  <td colSpan={8}>
                    <div className="flex flex-col items-center justify-center py-16 text-center">
                      <div className="p-3 bg-slate-800/40 border border-slate-700/40 rounded-xl mb-4">
                        <Search className="w-8 h-8 text-slate-600" />
                      </div>
                      <p className="text-sm font-semibold text-slate-400">No FIR Cases Found</p>
                      <p className="text-xs text-slate-600 mt-1 max-w-[260px]">
                        {hasActiveFilters
                          ? "No cases match your current filters. Try adjusting or clearing them."
                          : "No cases registered yet. Create a new FIR case to get started."}
                      </p>
                    </div>
                  </td>
                </tr>
              ) : (
                cases.map((c, idx) => {
                  const statusBadge = getStatusBadge(c.CaseStatusID);
                  return (
                    <tr
                      key={c.id}
                      className="border-b border-slate-800/45 hover:bg-slate-800/30 even:bg-slate-900/10 transition-colors cursor-pointer"
                      onClick={() => (window.location.href = `/fir/cases/${c.id}`)}
                    >
                      <td className="px-4 py-3.5 text-xs text-slate-500 font-mono">
                        {(page - 1) * pageSize + idx + 1}
                      </td>
                      <td className="px-4 py-3.5 text-xs font-bold text-indigo-400 font-mono tracking-tight">
                        {c.CrimeNo || "—"}
                      </td>
                      <td className="px-4 py-3.5 text-xs text-slate-300 font-mono">
                        {c.CaseNo || "—"}
                      </td>
                      <td className="px-4 py-3.5 text-xs text-slate-400 font-mono">
                        {formatDate(c.CrimeRegisteredDate)}
                      </td>
                      <td className="px-4 py-3.5">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[9px] font-extrabold tracking-wider ${statusBadge.className}`}>
                          {statusBadge.label.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-4 py-3.5 text-xs text-slate-400 text-center font-bold">
                        {c.complainants.length}
                      </td>
                      <td className="px-4 py-3.5 text-xs text-slate-400 text-center font-bold">
                        {c.accused.length}
                      </td>
                      <td className="px-4 py-3.5 text-xs text-slate-400 text-center font-bold">
                        {c.victims.length}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* ── Pagination ─────────────────────────────────────────────────────── */}
        {total > 0 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-slate-800/50">
            <span className="text-[11px] text-slate-500 font-mono">
              Showing {(page - 1) * pageSize + 1}–{Math.min(page * pageSize, total)} of {total} cases
            </span>
            <div className="flex items-center gap-1.5">
              <button
                disabled={page <= 1}
                onClick={() => setPage(page - 1)}
                className="p-2 rounded-lg border border-slate-700/50 text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 disabled:opacity-30 disabled:cursor-not-allowed transition-colors cursor-pointer"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <span className="text-xs font-mono text-slate-400 px-2">
                {page} / {totalPages}
              </span>
              <button
                disabled={page >= totalPages}
                onClick={() => setPage(page + 1)}
                className="p-2 rounded-lg border border-slate-700/50 text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 disabled:opacity-30 disabled:cursor-not-allowed transition-colors cursor-pointer"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
