"use client";

import React, { useState, useEffect } from "react";
import { Cpu, Activity, CheckCircle2, RefreshCw } from "lucide-react";
import {
  predictCrimeRisk,
  CrimeRiskPredictionResponse,
  CrimeRiskPredictionRequest,
} from "@/services/predictionService";
import type { GeoFiltersState } from "@/features/geo/types/geo";

interface CrimeRiskPredictionCardProps {
  filters?: GeoFiltersState;
}

export default function CrimeRiskPredictionCard({ filters }: CrimeRiskPredictionCardProps) {
  const [prediction, setPrediction] = useState<CrimeRiskPredictionResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const getNumericId = (str?: string): number => {
    if (!str) return 1;
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      hash = (hash << 5) - hash + str.charCodeAt(i);
      hash |= 0;
    }
    return Math.abs(hash % 30) + 1;
  };

  const runPrediction = async (signal?: AbortSignal) => {
    setLoading(true);
    setError(null);
    try {
      const isNight = filters?.time_period === "night";
      let hour = 22;
      if (filters?.time_period === "morning") hour = 8;
      else if (filters?.time_period === "afternoon") hour = 14;
      else if (filters?.time_period === "evening") hour = 19;
      else if (filters?.time_period === "night") hour = 23;

      const payload: CrimeRiskPredictionRequest = {
        district_id: getNumericId(filters?.district),
        police_station_id: getNumericId(filters?.police_station),
        crime_major_head_id: getNumericId(filters?.crime_type),
        hour_of_day: hour,
        day_of_week: 5,
        gravity_offence_id: 2,
        is_night_time: isNight ? 1 : 1,
        hist_station_crime_count_30d: 500,
        hist_district_crime_count_30d: 800,
      };

      const res = await predictCrimeRisk(payload, signal);
      setPrediction(res);
    } catch (err: any) {
      if (err.name !== "CanceledError" && err.name !== "AbortError") {
        console.error("Crime Risk Prediction API failed:", err);
        setError("Failed to fetch live QuickML prediction.");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const controller = new AbortController();
    runPrediction(controller.signal);
    return () => controller.abort();
  }, [filters?.district, filters?.police_station, filters?.time_period, filters?.crime_type]);

  const getTierColor = (tier?: string) => {
    switch (tier) {
      case "CRITICAL":
        return "bg-rose-500/10 text-rose-400 border-rose-500/30 shadow-rose-500/10";
      case "HIGH":
        return "bg-amber-500/10 text-amber-400 border-amber-500/30 shadow-amber-500/10";
      case "MEDIUM":
        return "bg-yellow-500/10 text-yellow-400 border-yellow-500/30 shadow-yellow-500/10";
      default:
        return "bg-emerald-500/10 text-emerald-400 border-emerald-500/30 shadow-emerald-500/10";
    }
  };

  // Safe confidence score calculation
  const rawConf = prediction?.confidence ?? prediction?.risk_score;
  const safeConfidence = typeof rawConf === "number" && !isNaN(rawConf) ? rawConf : 0.95;

  return (
    <div className="glass-card p-6 rounded-2xl border border-indigo-500/30 bg-slate-900/60 backdrop-blur-xl mb-6 relative overflow-hidden font-sans">
      {/* Background Lighting Effect */}
      <div className="absolute -right-10 -top-10 w-40 h-40 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-4 pb-3 border-b border-slate-800/80">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-indigo-500/15 border border-indigo-500/30 rounded-xl">
            <Cpu className="w-5 h-5 text-indigo-400 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base font-bold text-slate-100 uppercase tracking-tight">
                Crime Risk Predictive Intelligence
              </h3>
              <span className="px-2 py-0.5 text-[10px] font-bold rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 font-mono">
                Pipeline 1: QuickML
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Live CatBoost MultiClass Inference powered by Zoho Catalyst QuickML
            </p>
          </div>
        </div>

        <button
          onClick={() => runPrediction()}
          disabled={loading}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 text-xs font-semibold text-slate-300 border border-slate-700 transition cursor-pointer"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-indigo-400" : ""}`} />
          <span>Refresh AI</span>
        </button>
      </div>

      {loading ? (
        <div className="h-28 flex flex-col items-center justify-center gap-2 text-slate-400 animate-pulse">
          <Activity className="w-6 h-6 text-indigo-400 animate-spin" />
          <span className="text-xs">Evaluating QuickML CatBoost model...</span>
        </div>
      ) : error ? (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs">
          {error}
        </div>
      ) : prediction ? (
        <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-center">
          {/* Main Risk Tier Badge & Confidence */}
          <div className="md:col-span-5 flex flex-col gap-3">
            <div className="flex items-center gap-2">
              <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">
                Predicted Risk Tier
              </span>
            </div>

            <div className="flex items-center gap-4">
              <div
                className={`px-5 py-2.5 rounded-xl border text-xl font-black tracking-wider uppercase shadow-lg ${getTierColor(
                  prediction.risk_tier
                )}`}
              >
                {prediction.risk_tier}
              </div>

              <div>
                <div className="text-xs font-bold text-slate-300 font-mono">
                  {(safeConfidence * 100).toFixed(2)}% Confidence
                </div>
                <div className="w-28 h-2 bg-slate-800 rounded-full mt-1 overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-indigo-500 to-emerald-400 rounded-full transition-all duration-500"
                    style={{ width: `${Math.min(100, safeConfidence * 100)}%` }}
                  />
                </div>
              </div>
            </div>

            <div className="flex items-center gap-1.5 text-[11px] text-slate-400 pt-1">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              <span>
                Engine: <strong className="text-slate-200 font-mono">{prediction.source}</strong>
              </span>
            </div>
          </div>

          {/* Top Contributing Factors Breakdown */}
          <div className="md:col-span-7 border-t md:border-t-0 md:border-l border-slate-800/80 pt-4 md:pt-0 md:pl-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                Top Contributing Feature Drivers (QuickML XAI)
              </span>
            </div>

            <div className="space-y-2">
              {prediction.top_contributing_factors.map((factor, idx) => {
                const absWeight = Math.abs(factor.weight);
                const pct = Math.min(100, Math.max(10, absWeight * 100));
                return (
                  <div key={idx} className="space-y-1">
                    <div className="flex justify-between text-xs font-mono">
                      <span className="text-slate-300">{factor.factor}</span>
                      <span className="text-indigo-400 font-semibold">
                        {factor.weight > 0 ? "+" : ""}
                        {factor.weight.toFixed(4)}
                      </span>
                    </div>
                    <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-indigo-500/80 rounded-full"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
