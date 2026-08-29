"use client";

import React, { useMemo, useState } from "react";
import {
  Clock,
  Moon,
  Sunrise,
  Sun,
  Sunset,
  TrendingUp,
  BarChart3,
  Activity,
  Flame,
} from "lucide-react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
} from "recharts";
import type { TimeOfDayResponse, HourlyDataPoint } from "../types/geo";

interface TimeOfDayAnalysisProps {
  data?: TimeOfDayResponse | null;
  loading?: boolean;
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{ payload: HourlyDataPoint & { periodName: string; pct: string; isPeak: boolean } }>;
}

const CustomHourlyTooltip = ({ active, payload }: CustomTooltipProps) => {
  if (active && payload && payload.length) {
    const d = payload[0].payload;
    const nextHour = (d.hour + 1) % 24;
    const nextHourStr = `${String(nextHour).padStart(2, "0")}:00`;
    return (
      <div className="glass-card bg-[#0f172a]/95 border border-indigo-500/30 p-3.5 rounded-xl shadow-2xl backdrop-blur-xl space-y-2 min-w-[170px] pointer-events-none">
        <div className="flex items-center justify-between gap-2 border-b border-slate-800 pb-1.5">
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 font-mono">
            {d.label} – {nextHourStr}
          </span>
          <span className="text-[9px] px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300 font-bold uppercase">
            {d.periodName}
          </span>
        </div>

        <div className="flex items-baseline justify-between gap-3">
          <div>
            <span className="text-[10px] text-slate-500 block uppercase font-bold">Incidents</span>
            <span className="text-xl font-black text-indigo-400 font-mono">
              {d.count.toLocaleString()}
            </span>
          </div>
          <div className="text-right">
            <span className="text-[10px] text-slate-500 block uppercase font-bold">Share</span>
            <span className="text-xs font-bold text-slate-300 font-mono">{d.pct}%</span>
          </div>
        </div>

        {d.isPeak && (
          <div className="flex items-center gap-1.5 text-[10px] font-bold text-rose-400 bg-rose-500/10 border border-rose-500/20 px-2 py-0.5 rounded-md mt-1">
            <Flame className="w-3 h-3 text-rose-400 shrink-0 animate-pulse" />
            <span>24-Hour Peak Window</span>
          </div>
        )}
      </div>
    );
  }
  return null;
};

