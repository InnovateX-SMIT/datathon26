import React from "react";
import { TrendingUp, TrendingDown, CalendarRange } from "lucide-react";
import type { ComparisonResponse } from "../types/analytics";

interface HistoricalComparisonCardProps {
  data: ComparisonResponse | null;
  loading?: boolean;
}

export default function HistoricalComparisonCard({ data, loading }: HistoricalComparisonCardProps) {
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {Array.from({ length: 2 }).map((_, i) => (
          <div key={i} className="glass-card p-6 rounded-2xl border border-slate-800/60 animate-pulse h-[200px] flex flex-col justify-between">
            <div className="h-4 w-32 bg-slate-800 rounded" />
            <div className="space-y-3">
              <div className="h-8 w-24 bg-slate-800/50 rounded" />
              <div className="h-4 w-48 bg-slate-800/55 rounded" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  const momChange = data?.month_change_percent ?? 0;
  const yoyChange = data?.year_change_percent ?? 0;

  const renderTrendBadge = (change: number) => {
    const isDecrease = change < 0;
    const isZero = change === 0;

    if (isZero) {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-slate-850 text-slate-400">
          No change
        </span>
      );
    }

    return (
      <span
        className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold ${
          isDecrease
            ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
            : "bg-rose-500/10 text-rose-400 border border-rose-500/20"
        }`}
      >
        {isDecrease ? (
          <TrendingDown className="w-3.5 h-3.5" />
        ) : (
          <TrendingUp className="w-3.5 h-3.5" />
        )}
        {Math.abs(change).toFixed(2)}% {isDecrease ? "reduction" : "increase"}
      </span>
    );
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
      {/* Month-over-Month Card */}
      <div className="glass-card p-6 rounded-2xl border border-slate-800/60 flex flex-col justify-between h-[200px] relative overflow-hidden bg-gradient-to-br from-indigo-500/5 to-transparent">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CalendarRange className="w-4 h-4 text-indigo-400" />
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
              Month-over-Month
            </h4>
          </div>
          {renderTrendBadge(momChange)}
        </div>
        <div className="mt-4">
          <div className="flex items-baseline gap-2">
            <span className="text-4xl font-extrabold text-white">
              {(data?.current_month ?? 0).toLocaleString("en-IN")}
            </span>
            <span className="text-xs font-medium text-slate-400">crimes this month</span>
          </div>
          <p className="text-xs text-slate-500 mt-2">
            Compared to{" "}
            <span className="text-slate-300 font-semibold">
              {(data?.previous_month ?? 0).toLocaleString("en-IN")}
            </span>{" "}
            crimes in the previous month.
          </p>
        </div>
      </div>

      {/* Year-over-Year Card */}
      <div className="glass-card p-6 rounded-2xl border border-slate-800/60 flex flex-col justify-between h-[200px] relative overflow-hidden bg-gradient-to-br from-indigo-500/5 to-transparent">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CalendarRange className="w-4 h-4 text-blue-400" />
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
              Year-over-Year
            </h4>
          </div>
          {renderTrendBadge(yoyChange)}
        </div>
        <div className="mt-4">
          <div className="flex items-baseline gap-2">
            <span className="text-4xl font-extrabold text-white">
              {(data?.current_year ?? 0).toLocaleString("en-IN")}
            </span>
            <span className="text-xs font-medium text-slate-400">crimes this year</span>
          </div>
          <p className="text-xs text-slate-500 mt-2">
            Compared to{" "}
            <span className="text-slate-300 font-semibold">
              {(data?.previous_year ?? 0).toLocaleString("en-IN")}
            </span>{" "}
            crimes in the previous year.
          </p>
        </div>
      </div>
    </div>
  );
}
