import React from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";
import type { TooltipContentProps } from "recharts/types/component/Tooltip";
import type { TrendResponse } from "../types/analytics";

interface TemporalTrendChartProps {
  data: TrendResponse[];
  granularity: string;
  onGranularityChange: (granularity: string) => void;
  loading?: boolean;
}

const CustomTooltip = ({ active, payload }: TooltipContentProps) => {
  if (active && payload && payload.length) {
    const dataPoint = payload[0].payload as TrendResponse;
    const value = payload[0].value;
    return (
      <div className="bg-[#0f172a]/95 border border-[#1e293b] p-3 rounded-lg shadow-xl backdrop-blur-md">
        <p className="text-[10px] uppercase tracking-wider font-bold text-slate-400">
          Period: {dataPoint.period}
        </p>
        <p className="text-sm font-extrabold text-indigo-400 mt-1">
          {value} <span className="text-xs text-slate-400 font-medium">crimes</span>
        </p>
      </div>
    );
  }
  return null;
};

export default function TemporalTrendChart({
  data,
  granularity,
  onGranularityChange,
  loading,
}: TemporalTrendChartProps) {
  const options = [
    { label: "Daily", value: "daily" },
    { label: "Weekly", value: "weekly" },
    { label: "Monthly", value: "monthly" },
    { label: "Yearly", value: "yearly" },
  ];

  const formatXAxis = (tickItem: string) => {
    if (granularity === "daily") {
      try {
        const dateObj = new Date(tickItem);
        return dateObj.toLocaleDateString("en-US", { month: "short", day: "numeric" });
      } catch {
        return tickItem;
      }
    }
    return tickItem;
  };

  const renderHeader = () => (
    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
      <div className="flex items-center gap-2">
        <div className="w-1 h-5 bg-indigo-500 rounded" />
        <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
          Temporal Analytics
        </h3>
      </div>
      <div className="flex bg-slate-900/60 p-1 rounded-xl border border-slate-800/50 self-start">
        {options.map((opt) => (
          <button
            key={opt.value}
            onClick={() => onGranularityChange(opt.value)}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all duration-200 cursor-pointer ${
              granularity === opt.value
                ? "bg-indigo-600 text-white shadow-md"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            {opt.label}
          </button>
        ))}
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="glass-card p-6 rounded-2xl border border-slate-800/60 h-[400px] flex flex-col mb-6">
        {renderHeader()}
        <div className="flex-1 flex flex-col justify-between h-[280px] bg-slate-800/10 rounded-xl p-4 animate-pulse relative">
          <div className="w-full h-[1px] bg-slate-800/40 mt-8" />
          <div className="w-full h-[1px] bg-slate-800/40" />
          <div className="w-full h-[1px] bg-slate-800/40" />
          <div className="w-full h-[1px] bg-slate-800/40 mb-8" />
        </div>
      </div>
    );
  }

  return (
    <div className="glass-card p-6 rounded-2xl border border-slate-800/60 h-[400px] flex flex-col mb-6">
      {renderHeader()}
      <div className="flex-1 min-h-0">
        {data.length === 0 ? (
          <div className="h-full flex items-center justify-center border border-dashed border-slate-800 rounded-xl p-6 text-center text-slate-400">
            No temporal trend data available.
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
              <XAxis
                dataKey="period"
                tickFormatter={formatXAxis}
                tick={{ fill: "#94a3b8", fontSize: 10 }}
                tickLine={false}
                axisLine={false}
                dy={10}
              />
              <YAxis
                tick={{ fill: "#94a3b8", fontSize: 10 }}
                tickLine={false}
                axisLine={false}
                dx={-5}
              />
              <Tooltip content={CustomTooltip} cursor={{ stroke: "#334155" }} />
              <Line
                type="monotone"
                dataKey="count"
                stroke="#6366f1"
                strokeWidth={3}
                dot={{ r: 3, fill: "#6366f1", strokeWidth: 0 }}
                activeDot={{ r: 6, stroke: "#818cf8", strokeWidth: 2 }}
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}
