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
                  <td colSpan={8} className="px-4 py-8 text-center text-xs font-medium text-slate-400">
                    No recent crime data available
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
