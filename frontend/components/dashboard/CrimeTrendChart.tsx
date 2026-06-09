"use client";

import React from "react";
import { AlertCircle } from "lucide-react";
import {
  ResponsiveContainer,
  ComposedChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";
import type { TooltipContentProps } from "recharts/types/component/Tooltip";
import type { TrendDataPoint } from "@/types/dashboard";

interface CrimeTrendChartProps {
  data: TrendDataPoint[];
  loading?: boolean;
  error?: string;
  onRetry?: () => void;
}

// Custom tooltip renderer
const CustomTooltip = ({ active, payload }: TooltipContentProps) => {
  if (active && payload && payload.length) {
    const dataPoint = payload[0].payload as TrendDataPoint;
    const rawValue = payload[0].value;
    const displayValue = Array.isArray(rawValue) ? rawValue.join(', ') : String(rawValue ?? '');
    const formattedDate = new Date(dataPoint.date).toLocaleDateString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });

    return (
      <div className="bg-[#0f172a] border border-[#1e293b] p-3 rounded-lg shadow-xl">
        <p className="text-[10px] uppercase tracking-wider font-bold text-slate-500">
          {formattedDate}
        </p>
        <p className="text-sm font-extrabold text-indigo-400 mt-1">
          {displayValue} <span className="text-xs text-slate-400 font-medium">crimes</span>
        </p>
      </div>
    );
  }
  return null;
};

export default function CrimeTrendChart({
  data,
  loading = false,
  error,
  onRetry,
}: CrimeTrendChartProps) {
  // Helper to format date ticks for XAxis
  const formatXAxis = (tickItem: string) => {
    try {
      const dateObj = new Date(tickItem);
      return dateObj.toLocaleDateString("en-US", { month: "short", day: "numeric" });
    } catch {
      return tickItem;
    }
  };

  const renderHeader = () => (
    <div className="flex items-center gap-2 mb-5">
      <div className="w-1 h-5 bg-indigo-500 rounded" />
      <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
        Temporal Crime Trends
      </h3>
    </div>
  );

  if (loading) {
    return (
      <div className="glass-card p-6 rounded-2xl border border-slate-800/60 h-[370px] flex flex-col">
        {renderHeader()}
        <div className="flex-1 flex flex-col justify-between h-[280px] bg-slate-800/20 rounded-xl p-4 animate-pulse relative">
          <div className="w-full h-[1px] bg-slate-800/50 mt-8" />
          <div className="w-full h-[1px] bg-slate-800/50" />
          <div className="w-full h-[1px] bg-slate-800/50" />
          <div className="w-full h-[1px] bg-slate-800/50 mb-8" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass-card p-6 rounded-2xl border border-slate-800/60 h-[370px] flex flex-col">
        {renderHeader()}
        <div className="flex-1 flex flex-col items-center justify-center border border-dashed border-red-500/20 rounded-xl bg-red-500/5 p-6 text-center">
          <AlertCircle className="w-8 h-8 text-red-500 mb-3 animate-pulse" />
          <p className="text-xs text-slate-300 max-w-sm mb-4">
            {error || "Failed to load crime trends. Please try again."}
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
      </div>
    );
  }

  return (
    <div className="glass-card p-6 rounded-2xl border border-slate-800/60 h-[370px] flex flex-col">
      {renderHeader()}
      <div className="flex-1 min-h-0">
        <ResponsiveContainer width="100%" height={280}>
          <ComposedChart data={data} margin={{ top: 10, right: 5, left: -25, bottom: 0 }}>
            <defs>
              <linearGradient id="trendGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#6366f1" stopOpacity={0.25} />
                <stop offset="95%" stopColor="#6366f1" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
            <XAxis
              dataKey="date"
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
            <Tooltip content={CustomTooltip} cursor={{ stroke: "#1e293b" }} />
            <Area
              type="monotone"
              dataKey="count"
              stroke="#6366f1"
              strokeWidth={2}
              fill="url(#trendGradient)"
              dot={false}
              activeDot={{ r: 4, stroke: "#6366f1", strokeWidth: 1 }}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
