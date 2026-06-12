import React from "react";
import { ShieldAlert, Compass, User, AlertTriangle, Eye, ShieldCheck } from "lucide-react";
import type { Recommendation } from "@/types/recommendation";

interface MonitoringPanelsProps {
  recommendations: Recommendation[];
}

export default function MonitoringPanels({ recommendations }: MonitoringPanelsProps) {
  // Parse hotspot actions
  const hotspotActions = recommendations.filter(
    (r) =>
      r.status === "pending" &&
      (r.recommendation_text.toLowerCase().includes("hotspot") ||
        r.recommendation_text.toLowerCase().includes("patrol") ||
        r.recommendation_text.toLowerCase().includes("bengaluru"))
  );

  // Parse criminal actions
  const criminalActions = recommendations.filter(
    (r) =>
      r.status === "pending" &&
      (r.recommendation_text.toLowerCase().includes("offender") ||
        r.recommendation_text.toLowerCase().includes("suspect") ||
        r.recommendation_text.toLowerCase().includes("investigation") ||
        r.recommendation_text.toLowerCase().includes("influencer"))
  );

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start animate-fade-in">
      {/* Hotspots Section */}
      <div className="lg:col-span-6 bg-slate-950/40 border border-slate-900/80 rounded-3xl p-6 backdrop-blur-xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-[150px] h-[150px] rounded-full bg-indigo-500/5 blur-[50px] pointer-events-none" />
        
        <div className="flex items-center gap-2 mb-6 border-b border-slate-900 pb-4">
          <Compass className="w-5 h-5 text-indigo-400" />
          <div>
            <h3 className="text-md font-extrabold text-slate-100 uppercase tracking-tight">Hotspot Patrol Directives</h3>
            <p className="text-[9px] text-slate-400 font-semibold uppercase tracking-widest mt-0.5">High-risk locations requiring supervision</p>
          </div>
        </div>

        {hotspotActions.length === 0 ? (
          <div className="py-12 text-center flex flex-col items-center justify-center">
            <ShieldCheck className="w-8 h-8 text-green-500/60 mb-3" />
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">All Locations Secure</h4>
            <p className="text-[10px] text-slate-600 mt-1">No active hotspot patrol directives registered.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {hotspotActions.map((act) => (
              <div
                key={act.id}
                className="bg-slate-950/60 border border-slate-900 rounded-2xl p-4 space-y-3 hover:border-slate-800 transition-all"
              >
                <div className="flex justify-between items-start gap-3">
                  <h4 className="text-xs font-black text-slate-200 uppercase tracking-wide leading-snug">
                    {act.recommendation_text}
                  </h4>
                  <span className="shrink-0 px-2 py-0.5 bg-red-500/10 border border-red-500/20 text-red-400 text-[8px] font-bold rounded uppercase tracking-wider">
                    High Alert
                  </span>
                </div>

                <p className="text-[11px] text-slate-400 font-medium leading-relaxed">
                  {act.reason}
                </p>

                {/* Operations recommendations checklist */}
                <div className="border-t border-slate-900 pt-3 flex flex-wrap gap-x-4 gap-y-2 text-[10px] font-mono text-slate-500">
                  <span className="flex items-center gap-1">
                    <Eye className="w-3.5 h-3.5 text-indigo-400" />
                    Patrol Frequency: <strong className="text-slate-300 font-bold">Hourly</strong>
                  </span>
                  <span className="flex items-center gap-1">
                    <ShieldAlert className="w-3.5 h-3.5 text-indigo-400" />
                    Recommended Vehicles: <strong className="text-slate-300 font-bold">2 Jeeps</strong>
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Suspects Section */}
      <div className="lg:col-span-6 bg-slate-950/40 border border-slate-900/80 rounded-3xl p-6 backdrop-blur-xl relative overflow-hidden">
        <div className="absolute bottom-0 left-0 w-[150px] h-[150px] rounded-full bg-violet-500/5 blur-[50px] pointer-events-none" />

        <div className="flex items-center gap-2 mb-6 border-b border-slate-900 pb-4">
          <User className="w-5 h-5 text-indigo-400" />
          <div>
            <h3 className="text-md font-extrabold text-slate-100 uppercase tracking-tight">Active Suspect Supervision</h3>
            <p className="text-[9px] text-slate-400 font-semibold uppercase tracking-widest mt-0.5">High-recidivism monitoring roster</p>
          </div>
        </div>

        {criminalActions.length === 0 ? (
          <div className="py-12 text-center flex flex-col items-center justify-center">
            <ShieldCheck className="w-8 h-8 text-green-500/60 mb-3" />
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">No Active Supervision</h4>
            <p className="text-[10px] text-slate-600 mt-1">No repeat offenders currently flagged for intensive check-ins.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {criminalActions.map((act) => (
              <div
                key={act.id}
                className="bg-slate-950/60 border border-slate-900 rounded-2xl p-4 space-y-3 hover:border-slate-800 transition-all"
              >
                <div className="flex justify-between items-start gap-3">
                  <h4 className="text-xs font-black text-slate-200 uppercase tracking-wide leading-snug">
                    {act.recommendation_text}
                  </h4>
                  <span className="shrink-0 px-2 py-0.5 bg-yellow-500/10 border border-yellow-500/20 text-yellow-400 text-[8px] font-bold rounded uppercase tracking-wider">
                    Medium Alert
                  </span>
                </div>

                <p className="text-[11px] text-slate-400 font-medium leading-relaxed">
                  {act.reason}
                </p>

                {/* Operations recommendations checklist */}
                <div className="border-t border-slate-900 pt-3 flex flex-wrap gap-x-4 gap-y-2 text-[10px] font-mono text-slate-500">
                  <span className="flex items-center gap-1">
                    <Eye className="w-3.5 h-3.5 text-indigo-400" />
                    Supervision: <strong className="text-slate-300 font-bold">Bi-weekly physical checks</strong>
                  </span>
                  <span className="flex items-center gap-1">
                    <AlertTriangle className="w-3.5 h-3.5 text-indigo-400" />
                    Priority Code: <strong className="text-slate-300 font-bold">CAT-1</strong>
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
