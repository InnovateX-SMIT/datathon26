import React from "react";
import type { PredictiveInsights } from "../types/report";
import { ShieldAlert, AlertTriangle, Info } from "lucide-react";

interface Props {
  insights: PredictiveInsights;
}

export default function ReportTrendsSection({ insights }: Props) {
  const getRiskLevelBadge = (level: string) => {
    switch (level.toUpperCase()) {
      case "CRITICAL":
        return "bg-red-500/10 border-red-500/20 text-red-400";
      case "HIGH":
        return "bg-amber-500/10 border-amber-500/20 text-amber-400";
      default:
        return "bg-indigo-500/10 border-indigo-500/20 text-indigo-400";
    }
  };

  const getRiskIcon = (level: string) => {
    switch (level.toUpperCase()) {
      case "CRITICAL":
        return <ShieldAlert className="w-4 h-4 text-red-400" />;
      case "HIGH":
        return <AlertTriangle className="w-4 h-4 text-amber-400" />;
      default:
        return <Info className="w-4 h-4 text-indigo-400" />;
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-fade-in report-trends-grid">
      {/* High Risk Locations Table */}
      <div className="glass-card p-6 rounded-2xl border border-slate-800/60 flex flex-col justify-between">
        <div>
          <div className="flex items-center gap-2 mb-4">
            <div className="w-1 h-5 bg-indigo-500 rounded" />
            <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
              High-Risk District Locations
            </h3>
          </div>
          
          {insights.high_risk_locations.length === 0 ? (
            <div className="flex flex-col items-center justify-center p-8 border border-dashed border-slate-800 rounded-xl bg-slate-900/25">
              <p className="text-xs text-slate-500">No high-risk locations computed.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider">
                    <th className="py-2.5 px-3">District</th>
                    <th className="py-2.5 px-3 text-right">Crimes Logged</th>
                    <th className="py-2.5 px-3 text-right">Clearance Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/40 text-slate-300">
                  {insights.high_risk_locations.map((loc, idx) => (
                    <tr key={idx} className="hover:bg-slate-900/35 transition-colors">
                      <td className="py-3 px-3 font-semibold text-slate-200">{loc.district}</td>
                      <td className="py-3 px-3 text-right font-mono">{loc.crime_count.toLocaleString()}</td>
                      <td className="py-3 px-3 text-right">
                        <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded text-[10px] font-bold border uppercase ${getRiskLevelBadge(loc.risk_level)}`}>
                          {getRiskIcon(loc.risk_level)}
                          {loc.risk_level}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Predictive Indicators Summary */}
      <div className="glass-card p-6 rounded-2xl border border-slate-800/60 flex flex-col justify-between">
        <div>
          <div className="flex items-center gap-2 mb-6">
            <div className="w-1 h-5 bg-indigo-500 rounded" />
            <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
              Recidivism & Spot Indicators
            </h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Active Hotspots Count */}
            <div className="p-4 bg-slate-950/40 border border-slate-900 rounded-xl">
              <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Active Hotspots Flagged</p>
              <p className="text-2xl font-black text-white mt-1 tracking-tight">
                {insights.hotspot_count}
              </p>
              <p className="text-[10px] text-indigo-400 font-semibold mt-1">Probability Threshold &gt; 70%</p>
            </div>

            {/* Avg Risk Score */}
            <div className="p-4 bg-slate-950/40 border border-slate-900 rounded-xl">
              <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Average Accused Risk Index</p>
              <p className="text-2xl font-black text-white mt-1 tracking-tight">
                {insights.risk_score_summary.average_criminal_risk} <span className="text-xs text-slate-500 font-semibold">/ 10</span>
              </p>
              <p className="text-[10px] text-indigo-400 font-semibold mt-1">Database-wide Mean Score</p>
            </div>

            {/* High Risk Offenders Count */}
            <div className="p-4 bg-slate-950/40 border border-slate-900 rounded-xl">
              <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">High Risk Repeat Suspects</p>
              <p className="text-2xl font-black text-white mt-1 tracking-tight text-amber-500">
                {insights.risk_score_summary.high_risk_criminals_count}
              </p>
              <p className="text-[10px] text-amber-400 font-semibold mt-1">Risk Rating Scale &gt;= 7.0</p>
            </div>

            {/* Total Monitored */}
            <div className="p-4 bg-slate-950/40 border border-slate-900 rounded-xl">
              <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Total Tracked Suspects</p>
              <p className="text-2xl font-black text-white mt-1 tracking-tight">
                {insights.risk_score_summary.total_criminals_tracked.toLocaleString()}
              </p>
              <p className="text-[10px] text-indigo-400 font-semibold mt-1">Full Offender Registry Size</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
