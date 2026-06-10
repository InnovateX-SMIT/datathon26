import React from "react";
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";
import type { TooltipContentProps } from "recharts/types/component/Tooltip";
import type { CategoryResponse } from "../types/analytics";

interface CategoryDistributionChartProps {
  data: CategoryResponse | null;
  loading?: boolean;
}

const COLORS = [
  "#6366f1", // Indigo
  "#10b981", // Emerald
  "#f43f5e", // Rose
  "#f59e0b", // Amber
  "#8b5cf6", // Violet
  "#06b6d4", // Cyan
  "#ec4899", // Pink
  "#14b8a6", // Teal
];

const PieTooltip = ({ active, payload }: TooltipContentProps) => {
  if (active && payload && payload.length) {
    const { name, value } = payload[0];
    return (
      <div className="bg-[#0f172a]/95 border border-[#1e293b] p-3 rounded-lg shadow-xl backdrop-blur-md">
        <p className="text-xs font-bold text-slate-200">{name}</p>
        <p className="text-sm font-extrabold text-indigo-400 mt-1">
          {value} <span className="text-xs text-slate-400 font-medium">crimes</span>
        </p>
      </div>
    );
  }
  return null;
};

export default function CategoryDistributionChart({ data, loading }: CategoryDistributionChartProps) {
  const categories = data?.categories ?? [];
  const subcategories = data?.subcategories ?? [];

  if (loading) {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="glass-card p-6 rounded-2xl border border-slate-800/60 h-[380px] animate-pulse flex flex-col justify-between">
          <div className="h-4 w-32 bg-slate-800 rounded" />
          <div className="w-48 h-48 rounded-full bg-slate-800/30 mx-auto" />
          <div className="h-4 w-48 bg-slate-800/30 rounded mx-auto" />
        </div>
        <div className="glass-card p-6 rounded-2xl border border-slate-800/60 h-[380px] animate-pulse flex flex-col justify-between">
          <div className="h-4 w-32 bg-slate-800 rounded" />
          <div className="h-[240px] bg-slate-800/10 rounded-xl w-full" />
        </div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
      {/* Category Pie Chart */}
      <div className="glass-card p-6 rounded-2xl border border-slate-800/60 h-[380px] flex flex-col">
        <div className="flex items-center gap-2 mb-6">
          <div className="w-1 h-5 bg-indigo-500 rounded" />
          <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
            Category Distribution
          </h3>
        </div>
        <div className="flex-1 min-h-0 relative">
          {categories.length === 0 ? (
            <div className="h-full flex items-center justify-center text-slate-400 text-sm">
              No categories data available.
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={categories}
                  cx="50%"
                  cy="45%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={4}
                  dataKey="count"
                >
                  {categories.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip content={PieTooltip} />
                <Legend
                  verticalAlign="bottom"
                  height={36}
                  iconType="circle"
                  iconSize={8}
                  formatter={(value, entry: any) => {
                    const payload = entry.payload;
                    return (
                      <span className="text-[11px] font-medium text-slate-300">
                        {payload.name} ({payload.count})
                      </span>
                    );
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* Subcategory Bar Chart */}
      <div className="glass-card p-6 rounded-2xl border border-slate-800/60 h-[380px] flex flex-col">
        <div className="flex items-center gap-2 mb-6">
          <div className="w-1 h-5 bg-indigo-500 rounded" />
          <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
            Top Subcategories
          </h3>
        </div>
        <div className="flex-1 min-h-0">
          {subcategories.length === 0 ? (
            <div className="h-full flex items-center justify-center text-slate-400 text-sm">
              No subcategories data available.
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={subcategories.slice(0, 8)}
                layout="vertical"
                margin={{ top: 0, right: 10, left: 10, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
                <XAxis type="number" tick={{ fill: "#94a3b8", fontSize: 9 }} tickLine={false} axisLine={false} />
                <YAxis
                  dataKey="name"
                  type="category"
                  tick={{ fill: "#cbd5e1", fontSize: 10 }}
                  tickLine={false}
                  axisLine={false}
                  width={90}
                />
                <Tooltip
                  cursor={{ fill: "rgba(148, 163, 184, 0.05)" }}
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      return (
                        <div className="bg-[#0f172a]/95 border border-[#1e293b] p-3 rounded-lg shadow-xl backdrop-blur-md">
                          <p className="text-xs font-bold text-slate-200">{payload[0].payload.name}</p>
                          <p className="text-sm font-extrabold text-indigo-400 mt-1">
                            {payload[0].value} <span className="text-xs text-slate-400 font-medium">crimes</span>
                          </p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Bar dataKey="count" fill="#3b82f6" radius={[0, 4, 4, 0]}>
                  {subcategories.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[(index + 2) % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </div>
  );
}
