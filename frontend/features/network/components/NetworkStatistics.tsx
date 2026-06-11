import React from "react";
import { NetworkStatistics as StatsType } from "../hooks/useNetworkGraph";
import { Share2, Link as LinkIcon, User, AlertTriangle, MapPin } from "lucide-react";

interface NetworkStatisticsProps {
  statistics: StatsType;
}

export default function NetworkStatistics({ statistics }: NetworkStatisticsProps) {
  const statsList = [
    {
      label: "Total Nodes",
      value: statistics.totalNodes,
      icon: Share2,
      colorClass: "text-indigo-400 bg-indigo-500/10 border-indigo-500/20",
    },
    {
      label: "Total Edges",
      value: statistics.totalEdges,
      icon: LinkIcon,
      colorClass: "text-slate-400 bg-slate-500/10 border-slate-500/20",
    },
    {
      label: "Criminal Nodes",
      value: statistics.criminalNodes,
      icon: User,
      colorClass: "text-blue-400 bg-blue-500/10 border-blue-500/20",
    },
    {
      label: "Crime Event Nodes",
      value: statistics.crimeNodes,
      icon: AlertTriangle,
      colorClass: "text-amber-400 bg-amber-500/10 border-amber-500/20",
    },
    {
      label: "Location Nodes",
      value: statistics.locationNodes,
      icon: MapPin,
      colorClass: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
      {statsList.map((stat, i) => {
        const Icon = stat.icon;
        return (
          <div
            key={i}
            className="glass-card bg-slate-950/40 border border-slate-900 rounded-2xl p-4 shadow-md backdrop-blur-sm flex items-center justify-between"
          >
            <div className="space-y-1">
              <span className="text-[9px] font-bold text-slate-500 uppercase tracking-widest block">
                {stat.label}
              </span>
              <span className="text-xl font-extrabold text-slate-200 block font-mono leading-none">
                {stat.value}
              </span>
            </div>
            <div className={`p-2 rounded-xl border ${stat.colorClass} shrink-0`}>
              <Icon className="w-4 h-4" />
            </div>
          </div>
        );
      })}
    </div>
  );
}