export default function TimeOfDayAnalysis({ data, loading }: TimeOfDayAnalysisProps) {
  const [chartMode, setChartMode] = useState<"bar" | "area">("bar");
  const [hoveredHour, setHoveredHour] = useState<number | null>(null);

  const total = data?.total_analyzed || 0;

  const maxHourlyCount = useMemo(() => {
    if (!data?.hourly || data.hourly.length === 0) return 1;
    return Math.max(...data.hourly.map((h) => h.count), 1);
  }, [data]);

  const getPeriodForHour = (hour: number) => {
    if (hour >= 0 && hour < 6) return "Night";
    if (hour >= 6 && hour < 12) return "Morning";
    if (hour >= 12 && hour < 18) return "Afternoon";
    return "Evening";
  };

  const chartData = useMemo(() => {
    if (!data?.hourly) return [];
    return data.hourly.map((h) => {
      const pct = total > 0 ? ((h.count / total) * 100).toFixed(1) : "0.0";
      const isPeak = h.count === maxHourlyCount && h.count > 0;
      return {
        ...h,
        periodName: getPeriodForHour(h.hour),
        pct,
        isPeak,
        displayHour: `${String(h.hour).padStart(2, "0")}h`,
      };
    });
  }, [data, maxHourlyCount, total]);

  const periods = [
    {
      key: "night",
      title: "Night",
      time: "00:00 – 06:00",
      count: data?.periods?.night || 0,
      icon: Moon,
      color: "from-indigo-950/40 to-slate-900/40 border-indigo-500/20 text-indigo-400",
      badgeColor: "bg-indigo-500/10 text-indigo-300 border-indigo-500/30",
    },
    {
      key: "morning",
      title: "Morning",
      time: "06:00 – 12:00",
      count: data?.periods?.morning || 0,
      icon: Sunrise,
      color: "from-amber-950/30 to-slate-900/40 border-amber-500/20 text-amber-400",
      badgeColor: "bg-amber-500/10 text-amber-300 border-amber-500/30",
    },
    {
      key: "afternoon",
      title: "Afternoon",
      time: "12:00 – 18:00",
      count: data?.periods?.afternoon || 0,
      icon: Sun,
      color: "from-sky-950/30 to-slate-900/40 border-sky-500/20 text-sky-400",
      badgeColor: "bg-sky-500/10 text-sky-300 border-sky-500/30",
    },
    {
      key: "evening",
      title: "Evening",
      time: "18:00 – 24:00",
      count: data?.periods?.evening || 0,
      icon: Sunset,
      color: "from-rose-950/30 to-slate-900/40 border-rose-500/20 text-rose-400",
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
      {/* ── Header ──────────────────────────────────────────────────────────── */}
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

      {/* ── 4 Time-Period Metric Cards ──────────────────────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {periods.map((p) => {
          const Icon = p.icon;
          const pct = total > 0 ? ((p.count / total) * 100).toFixed(1) : "0.0";
          return (
            <div
              key={p.key}
              className={`p-4 rounded-xl border bg-gradient-to-b ${p.color} flex flex-col justify-between transition-all duration-300 hover:scale-[1.01]`}
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

      {/* ── 24-Hour Interactive Timeline Distribution ─────────────────────────── */}
      <div className="space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs text-slate-400 font-sans">
          <div className="flex items-center gap-2">
            <span className="font-semibold uppercase tracking-wider text-[10px] text-slate-300">
              24-Hour Incident Distribution Timeline
            </span>
            <span className="text-[10px] text-slate-500 font-mono hidden sm:inline">• Hover or click bars for granular temporal analysis</span>
          </div>

          {/* View Mode Toggle */}
          <div className="flex items-center gap-1 bg-slate-950/60 p-1 border border-slate-800/80 rounded-xl">
            <button
              onClick={() => setChartMode("bar")}
              className={`flex items-center gap-1 px-2.5 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-colors cursor-pointer ${
                chartMode === "bar"
                  ? "bg-indigo-600 text-white shadow"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <BarChart3 className="w-3 h-3" />
              Hourly Bars
            </button>
            <button
              onClick={() => setChartMode("area")}
              className={`flex items-center gap-1 px-2.5 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-colors cursor-pointer ${
                chartMode === "area"
                  ? "bg-indigo-600 text-white shadow"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <Activity className="w-3 h-3" />
              Diurnal Curve
            </button>
          </div>
        </div>

        {/* Chart Container */}
        <div className="bg-slate-950/60 border border-slate-800/80 rounded-2xl p-4 sm:p-5 relative overflow-hidden">
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              {chartMode === "bar" ? (
                <BarChart
                  data={chartData}
                  margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
                  onMouseMove={(state) => {
                    if (state?.activeTooltipIndex !== undefined && state.activeTooltipIndex !== null) {
                      setHoveredHour(state.activeTooltipIndex as number);
                    }
                  }}
                  onMouseLeave={() => setHoveredHour(null)}
                >
                  <defs>
                    <linearGradient id="barStandard" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#6366f1" stopOpacity={0.9} />
                      <stop offset="100%" stopColor="#4338ca" stopOpacity={0.4} />
                    </linearGradient>
                    <linearGradient id="barPeak" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#f43f5e" stopOpacity={1} />
                      <stop offset="100%" stopColor="#be123c" stopOpacity={0.6} />
                    </linearGradient>
                    <linearGradient id="barHigh" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#818cf8" stopOpacity={0.95} />
                      <stop offset="100%" stopColor="#4f46e5" stopOpacity={0.5} />
                    </linearGradient>
                  </defs>

                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} opacity={0.6} />

                  <XAxis
                    dataKey="displayHour"
                    stroke="#64748b"
                    fontSize={10}
                    tickLine={false}
                    axisLine={{ stroke: "#334155" }}
                    interval={1}
                  />

                  <YAxis
                    stroke="#64748b"
                    fontSize={10}
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={(val) => Number(val).toLocaleString()}
                  />

                  <Tooltip content={<CustomHourlyTooltip />} cursor={{ fill: "rgba(99, 102, 241, 0.08)" }} />

                  <Bar
                    dataKey="count"
                    radius={[6, 6, 0, 0]}
                    animationDuration={600}
                  >
                    {chartData.map((entry, index) => {
                      const isHovered = hoveredHour === index;
                      let fillUrl = "url(#barStandard)";
                      if (entry.isPeak) fillUrl = "url(#barPeak)";
                      else if (entry.count > maxHourlyCount * 0.7) fillUrl = "url(#barHigh)";

                      return (
                        <Cell
                          key={`cell-${index}`}
                          fill={fillUrl}
                          stroke={isHovered ? "#ffffff" : entry.isPeak ? "#f43f5e" : "transparent"}
                          strokeWidth={isHovered ? 1.5 : 0}
                          style={{
                            filter: isHovered
                              ? "drop-shadow(0 0 8px rgba(99, 102, 241, 0.6))"
                              : entry.isPeak
                              ? "drop-shadow(0 0 6px rgba(244, 63, 94, 0.4))"
                              : "none",
                            transition: "all 0.2s ease",
                            cursor: "pointer",
                          }}
                        />
                      );
                    })}
                  </Bar>
                </BarChart>
              ) : (
                <AreaChart
                  data={chartData}
                  margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
                >
                  <defs>
                    <linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#6366f1" stopOpacity={0.5} />
                      <stop offset="60%" stopColor="#a855f7" stopOpacity={0.2} />
                      <stop offset="100%" stopColor="#0f172a" stopOpacity={0} />
                    </linearGradient>
                  </defs>

                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} opacity={0.6} />

                  <XAxis
                    dataKey="displayHour"
                    stroke="#64748b"
                    fontSize={10}
                    tickLine={false}
                    axisLine={{ stroke: "#334155" }}
                    interval={1}
                  />

                  <YAxis
                    stroke="#64748b"
                    fontSize={10}
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={(val) => Number(val).toLocaleString()}
                  />

                  <Tooltip content={<CustomHourlyTooltip />} />

                  <Area
                    type="monotone"
                    dataKey="count"
                    stroke="#6366f1"
                    strokeWidth={2.5}
                    fillOpacity={1}
                    fill="url(#areaGradient)"
                    activeDot={{
                      r: 6,
                      fill: "#818cf8",
                      stroke: "#ffffff",
                      strokeWidth: 2,
                      style: { filter: "drop-shadow(0 0 8px rgba(99, 102, 241, 0.8))" },
                    }}
                    animationDuration={800}
                  />
                </AreaChart>
              )}
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* ── Top Crime Categories by Time Period ──────────────────────────────── */}
      {data.category_by_time && data.category_by_time.length > 0 && (
        <div className="space-y-3">
          <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider font-sans">
            Top Crime Categories by Time Period
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
            {data.category_by_time.map((item) => (
              <div
                key={item.period}
                className="bg-slate-950/40 border border-slate-800/80 rounded-xl p-3.5 space-y-2 hover:border-slate-700/80 transition-colors"
              >
                <div className="text-[11px] font-bold text-slate-200 border-b border-slate-800/80 pb-1.5 font-sans flex items-center justify-between">
                  <span>{item.period}</span>
                  <span className="text-[9px] text-slate-500 font-mono uppercase">Distribution</span>
                </div>
                {item.top_categories.length > 0 ? (
                  <div className="space-y-1.5 pt-1">
                    {item.top_categories.map((c) => (
                      <div
                        key={c.category}
                        className="flex items-center justify-between text-[11px] text-slate-400 font-sans"
                      >
                        <span className="truncate max-w-[130px]">{c.category}</span>
                        <span className="font-bold text-slate-200 font-mono">{c.count.toLocaleString()}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-[10px] text-slate-600 font-sans italic py-2">No crimes in this period</div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
