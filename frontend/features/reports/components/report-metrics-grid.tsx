import React from "react";
import type { CrimeOverview } from "../types/report";
import { ShieldAlert, TrendingUp, TrendingDown, Minus, Layers } from "lucide-react";

interface Props {
  overview: CrimeOverview;
}

export default function ReportMetricsGrid({ overview }: Props) {
  const getTrendIcon = (direction: string) => {
    switch (direction.toUpperCase()) {
      case "UP":
        return <TrendingUp className="w-5 h-5 text-red-500" />;
      case "DOWN":
        return <TrendingDown className="w-5 h-5 text-emerald-500" />;
      default:
        return <Minus className="w-5 h-5 text-slate-400" />;
    }
  };

  const getTrendBadgeClass = (direction: string) => {
    switch (direction.toUpperCase()) {
      case "UP":
        return "bg-red-500/10 border-red-500/20 text-red-400";
      case "DOWN":
        return "bg-emerald-500/10 border-emerald-500/20 text-emerald-400";
      default:
        return "bg-slate-500/10 border-slate-500/20 text-slate-400";
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 animate-fade-in report-metrics-grid">
      {/* Total Crimes Card */}
      <div className="glass-card p-6 rounded-2xl border border-slate-800/80 shadow-md flex items-center gap-5 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-24 h-24 bg-indigo-500/5 rounded-full blur-2xl pointer-events-none" />
        <div className="bg-indigo-500/10 border border-indigo-500/25 p-3.5 rounded-xl text-indigo-400 shadow-inner">
          <ShieldAlert className="w-6 h-6" />
        </div>
        <div>
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Crimes Indexed</p>
          <p className="text-3xl font-black text-white mt-1 tracking-tight">{overview.total_crimes.toLocaleString()}</p>
        </div>
      </div>

      {/* Crime Trend Card */}
      <div className="glass-card p-6 rounded-2xl border border-slate-800/80 shadow-md flex items-center gap-5 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-24 h-24 bg-pink-500/5 rounded-full blur-2xl pointer-events-none" />
        <div className="bg-pink-500/10 border border-pink-500/25 p-3.5 rounded-xl text-pink-400 shadow-inner">
          {getTrendIcon(overview.trend_direction)}
        </div>
        <div>
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Historical Trend Direction</p>
          <div className="flex items-center gap-2 mt-1">
            <p className="text-2xl font-black text-white tracking-tight">{overview.trend_direction}</p>
            <span className={`px-2 py-0.5 rounded text-[10px] font-bold border uppercase ${getTrendBadgeClass(overview.trend_direction)}`}>
              {overview.trend_direction === "UP" ? "Spike Risk" : overview.trend_direction === "DOWN" ? "Improving" : "Steady"}
            </span>
          </div>
        </div>
      </div>

      {/* Top Category Card */}
      <div className="glass-card p-6 rounded-2xl border border-slate-800/80 shadow-md flex items-center gap-5 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-24 h-24 bg-cyan-500/5 rounded-full blur-2xl pointer-events-none" />
        <div className="bg-cyan-500/10 border border-cyan-500/25 p-3.5 rounded-xl text-cyan-400 shadow-inner">
          <Layers className="w-6 h-6" />
        </div>
        <div>
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Primary Crime Category</p>
          <p className="text-xl font-bold text-white mt-1 truncate max-w-[200px]">
            {overview.top_categories.length > 0 ? overview.top_categories[0].category : "None"}
          </p>
          <p className="text-[10px] text-slate-500 mt-0.5">
            {overview.top_categories.length > 0 
              ? `${overview.top_categories[0].count} registered incidents` 
              : "0 incidents"}
          </p>
        </div>
      </div>
    </div>
  );
}
