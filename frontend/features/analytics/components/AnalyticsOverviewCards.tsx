import React from "react";
import { Shield, Users, AlertTriangle } from "lucide-react";
import type { OverviewResponse } from "../types/analytics";

interface AnalyticsOverviewCardsProps {
  data: OverviewResponse | null;
  loading?: boolean;
}

export default function AnalyticsOverviewCards({ data, loading }: AnalyticsOverviewCardsProps) {
  const cards = [
    {
      title: "Total Crimes",
      value: data?.total_crimes ?? 0,
      icon: Shield,
      color: "from-blue-500/10 to-indigo-500/10 text-indigo-400 border-indigo-500/20",
      iconBg: "bg-indigo-500/10 text-indigo-400",
      description: "Aggregated incident records"
    },
    {
      title: "Total Victims",
      value: data?.total_victims ?? 0,
      icon: Users,
      color: "from-emerald-500/10 to-teal-500/10 text-emerald-400 border-emerald-500/20",
      iconBg: "bg-emerald-500/10 text-emerald-400",
      description: "Registered victim count"
    },
    {
      title: "Total Accused",
      value: data?.total_accused ?? 0,
      icon: AlertTriangle,
      color: "from-rose-500/10 to-orange-500/10 text-rose-400 border-rose-500/20",
      iconBg: "bg-rose-500/10 text-rose-400",
      description: "Identified suspect profiles"
    }
  ];

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="glass-card p-6 rounded-2xl border border-slate-800/60 animate-pulse flex items-center justify-between h-[120px]">
            <div className="space-y-3">
              <div className="h-4 w-24 bg-slate-800 rounded" />
              <div className="h-8 w-16 bg-slate-800/50 rounded" />
            </div>
            <div className="w-12 h-12 rounded-full bg-slate-800" />
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
      {cards.map((card) => {
        const Icon = card.icon;
        return (
          <div
            key={card.title}
            className={`glass-card p-6 rounded-2xl border bg-gradient-to-br ${card.color} hover:translate-y-[-2px] transition-all duration-300 flex items-center justify-between`}
          >
            <div>
              <p className="text-xs uppercase tracking-wider text-slate-400 font-bold mb-1">
                {card.title}
              </p>
              <h3 className="text-3xl font-extrabold tracking-tight mt-1 text-white">
                {card.value.toLocaleString("en-IN")}
              </h3>
              <p className="text-[10px] text-slate-400 mt-2 font-medium">
                {card.description}
              </p>
            </div>
            <div className={`p-4 rounded-xl ${card.iconBg}`}>
              <Icon className="w-6 h-6" />
            </div>
          </div>
        );
      })}
    </div>
  );
}
