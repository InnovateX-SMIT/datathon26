import React from "react";
import type { Recommendation } from "../types/report";
import { AlertCircle, CheckCircle, Clock } from "lucide-react";

interface Props {
  recommendations: Recommendation[];
}

export default function ReportRecommendationsSection({ recommendations }: Props) {
  const getPriorityBadgeClass = (priority: string) => {
    switch (priority.toLowerCase()) {
      case "high":
        return "bg-red-500/10 border-red-500/25 text-red-400";
      case "medium":
        return "bg-amber-500/10 border-amber-500/25 text-amber-400";
      default:
        return "bg-indigo-500/10 border-indigo-500/25 text-indigo-400";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case "resolved":
      case "implemented":
        return <CheckCircle className="w-4 h-4 text-emerald-500" />;
      case "pending":
      default:
        return <Clock className="w-4 h-4 text-slate-500" />;
    }
  };

  return (
    <div className="glass-card p-6 rounded-2xl border border-slate-800/60 animate-fade-in">
      <div className="flex items-center gap-2 mb-5">
        <div className="w-1 h-5 bg-emerald-500 rounded" />
        <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
          Decision Support — Strategic Recommendations
        </h3>
      </div>

      {recommendations.length === 0 ? (
        <div className="flex flex-col items-center justify-center p-8 border border-dashed border-slate-800 rounded-xl bg-slate-900/25 text-center">
          <AlertCircle className="w-8 h-8 text-slate-600 mb-2" />
          <p className="text-xs text-slate-500">No strategic recommendations aggregated for this dossier.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 report-recommendations-grid">
          {recommendations.map((rec, idx) => (
            <div
              key={idx}
              className="p-4 bg-slate-950/40 border border-slate-900 rounded-xl flex flex-col justify-between hover:border-slate-800 transition-all duration-200"
            >
              <div>
                <div className="flex items-center justify-between gap-2">
                  <span className={`px-2 py-0.5 rounded text-[9px] font-bold border uppercase ${getPriorityBadgeClass(rec.priority)}`}>
                    {rec.priority} Priority
                  </span>
                  <div className="flex items-center gap-1 text-[10px] text-slate-500 font-semibold uppercase">
                    {getStatusIcon(rec.status)}
                    {rec.status}
                  </div>
                </div>
                
                <h4 className="text-xs font-bold text-slate-200 mt-3 leading-relaxed">
                  {rec.recommendation_text}
                </h4>
                
                <p className="text-[11px] text-slate-400 mt-2 leading-relaxed bg-slate-950/60 p-2.5 rounded border border-slate-900/80">
                  <span className="text-[9px] font-bold text-slate-500 block uppercase tracking-wider mb-1">Reason / Trigger</span>
                  {rec.reason}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
