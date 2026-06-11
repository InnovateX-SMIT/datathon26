import React from "react";
import { User, AlertTriangle, MapPin } from "lucide-react";

export default function NetworkLegend() {
  return (
    <div className="glass-card bg-slate-950/70 border border-slate-900 rounded-2xl p-4 flex flex-wrap gap-6 items-center justify-center w-fit mx-auto shadow-lg backdrop-blur-md">
      <span className="text-[10px] font-mono text-slate-500 uppercase tracking-widest border-r border-slate-900 pr-5">
        Graph Legend
      </span>

      {/* Criminal Node Info */}
      <div className="flex items-center gap-2.5">
        <div className="p-1.5 bg-blue-500/10 border border-blue-500/20 rounded-lg">
          <User className="w-3.5 h-3.5 text-blue-400" />
        </div>
        <span className="text-[11px] font-bold text-slate-300 uppercase tracking-wider">Criminal</span>
        <span className="w-1.5 h-1.5 bg-blue-500 rounded-full shadow-[0_0_8px_#3b82f6]" />
      </div>

      {/* Crime Event Node Info */}
      <div className="flex items-center gap-2.5">
        <div className="p-1.5 bg-amber-500/10 border border-amber-500/20 rounded-lg">
          <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
        </div>
        <span className="text-[11px] font-bold text-slate-300 uppercase tracking-wider">Crime Event</span>
        <span className="w-1.5 h-1.5 bg-amber-500 rounded-full shadow-[0_0_8px_#f59e0b]" />
      </div>

      {/* Location Node Info */}
      <div className="flex items-center gap-2.5">
        <div className="p-1.5 bg-emerald-500/10 border border-emerald-500/20 rounded-lg">
          <MapPin className="w-3.5 h-3.5 text-emerald-400" />
        </div>
        <span className="text-[11px] font-bold text-slate-300 uppercase tracking-wider">Location</span>
        <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full shadow-[0_0_8px_#10b981]" />
      </div>
    </div>
  );
}
