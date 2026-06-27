"use client";

import React, { useState, useEffect } from "react";
import { BrainCircuit, Activity, ShieldAlert } from "lucide-react";
import RepeatOffenderCard from "@/components/prediction/repeat-offender-card";
import CrimeRiskCard from "@/components/prediction/crime-risk-card";
import CrimeTypeCard from "@/components/prediction/crime-type-card";
import HotspotCard from "@/components/prediction/hotspot-card";
import SHAPExplanation from "@/components/prediction/shap-explanation";
import { fetchPredictionHealth } from "@/services/prediction.service";
import type { SHAPImpact } from "@/types/prediction";

export default function PredictionPage() {
  const [activeModel, setActiveModel] = useState<string | null>(null);
  const [shapExplanations, setShapExplanations] = useState<SHAPImpact[]>([]);
  const [shapLoading, setShapLoading] = useState(false);
  const [engineHealth, setEngineHealth] = useState<"healthy" | "degraded" | "loading">("loading");

  useEffect(() => {
    async function verifyHealth() {
      try {
        const health = await fetchPredictionHealth();
        setEngineHealth(health.status === "healthy" ? "healthy" : "degraded");
      } catch {
        setEngineHealth("degraded");
      }
    }
    verifyHealth();
  }, []);

  const handlePredictionSuccess = (type: string, _result: unknown, shap: SHAPImpact[]) => {
    setShapExplanations(shap);
    setShapLoading(false);
  };

  const handleSelectModel = (type: string) => {
    setActiveModel(type);
    setShapLoading(true);
  };

  return (
    <div className="min-h-screen py-8 px-4 sm:px-6 lg:px-8 space-y-8 animate-fade-in relative">
      {/* Background ambient lighting glows */}
      <div className="absolute top-[20%] right-[10%] w-[400px] h-[400px] rounded-full bg-indigo-500/5 blur-[100px] pointer-events-none" />
      <div className="absolute bottom-[20%] left-[5%] w-[350px] h-[350px] rounded-full bg-violet-500/5 blur-[90px] pointer-events-none" />

      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-900 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-indigo-500/10 border border-indigo-500/20 rounded-2xl">
              <BrainCircuit className="w-6 h-6 text-indigo-400" />
            </div>
            <div>
              <h1 className="text-3xl font-black text-slate-100 uppercase tracking-tight">
                Predictive Intelligence
              </h1>
              <p className="text-slate-400 text-xs font-semibold uppercase tracking-widest mt-1">
                Risk & Recidivism Forecaster
              </p>
            </div>
          </div>
          <p className="text-slate-400 text-sm mt-3 max-w-2xl leading-relaxed">
            Employ advanced machine learning classifiers and attribution engines to predict criminal repeat offenses, occurrence risk ratings, spatial hotspots, and future incident types.
          </p>
        </div>

        {/* Engine status indicator */}
        <div className="flex items-center gap-2.5 px-4 py-2.5 bg-slate-950/60 border border-slate-800 rounded-2xl w-fit">
          <Activity className={`w-4 h-4 ${engineHealth === "healthy" ? "text-green-400 animate-pulse" : engineHealth === "loading" ? "text-indigo-400 animate-spin" : "text-red-400"}`} />
          <div className="text-left">
            <span className="text-[9px] font-bold text-slate-500 block uppercase tracking-wider">Predictive Engine Status</span>
            <span className="text-xs font-extrabold text-slate-300 block uppercase tracking-wide">
              {engineHealth === "healthy" ? "Active" : engineHealth === "loading" ? "Initializing..." : "Degraded (Models Missing)"}
            </span>
          </div>
        </div>
      </div>

      {engineHealth === "degraded" && (
        <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-3xl text-red-400 text-sm flex gap-3 items-start max-w-4xl">
          <ShieldAlert className="w-5 h-5 shrink-0 mt-0.5" />
          <div>
            <h4 className="font-bold uppercase tracking-wide text-red-500">Models Not Pre-trained or Missing</h4>
            <p className="text-xs text-slate-400 mt-1 leading-relaxed">
              The application backend cannot locate the trained XGBoost model files in `ml/`. Please run the model training scripts to generate the `.pkl` files before running queries:
            </p>
            <code className="block mt-2 px-3 py-1.5 bg-slate-950/80 rounded-lg text-xs font-mono text-indigo-400 w-fit">
              PYTHONPATH=. .venv/bin/python ml/offender_prediction/train.py
            </code>
          </div>
        </div>
      )}

      {/* 2-Column Responsive Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Predictors List */}
        <div className="lg:col-span-7 space-y-8">
          <div className="grid grid-cols-1 md:grid-cols-1 gap-8">
            <RepeatOffenderCard
              isActive={activeModel === "repeat-offender"}
              onSelect={() => handleSelectModel("repeat-offender")}
              onSuccess={(res, shap) => handlePredictionSuccess("repeat-offender", res, shap)}
            />

            <CrimeRiskCard
              isActive={activeModel === "crime-risk"}
              onSelect={() => handleSelectModel("crime-risk")}
              onSuccess={(res, shap) => handlePredictionSuccess("crime-risk", res, shap)}
            />

            <CrimeTypeCard
              isActive={activeModel === "crime-type"}
              onSelect={() => handleSelectModel("crime-type")}
              onSuccess={(res, shap) => handlePredictionSuccess("crime-type", res, shap)}
            />

            <HotspotCard
              isActive={activeModel === "hotspot"}
              onSelect={() => handleSelectModel("hotspot")}
              onSuccess={(res, shap) => handlePredictionSuccess("hotspot", res, shap)}
            />
          </div>
        </div>

        {/* Right Column: SHAP Explainer */}
        <div className="lg:col-span-5 lg:sticky lg:top-8">
          <SHAPExplanation
            explanations={shapExplanations}
            loading={shapLoading}
            predictionType={activeModel || undefined}
          />
        </div>
      </div>

      {/* Footer System Grid Logs */}
      <div className="pt-6 mt-4 border-t border-slate-900/60 flex justify-between items-center text-[9px] font-mono text-slate-700/60 tracking-widest select-none">
        <span>SECURE PREDICTIVE INTELLIGENCE PLATFORM</span>
        <span>PHASE 5 ENGINE ACTIVE</span>
      </div>
    </div>
  );
}
