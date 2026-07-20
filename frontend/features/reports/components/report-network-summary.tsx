import React from "react";
import type { NetworkInsights } from "../types/report";
import { Network, Users, UserMinus, ShieldAlert } from "lucide-react";

interface Props {
  insights: NetworkInsights;
}

export default function ReportNetworkSummary({ insights }: Props) {
  const getEntityTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case "criminal":
        return "bg-rose-500/10 border-rose-500/20 text-rose-400";
      case "crime":
        return "bg-amber-500/10 border-amber-500/20 text-amber-400";
      default:
        return "bg-indigo-500/10 border-indigo-500/20 text-indigo-400";
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-fade-in report-network-grid">
      {/* Network Stats Cards */}
      <div className="lg:col-span-1 flex flex-col gap-4">
        {/* Total Cluster count */}
        <div className="glass-card p-5 rounded-2xl border border-slate-800/80 flex items-center gap-4 relative overflow-hidden">
          <div className="bg-indigo-500/10 border border-indigo-500/20 p-3 rounded-xl text-indigo-400">
            <Network className="w-5 h-5" />
          </div>
          <div>
            <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Identified Gang Clusters</p>
            <p className="text-2xl font-black text-white mt-0.5">{insights.total_networks}</p>
          </div>
        </div>

        {/* Largest Cluster size */}
        <div className="glass-card p-5 rounded-2xl border border-slate-800/80 flex items-center gap-4 relative overflow-hidden">
          <div className="bg-rose-500/10 border border-rose-500/20 p-3 rounded-xl text-rose-400">
            <Users className="w-5 h-5" />
          </div>
          <div>
            <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Largest Network Component</p>
            <p className="text-2xl font-black text-white mt-0.5">
              {insights.largest_network_size} <span className="text-xs text-slate-500 font-semibold">nodes</span>
            </p>
          </div>
        </div>
      </div>

      {/* Key Central entities */}
      <div className="lg:col-span-2 glass-card p-6 rounded-2xl border border-slate-800/60">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-1 h-5 bg-rose-500 rounded" />
          <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
            Network Key Influencers (Centrality)
          </h3>
        </div>

        {insights.key_entities.length === 0 ? (
          <div className="flex flex-col items-center justify-center p-8 border border-dashed border-slate-800 rounded-xl bg-slate-900/25">
            <UserMinus className="w-8 h-8 text-slate-600 mb-2" />
            <p className="text-xs text-slate-500">No key central entities found.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider">
                  <th className="py-2 px-3">Entity Name</th>
                  <th className="py-2 px-3 text-center">Type</th>
                  <th className="py-2 px-3 text-right">Centrality Score</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/40 text-slate-300">
                {insights.key_entities.map((entity, idx) => (
                  <tr key={idx} className="hover:bg-slate-900/35 transition-colors">
                    <td className="py-2.5 px-3 font-semibold text-slate-200 flex items-center gap-1.5">
                      {entity.type.toLowerCase() === "criminal" && <ShieldAlert className="w-3.5 h-3.5 text-rose-500" />}
                      {entity.label}
                    </td>
                    <td className="py-2.5 px-3 text-center">
                      <span className={`inline-block px-2 py-0.5 rounded text-[9px] font-bold border uppercase ${getEntityTypeColor(entity.type)}`}>
                        {entity.type}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-right font-mono font-bold text-rose-400">
                      {entity.score.toFixed(4)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
