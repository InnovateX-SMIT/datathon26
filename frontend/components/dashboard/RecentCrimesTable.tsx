"use client";

import React from "react";
import { AlertCircle } from "lucide-react";
import type { RecentCrimeItem } from "@/types/dashboard";

interface RecentCrimesTableProps {
  data: RecentCrimeItem[];
  loading?: boolean;
  error?: string;
  onRetry?: () => void;
}

export default function RecentCrimesTable({
  data,
  loading = false,
  error,
  onRetry,
}: RecentCrimesTableProps) {
  // Format Date to Indian standard
  const formatDate = (dateStr: string) => {
    if (!dateStr) return "N/A";
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

  // Severity Badge styling selector
  const getSeverityBadge = (severity: number) => {
    if (severity >= 7) {
      return "bg-red-500/20 text-red-400 border border-red-500/30";
    } else if (severity >= 4) {
      return "bg-amber-500/20 text-amber-400 border border-amber-500/30";
    } else {
      return "bg-green-500/20 text-green-400 border border-green-500/30";
    }
  };

  // Status Badge styling selector and formatter
  const getStatusDetails = (status: string) => {
    const rawStatus = status.toLowerCase();
    const formattedLabel = status.replace(/_/g, " ").toUpperCase();
    
    if (rawStatus === "reported" || rawStatus === "pending trial" || rawStatus === "pending_trial") {
      return {
        label: formattedLabel,
        className: "bg-amber-500/20 text-amber-400 border border-amber-500/30",
      };
    } else if (rawStatus === "closed") {
      return {
        label: formattedLabel,
        className: "bg-green-500/20 text-green-400 border border-green-500/30",
      };
    } else if (rawStatus === "under investigation" || rawStatus === "under_investigation") {
      return {
        label: "UNDER INVESTIGATION",
        className: "bg-indigo-500/20 text-indigo-400 border border-indigo-500/30",
      };
    } else if (rawStatus === "chargesheet filed" || rawStatus === "chargesheet_filed") {
      return {
        label: "CHARGESHEET FILED",
        className: "bg-cyan-500/20 text-cyan-400 border border-cyan-500/30",
      };
    } else {
      return {
        label: formattedLabel,
        className: "bg-slate-500/20 text-slate-400 border border-slate-500/30",
      };
    }
  };

  const renderHeader = () => (
    <div className="flex items-center gap-2 mb-5">
      <div className="w-1 h-5 bg-indigo-500 rounded" />
      <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
        Recent Crime Events
      </h3>
    </div>
  );

  return (
    <div className="glass-card p-6 rounded-2xl border border-slate-800/60 flex flex-col w-full">
      {renderHeader()}
      
      {error ? (
        <div className="flex-1 flex flex-col items-center justify-center border border-dashed border-red-500/20 rounded-xl bg-red-500/5 p-8 text-center min-h-[250px]">
          <AlertCircle className="w-8 h-8 text-red-500 mb-3 animate-pulse" />
          <p className="text-xs text-slate-300 max-w-sm mb-4">
            {error || "Failed to load recent crimes. Please try again."}
          </p>
          {onRetry && (
            <button
              onClick={onRetry}
              className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs uppercase tracking-wider rounded-lg transition-colors cursor-pointer"
            >
              Retry
            </button>
          )}
        </div>
      ) : (
        <div className="overflow-x-auto w-full">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-900/60 border-b border-slate-800">
                <th className="px-4 py-3 text-left text-xs font-bold text-slate-400 uppercase tracking-wider w-12">#</th>
                <th className="px-4 py-3 text-left text-xs font-bold text-slate-400 uppercase tracking-wider">Crime Type</th>
                <th className="px-4 py-3 text-left text-xs font-bold text-slate-400 uppercase tracking-wider">Category</th>
                <th className="px-4 py-3 text-left text-xs font-bold text-slate-400 uppercase tracking-wider">District</th>
                <th className="px-4 py-3 text-left text-xs font-bold text-slate-400 uppercase tracking-wider w-24">Severity</th>
                <th className="px-4 py-3 text-left text-xs font-bold text-slate-400 uppercase tracking-wider">Status</th>
                <th className="px-4 py-3 text-left text-xs font-bold text-slate-400 uppercase tracking-wider">Date</th>
                <th className="px-4 py-3 text-left text-xs font-bold text-slate-400 uppercase tracking-wider w-20">Victims</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/40">
              {loading ? (
                // 10 skeleton rows
                Array.from({ length: 10 }).map((_, idx) => (
                  <tr key={idx} className="border-b border-slate-800/40">
                    <td className="px-4 py-3.5"><div className="h-4 w-6 bg-slate-800/50 rounded animate-pulse" /></td>
                    <td className="px-4 py-3.5"><div className="h-4 w-28 bg-slate-800/50 rounded animate-pulse" /></td>
                    <td className="px-4 py-3.5"><div className="h-4 w-24 bg-slate-800/50 rounded animate-pulse" /></td>
                    <td className="px-4 py-3.5"><div className="h-4 w-28 bg-slate-800/50 rounded animate-pulse" /></td>
                    <td className="px-4 py-3.5"><div className="h-6 w-12 bg-slate-800/50 rounded-full animate-pulse" /></td>
                    <td className="px-4 py-3.5"><div className="h-6 w-20 bg-slate-800/50 rounded-full animate-pulse" /></td>
                    <td className="px-4 py-3.5"><div className="h-4 w-20 bg-slate-800/50 rounded animate-pulse" /></td>
                    <td className="px-4 py-3.5"><div className="h-4 w-8 bg-slate-800/50 rounded animate-pulse" /></td>
                  </tr>
                ))
              ) : data.length === 0 ? (
                <tr>
                  <td colSpan={8}>
                    <div className="flex flex-col items-center justify-center py-14 text-center">
                      <div className="p-3 bg-slate-800/40 border border-slate-700/40 rounded-xl mb-4">
                        <svg className="w-8 h-8 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25zM6.75 12h.008v.008H6.75V12zm0 3h.008v.008H6.75V15zm0 3h.008v.008H6.75V18z" />
                        </svg>
                      </div>
                      <p className="text-sm font-semibold text-slate-400">No Crime Events Found</p>
                      <p className="text-xs text-slate-600 mt-1 max-w-[220px]">No recent crime data matches your current filters or the dataset is empty.</p>
                    </div>
                  </td>
                </tr>
              ) : (
                data.map((crime, index) => {
                  const statusDetails = getStatusDetails(crime.status);
                  return (
                    <tr
                      key={crime.id}
                      className="border-b border-slate-800/45 hover:bg-slate-800/30 even:bg-slate-900/10 transition-colors"
                    >
                      <td className="px-4 py-3.5 text-xs text-slate-500 font-mono">
                        {index + 1}
                      </td>
                      <td className="px-4 py-3.5 text-xs font-bold text-slate-100 uppercase tracking-tight">
                        {crime.crime_type}
                      </td>
                      <td className="px-4 py-3.5 text-xs text-slate-400">
                        {crime.crime_category}
                      </td>
                      <td className="px-4 py-3.5 text-xs text-slate-300 font-medium">
                        {crime.district}
                      </td>
                      <td className="px-4 py-3.5">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold ${getSeverityBadge(crime.severity)}`}>
                          {crime.severity.toFixed(1)}
                        </span>
                      </td>
                      <td className="px-4 py-3.5">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[9px] font-extrabold tracking-wider ${statusDetails.className}`}>
                          {statusDetails.label}
                        </span>
                      </td>
                      <td className="px-4 py-3.5 text-xs text-slate-400 font-mono">
                        {formatDate(crime.crime_date)}
                      </td>
                      <td className="px-4 py-3.5 text-xs text-slate-400 text-center font-bold">
                        {crime.victim_count}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
