"use client";

import React, { useState, useEffect } from "react";
import { UserCheck, AlertTriangle, ShieldCheck, Activity, RefreshCw, Cpu } from "lucide-react";
import {
  predictRecidivism,
  OffenderRecidivismRequest,
  OffenderRecidivismResponse,
} from "@/services/predictionService";

export default function RepeatOffenderPredictionCard() {
  const [inputs, setInputs] = useState<OffenderRecidivismRequest>({
    age_years: 25,
    gender_id: 1,
    district_id: 11,
    police_station_id: 17,
    initial_gravity_offence_id: 2,
    initial_crime_major_head_id: 2,
    initial_crime_minor_head_id: 12,
    initial_hour_of_day: 19,
    initial_day_of_week: 6,
    initial_month: 12,
    initial_is_weekend: 1,
    initial_is_night_time: 0,
    initial_co_offender_count: 3,
  });

  const [prediction, setPrediction] = useState<OffenderRecidivismResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const runPrediction = async (payload: OffenderRecidivismRequest, signal?: AbortSignal) => {
    setLoading(true);
    setError(null);
    try {
      const res = await predictRecidivism(payload, signal);
      setPrediction(res);
    } catch (err: any) {
      if (err.name !== "CanceledError" && err.name !== "AbortError") {
        console.error("Recidivism Prediction API failed:", err);
        setError("Failed to communicate with QuickML Recidivism Endpoint.");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const controller = new AbortController();
    runPrediction(inputs, controller.signal);
    return () => controller.abort();
  }, []);

  const handleInputChange = (field: keyof OffenderRecidivismRequest, value: number) => {
    const updated = { ...inputs, [field]: value };
    setInputs(updated);
    runPrediction(updated);
  };

  const isRepeat = prediction?.recidivism_flag === "REPEAT_OFFENDER";
  const confidencePct = Math.round((prediction?.confidence ?? 0.85) * 100);

  return (
    <div className="glass-card p-6 rounded-2xl border border-purple-500/30 bg-slate-900/60 backdrop-blur-xl mb-6 relative overflow-hidden font-sans">
      {/* Glow highlight effect */}
      <div className="absolute -right-10 -top-10 w-44 h-44 bg-purple-500/10 rounded-full blur-3xl pointer-events-none" />

      {/* Header Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-4 pb-3 border-b border-slate-800/80">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-purple-500/15 border border-purple-500/30 rounded-xl">
            <UserCheck className="w-5 h-5 text-purple-400 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-semibold text-lg text-slate-100">
                Repeat Offender Recidivism Prediction
              </h3>
              <span className="px-2 py-0.5 text-[10px] font-medium bg-purple-500/20 text-purple-300 border border-purple-500/40 rounded-md uppercase tracking-wider">
                Pipeline 3 (QuickML CatBoost)
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Genuine AI Recidivism Risk Assessment & Model-Native Feature Explanations
            </p>
          </div>
        </div>

        <button
          onClick={() => runPrediction(inputs)}
          disabled={loading}
          className="flex items-center gap-2 px-3 py-1.5 bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 text-xs font-medium rounded-lg border border-purple-500/30 transition-all disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
          Recalculate
        </button>
      </div>

      {/* Quick Interactive Inputs Panel */}
      <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-3 mb-5 p-3.5 bg-slate-950/40 rounded-xl border border-slate-800/60">
        <div>
          <label className="block text-[11px] font-medium text-slate-400 mb-1">Age (Years)</label>
          <input
            type="number"
            min={18}
            max={90}
            value={inputs.age_years}
            onChange={(e) => handleInputChange("age_years", parseInt(e.target.value) || 25)}
            className="w-full bg-slate-900 border border-slate-700/80 rounded-lg px-2.5 py-1 text-xs text-slate-200 focus:outline-none focus:border-purple-500/60"
          />
        </div>

        <div>
          <label className="block text-[11px] font-medium text-slate-400 mb-1">Offence Gravity</label>
          <select
            value={inputs.initial_gravity_offence_id}
            onChange={(e) => handleInputChange("initial_gravity_offence_id", parseInt(e.target.value))}
            className="w-full bg-slate-900 border border-slate-700/80 rounded-lg px-2.5 py-1 text-xs text-slate-200 focus:outline-none focus:border-purple-500/60"
          >
            <option value={1}>Non-Grave (1)</option>
            <option value={2}>Grave / Heinous (2)</option>
          </select>
        </div>

        <div>
          <label className="block text-[11px] font-medium text-slate-400 mb-1">Incident Hour</label>
          <input
            type="number"
            min={0}
            max={23}
            value={inputs.initial_hour_of_day}
            onChange={(e) => handleInputChange("initial_hour_of_day", parseInt(e.target.value) || 0)}
            className="w-full bg-slate-900 border border-slate-700/80 rounded-lg px-2.5 py-1 text-xs text-slate-200 focus:outline-none focus:border-purple-500/60"
          />
        </div>

        <div>
          <label className="block text-[11px] font-medium text-slate-400 mb-1">Co-Offenders</label>
          <input
            type="number"
            min={1}
            max={10}
            value={inputs.initial_co_offender_count}
            onChange={(e) => handleInputChange("initial_co_offender_count", parseInt(e.target.value) || 1)}
            className="w-full bg-slate-900 border border-slate-700/80 rounded-lg px-2.5 py-1 text-xs text-slate-200 focus:outline-none focus:border-purple-500/60"
          />
        </div>
      </div>

      {/* Main Status Display */}
      {loading ? (
        <div className="py-8 flex flex-col items-center justify-center gap-2">
          <Activity className="w-7 h-7 text-purple-400 animate-spin" />
          <p className="text-xs text-slate-400">Executing QuickML Recidivism Pipeline 3...</p>
        </div>
      ) : error ? (
        <div className="p-4 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-300 text-xs flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0" />
          <span>{error}</span>
        </div>
      ) : prediction ? (
        <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-start">
          {/* Left Column: Result & Confidence Badge */}
          <div className="md:col-span-5 flex flex-col gap-3">
            <div
              className={`p-4 rounded-xl border flex flex-col gap-2 ${
                isRepeat
                  ? "bg-rose-500/10 border-rose-500/30 text-rose-300"
                  : "bg-emerald-500/10 border-emerald-500/30 text-emerald-300"
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold uppercase tracking-wider opacity-80">
                  Recidivism Risk Category
                </span>
                {isRepeat ? (
                  <AlertTriangle className="w-5 h-5 text-rose-400" />
                ) : (
                  <ShieldCheck className="w-5 h-5 text-emerald-400" />
                )}
              </div>

              <div className="text-2xl font-bold tracking-tight">
                {isRepeat ? "REPEAT OFFENDER" : "NON-RECIDIVIST"}
              </div>

              <div className="text-xs opacity-90">
                {isRepeat
                  ? "High probability of subsequent criminal re-offence based on initial incident profile."
                  : "Low probability of subsequent re-offence based on initial incident profile."}
              </div>
            </div>

            {/* Confidence Gauge Box */}
            <div className="p-3.5 bg-slate-950/50 border border-slate-800 rounded-xl">
              <div className="flex justify-between items-center text-xs mb-1.5">
                <span className="text-slate-400 font-medium">QuickML Model Confidence</span>
                <span className="font-semibold text-purple-300">{confidencePct}%</span>
              </div>
              <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-purple-500 to-indigo-400 rounded-full transition-all duration-500"
                  style={{ width: `${confidencePct}%` }}
                />
              </div>
              <div className="mt-2 text-[10px] text-slate-500 flex items-center justify-between">
                <span>Engine: {prediction.source}</span>
                <span>OAuth 2.0 Authenticated</span>
              </div>
            </div>
          </div>

          {/* Right Column: Native QuickML XAI Feature Contributions */}
          <div className="md:col-span-7 bg-slate-950/40 p-4 rounded-xl border border-slate-800/80">
            <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-3 flex items-center justify-between">
              <span>Top Model Feature Contributions (XAI)</span>
              <span className="text-[10px] text-purple-400 font-normal">Native Model Explainer</span>
            </h4>

            <div className="space-y-2.5">
              {prediction.top_contributing_factors && prediction.top_contributing_factors.length > 0 ? (
                prediction.top_contributing_factors.map((f, i) => {
                  const absWeight = Math.abs(f.weight);
                  const isPositive = f.weight >= 0;
                  const barWidth = Math.min(100, Math.max(10, Math.round(absWeight * 80)));
                  return (
                    <div key={i} className="text-xs">
                      <div className="flex justify-between text-slate-300 mb-1">
                        <span className="font-mono text-[11px] text-slate-400">
                          {f.factor}
                          {f.value !== undefined ? ` = ${f.value}` : ""}
                        </span>
                        <span
                          className={`font-semibold ${
                            isPositive ? "text-emerald-400" : "text-amber-400"
                          }`}
                        >
                          {isPositive ? `+${f.weight.toFixed(4)}` : f.weight.toFixed(4)}
                        </span>
                      </div>
                      <div className="w-full h-1.5 bg-slate-800/80 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all ${
                            isPositive ? "bg-emerald-500" : "bg-amber-500"
                          }`}
                          style={{ width: `${barWidth}%` }}
                        />
                      </div>
                    </div>
                  );
                })
              ) : (
                <p className="text-xs text-slate-500">No feature contribution factors available.</p>
              )}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
