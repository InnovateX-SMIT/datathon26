import React from "react";
import { Bell, ShieldAlert, CheckCircle, Clock } from "lucide-react";
import type { AlertSummary } from "@/types/alert";

interface AlertStatsProps {
  summary: AlertSummary;
  loading: boolean;
}

export default function AlertStats({ summary, loading }: AlertStatsProps) {
  const stats = [
    {
      label: "Active Alerts",
      value: summary.total_active,
      icon: Bell,
      color: "text-indigo-400",
      bg: "bg-indigo-500/10",
      border: "border-indigo-500/20",
      glow: "bg-indigo-500/5",
      desc: "Pending triage or active investigation"
    },
    {
      label: "Critical Anomalies",
      value: summary.critical_count,
      icon: ShieldAlert,
      color: "text-red-400",
      bg: "bg-red-500/10",
      border: "border-red-500/20",
      glow: "bg-red-500/5",
      desc: "Immediate intervention required"
    },
    {
      label: "Resolved Alerts",
      value: summary.resolved_count,
      icon: CheckCircle,
      color: "text-emerald-400",
      bg: "bg-emerald-500/10",
      border: "border-emerald-500/20",
      glow: "bg-emerald-500/5",
      desc: "Successfully closed lifecycle"
    },
    {
      label: "Today's Alerts",
      value: summary.today_count,
      icon: Clock,
      color: "text-amber-400",
      bg: "bg-amber-500/10",
      border: "border-amber-500/20",
      glow: "bg-amber-500/5",
      desc: "Alerts generated in the last 24h"
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 animate-fade-in">
      {stats.map((stat, idx) => {
        const Icon = stat.icon;
        return (
          <div
            key={idx}
            className="bg-slate-950/40 border border-slate-900 rounded-2xl p-6 backdrop-blur-xl relative overflow-hidden group hover:border-slate-800 transition-all duration-300"
          >
            {/* Soft decorative glow */}
            <div className={`absolute top-0 right-0 w-[100px] h-[100px] rounded-full ${stat.glow} blur-[40px] pointer-events-none group-hover:scale-125 transition-transform duration-500`} />
            
            <div className="flex items-center justify-between mb-4">
              <span className="text-[10px] text-slate-400 font-extrabold uppercase tracking-wider">{stat.label}</span>
              <div className={`p-2.5 rounded-xl ${stat.bg} ${stat.border} border ${stat.color} group-hover:scale-110 transition-transform duration-300`}>
                <Icon className="w-4.5 h-4.5" />
              </div>
            </div>

            {loading ? (
              <div className="h-9 w-16 bg-slate-900/60 animate-pulse rounded-lg mb-2" />
            ) : (
              <div className="text-3xl font-black text-slate-100 tracking-tight mb-2">
                {stat.value}
              </div>
            )}

            <p className="text-[10px] text-slate-500 font-medium leading-normal">
              {stat.desc}
            </p>
          </div>
        );
      })}
    </div>
  );
}
