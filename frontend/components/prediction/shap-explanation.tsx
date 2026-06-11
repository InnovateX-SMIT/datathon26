import React from "react";
import type { SHAPImpact } from "@/types/prediction";
import { Info, HelpCircle } from "lucide-react";

interface SHAPExplanationProps {
  explanations: SHAPImpact[];
  loading?: boolean;
  predictionType?: string;
}

export default function SHAPExplanation({
  explanations,
  loading = false,
  predictionType,
}: SHAPExplanationProps) {
  if (loading) {
    return (
      <div className="glass-card p-6 rounded-3xl border border-slate-800/60 h-full flex flex-col justify-center items-center min-h-[300px]">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-indigo-500 border-r-2 border-transparent" />
        <p className="text-xs text-slate-400 font-bold uppercase tracking-wider mt-4 animate-pulse">
          Computing SHAP values...
        </p>
      </div>
    );
  }

  if (explanations.length === 0) {
    return (
      <div className="glass-card p-8 rounded-3xl border border-slate-800/60 h-full flex flex-col justify-center items-center min-h-[300px] text-center">
        <div className="p-3 bg-indigo-500/10 border border-indigo-500/20 rounded-2xl mb-4 text-indigo-400">
          <HelpCircle className="w-8 h-8 animate-pulse" />
        </div>
        <h3 className="text-base font-extrabold text-slate-200 uppercase tracking-wider">
          No Prediction Selected
        </h3>
        <p className="text-xs text-slate-400 leading-relaxed max-w-xs mt-2 font-medium">
          Submit any prediction request above to analyze the underlying decision factors and feature contributions.
        </p>
      </div>
    );
  }

  // Find maximum absolute impact to scale bar widths
  const maxImpact = Math.max(...explanations.map((exp) => Math.abs(exp.impact)), 0.01);

  return (
    <div className="glass-card p-6 rounded-3xl border border-slate-800/60 h-full relative overflow-hidden transition-all duration-300">
      <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-indigo-500/20 to-transparent" />

      {/* Header */}
      <div className="flex items-start justify-between border-b border-slate-800/50 pb-4 mb-5">
        <div>
          <h3 className="text-lg font-bold text-slate-100 uppercase tracking-tight flex items-center gap-2">
            Decision Factor Attribution
            <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest px-2.5 py-0.5 bg-indigo-500/10 border border-indigo-500/20 rounded-full">
              SHAP Explainer
            </span>
          </h3>
          <p className="text-xs text-slate-400 font-medium mt-1">
            Analyzing tree-path contributions for: <span className="text-indigo-400 font-bold uppercase">{predictionType?.replace("-", " ")}</span>
          </p>
        </div>
      </div>

      {/* Bar List */}
      <div className="flex flex-col gap-4 max-h-[420px] overflow-y-auto pr-1">
        {explanations.map((item, idx) => {
          const isPositive = item.impact >= 0;
          const absVal = Math.abs(item.impact);
          const percentWidth = Math.min((absVal / maxImpact) * 100, 100);

          return (
            <div key={idx} className="flex flex-col gap-1.5 group">
              <div className="flex justify-between items-center text-xs">
                <span className="font-mono font-bold text-slate-300 truncate max-w-[200px]">
                  {item.feature}
                </span>
                <span className={`font-mono font-bold ${isPositive ? "text-red-400" : "text-sky-400"}`}>
                  {isPositive ? "+" : ""}
                  {item.impact.toFixed(4)}
                </span>
              </div>

              {/* Progress track */}
              <div className="w-full h-3 bg-slate-950/80 rounded-full overflow-hidden border border-slate-900/60 flex relative">
                {/* Visual grid divider */}
                <div className="absolute left-1/2 top-0 bottom-0 w-[1px] bg-slate-800/60 pointer-events-none" />

                {/* Left/Right oriented bars representing impact */}
                <div
                  className="h-full absolute transition-all duration-500 ease-out"
                  style={{
                    left: isPositive ? "50%" : "auto",
                    right: isPositive ? "auto" : "50%",
                    width: `${percentWidth / 2}%`,
                    background: isPositive
                      ? "linear-gradient(to right, rgba(239, 68, 68, 0.4), rgba(239, 68, 68, 0.95))"
                      : "linear-gradient(to left, rgba(56, 189, 248, 0.4), rgba(56, 189, 248, 0.95))",
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* Legend & Guide */}
      <div className="mt-6 pt-4 border-t border-slate-800/50 flex flex-wrap gap-4 items-center justify-between text-[10px] text-slate-400 font-bold uppercase tracking-wider">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 rounded bg-red-500" />
            <span>Increases Risk (+)</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 rounded bg-sky-500" />
            <span>Decreases Risk (-)</span>
          </div>
        </div>
        <div className="flex items-center gap-1 text-[9px] font-mono text-slate-500">
          <Info className="w-3.5 h-3.5 text-slate-500" />
          <span>SHAP TreeExplainer Local Attribution</span>
        </div>
      </div>
    </div>
  );
}
