"use client";

import React from "react";
import { AlertCircle } from "lucide-react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";
import type { TooltipContentProps } from "recharts/types/component/Tooltip";
import type { DistrictDataPoint } from "@/types/dashboard";

interface DistrictChartProps {
  data: DistrictDataPoint[];
  loading?: boolean;
  error?: string;
  onRetry?: () => void;
}

const CustomTooltip = ({ active, payload }: TooltipContentProps) => {
  if (active && payload && payload.length) {
    const dataPoint = payload[0].payload as DistrictDataPoint;
    const rawValue = payload[0].value;
    const displayValue = Array.isArray(rawValue) ? rawValue.join(', ') : String(rawValue ?? '');
    return (
      <div className="bg-[#0f172a] border border-[#1e293b] p-3 rounded-lg shadow-xl">
        <p className="text-[10px] uppercase tracking-wider font-bold text-slate-500">
          District
        </p>
        <p className="text-xs font-bold text-slate-200 mt-0.5 truncate max-w-[180px]">
          {dataPoint.district}
        </p>
        <p className="text-sm font-extrabold text-cyan-400 mt-1">
          {displayValue} <span className="text-xs text-slate-400 font-medium">crimes</span>
        </p>
      </div>
    );
  }
  return null;
};

export default function DistrictChart({
  data,
  loading = false,
  error,
  onRetry,
}: DistrictChartProps) {
  const renderHeader = () => (
    <div className="flex items-center gap-2 mb-5">
      <div className="w-1 h-5 bg-indigo-500 rounded" />
      <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
        Top 10 Districts by Crime Volume
      </h3>
    </div>
  );

  if (loading) {
    // Show 10 animated skeleton bars
    const skeletonWidths = [
      "w-[95%]",
      "w-[85%]",
      "w-[80%]",
      "w-[75%]",
      "w-[70%]",
      "w-[60%]",
      "w-[55%]",
      "w-[45%]",
      "w-[40%]",
      "w-[25%]",
    ];

    return (
      <div className="glass-card p-6 rounded-2xl border border-slate-800/60 h-[420px] flex flex-col">
        {renderHeader()}
        <div className="flex-1 flex flex-col justify-between h-[350px] py-1">
          {skeletonWidths.map((w, idx) => (
            <div key={idx} className="flex items-center gap-4">
              <div className="w-24 h-3 bg-slate-800/50 rounded animate-pulse" />
              <div className={`${w} h-5 bg-slate-800/30 rounded animate-pulse`} />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass-card p-6 rounded-2xl border border-slate-800/60 h-[420px] flex flex-col">
        {renderHeader()}
        <div className="flex-1 flex flex-col items-center justify-center border border-dashed border-red-500/20 rounded-xl bg-red-500/5 p-6 text-center">
          <AlertCircle className="w-8 h-8 text-red-500 mb-3 animate-pulse" />
          <p className="text-xs text-slate-300 max-w-sm mb-4">
            {error || "Failed to load district ranking. Please try again."}
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

  // Slice to 10 max
  const chartData = data.slice(0, 10);

  return (
    <div className="glass-card p-6 rounded-2xl border border-slate-800/60 h-[420px] flex flex-col">
      {renderHeader()}
      <div className="flex-1 min-h-0">
        <ResponsiveContainer width="100%" height={330}>
          <BarChart
            data={chartData}
            layout="vertical"
            margin={{ top: 5, right: 10, left: -5, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
            <XAxis
              type="number"
              tick={{ fill: "#94a3b8", fontSize: 10 }}
              tickLine={false}
              axisLine={false}
            />
            <YAxis
              type="category"
              dataKey="district"
              tick={{ fill: "#94a3b8", fontSize: 10 }}
              tickLine={false}
              axisLine={false}
              width={100}
            />
            <Tooltip content={CustomTooltip} cursor={{ fill: "rgba(30, 41, 59, 0.2)" }} />
            <Bar
              dataKey="count"
              fill="#22d3ee"
              radius={[0, 4, 4, 0]}
              barSize={16}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
