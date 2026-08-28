"use client";

import React, { useMemo } from "react";
import { Clock, Moon, Sunrise, Sun, Sunset, TrendingUp, AlertTriangle } from "lucide-react";
import type { TimeOfDayResponse } from "../types/geo";

interface TimeOfDayAnalysisProps {
  data?: TimeOfDayResponse | null;
  loading?: boolean;
}

export default function TimeOfDayAnalysis({ data, loading }: TimeOfDayAnalysisProps) {
  const total = data?.total_analyzed || 0;

  const maxHourlyCount = useMemo(() => {
    if (!data?.hourly || data.hourly.length === 0) return 1;
    return Math.max(...data.hourly.map((h) => h.count), 1);
  }, [data]);

  const periods = [
    {
      key: "night",
      title: "Night",
      time: "00:00 – 06:00",
      count: data?.periods?.night || 0,
      icon: Moon,
      color: "from-indigo-900/40 to-slate-900/40 border-indigo-500/20 text-indigo-400",
      badgeColor: "bg-indigo-500/10 text-indigo-300 border-indigo-500/30",
    },
    {
      key: "morning",
      title: "Morning",
      time: "06:00 – 12:00",
      count: data?.periods?.morning || 0,
      icon: Sunrise,
      color: "from-amber-900/30 to-slate-900/40 border-amber-500/20 text-amber-400",
      badgeColor: "bg-amber-500/10 text-amber-300 border-amber-500/30",
    },
    {
      key: "afternoon",
      title: "Afternoon",
      time: "12:00 – 18:00",
      count: data?.periods?.afternoon || 0,
      icon: Sun,
      color: "from-sky-900/30 to-slate-900/40 border-sky-500/20 text-sky-400",
      badgeColor: "bg-sky-500/10 text-sky-300 border-sky-500/30",
    },
    {
      key: "evening",
      title: "Evening",
      time: "18:00 – 24:00",
      count: data?.periods?.evening || 0,
      icon: Sunset,
      color: "from-rose-900/30 to-slate-900/40 border-rose-500/20 text-rose-400",
      badgeColor: "bg-rose-500/10 text-rose-300 border-rose-500/30",
    },
  ];

  if (loading) {
    return (
      <div className="glass-card p-6 rounded-2xl border border-slate-800/60 bg-slate-900/30 backdrop-blur-md animate-pulse">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-1.5 h-5 bg-indigo-500 rounded" />
          <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-sans">
            Time-of-Day Temporal Pattern Analysis
          </h3>
        </div>
        <div className="h-48 bg-slate-800/20 rounded-xl flex items-center justify-center text-slate-500 text-xs font-sans">
          Aggregating incident timestamps and diurnal distributions...
        </div>
      </div>
    );
  }

  if (!data || total === 0) {
    return (
      <div className="glass-card p-6 rounded-2xl border border-slate-800/60 bg-slate-900/30 backdrop-blur-md">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-1.5 h-5 bg-indigo-500 rounded" />
          <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-sans">
            Time-of-Day Temporal Pattern Analysis
          </h3>
        </div>
        <div className="py-8 rounded-xl border border-dashed border-slate-800 bg-slate-950/40 text-center text-slate-500 text-xs font-sans">
          No incident timestamp records available for active filters.
        </div>
      </div>
    );
  }

  return (
    <div className="glass-card p-6 rounded-2xl border border-slate-800/60 bg-slate-900/30 backdrop-blur-md space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800/60 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 rounded-xl">
            <Clock className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider font-sans flex items-center gap-2">
              Time-of-Day Incident Analysis
              <span className="text-[10px] bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 px-2 py-0.5 rounded-full font-mono">
                {total.toLocaleString()} Incidents
              </span>
            </h3>
            <p className="text-xs text-slate-400 font-sans mt-0.5">
              Diurnal incident distribution derived from official incident timestamps
            </p>
          </div>
        </div>

        {/* Peak Window Badge */}
        {data.peak_hour && (
          <div className="flex items-center gap-2 px-3 py-1.5 bg-rose-500/10 border border-rose-500/20 rounded-xl text-xs font-sans text-rose-300">
            <TrendingUp className="w-3.5 h-3.5 text-rose-400 flex-shrink-0" />
            <span>
              Peak Risk Hour: <strong className="text-rose-200">{data.peak_hour}</strong>
            </span>
          </div>
        )}
      </div>

      {/* 4 Time-Period Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {periods.map((p) => {
          const Icon = p.icon;
          const pct = total > 0 ? ((p.count / total) * 100).toFixed(1) : "0.0";
          return (
            <div
              key={p.key}
              className={`p-4 rounded-xl border bg-gradient-to-b ${p.color} flex flex-col justify-between`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Icon className="w-4 h-4" />
                  <span className="text-xs font-bold text-slate-200 uppercase font-sans">{p.title}</span>
                </div>
                <span className="text-[10px] text-slate-400 font-mono">{p.time}</span>
              </div>

              <div className="mt-3 flex items-baseline justify-between">
                <span className="text-2xl font-black text-slate-100 font-mono">
                  {p.count.toLocaleString()}
                </span>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${p.badgeColor}`}>
                  {pct}%
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* 24-Hour Timeline Bar Distribution */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-xs text-slate-400 font-sans">
          <span className="font-semibold uppercase tracking-wider text-[10px] text-slate-300">
            24-Hour Incident Distribution Timeline
          </span>
          <span className="text-[10px] text-slate-500 font-mono">Hover over bar for precise count</span>
        </div>

        <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-4">
          <div className="grid grid-cols-24 gap-1 items-end h-32 pt-4">
            {data.hourly.map((h) => {
              const heightPct = Math.max(4, Math.round((h.count / maxHourlyCount) * 100));
              const isPeak = h.count === maxHourlyCount && h.count > 0;
              return (
                <div
                  key={`hour-${h.hour}`}
                  className="flex flex-col items-center h-full justify-end group relative"
                >
                  {/* Tooltip on hover */}
                  <div className="absolute -top-8 bg-slate-900 text-slate-100 text-[10px] px-2 py-0.5 rounded border border-slate-700 pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity z-20 whitespace-nowrap shadow-lg">
                    {h.label}: <strong className="text-indigo-400">{h.count} crimes</strong>
                  </div>

                  {/* Bar */}
                  <div
                    style={{ height: `${heightPct}%` }}
                    className={`w-full rounded-t transition-all ${
                      isPeak
                        ? "bg-rose-500 shadow-md shadow-rose-500/30"
                        : h.count > maxHourlyCount * 0.6
                        ? "bg-indigo-500 group-hover:bg-indigo-400"
                        : "bg-indigo-900/60 group-hover:bg-indigo-700"
                    }`}
                  />
                  {/* Hour label below bar for every 3 hours */}
                  {h.hour % 3 === 0 && (
                    <span className="text-[8px] text-slate-500 font-mono mt-1">
                      {h.hour}h
                    </span>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Crime Category Breakdown Across Time Periods */}
      {data.category_by_time && data.category_by_time.length > 0 && (
        <div className="space-y-3">
          <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider font-sans">
            Top Crime Categories by Time Period
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
            {data.category_by_time.map((item) => (
              <div
                key={item.period}
                className="bg-slate-950/40 border border-slate-800/80 rounded-xl p-3 space-y-2"
              >
                <div className="text-[11px] font-bold text-slate-200 border-b border-slate-800/80 pb-1 font-sans">
                  {item.period}
                </div>
                {item.top_categories.length > 0 ? (
                  <div className="space-y-1">
                    {item.top_categories.map((c) => (
                      <div
                        key={c.category}
                        className="flex items-center justify-between text-[10px] text-slate-400 font-sans"
                      >
                        <span className="truncate max-w-[120px]">{c.category}</span>
                        <span className="font-bold text-slate-200 font-mono">{c.count}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-[10px] text-slate-600 font-sans italic">No crimes in this period</div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
