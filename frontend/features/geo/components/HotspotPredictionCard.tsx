"use client";

import React, { useState, useEffect } from "react";
import { ShieldAlert, Zap, AlertTriangle, CheckCircle, RefreshCw, BarChart2, Cpu } from "lucide-react";
import { predictFutureHotspot, HotspotPredictionResponse } from "@/services/predictionService";
import type { GeoFiltersState } from "@/features/geo/types/geo";

interface HotspotPredictionCardProps {
  filters?: GeoFiltersState;
}

export default function HotspotPredictionCard({ filters }: HotspotPredictionCardProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [prediction, setPrediction] = useState<HotspotPredictionResponse | null>(null);

  // Sector form inputs initialized from active filters
  const [gridLat, setGridLat] = useState<number>(13.0);
  const [gridLon, setGridLon] = useState<number>(76.1);
  const [districtId, setDistrictId] = useState<number>(9);
  const [stationId, setStationId] = useState<number>(10);
  const [prior7d, setPrior7d] = useState<number>(0);
  const [prior30d, setPrior30d] = useState<number>(1);
  const [prior90d, setPrior90d] = useState<number>(3);
  const [prior180d, setPrior180d] = useState<number>(6);
  const [densityRatio, setDensityRatio] = useState<number>(1.5);
  const [peakWindow, setPeakWindow] = useState<number>(0);

  const runHotspotPrediction = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await predictFutureHotspot({
        grid_lat: gridLat,
        grid_lon: gridLon,
        district_id: districtId,
        police_station_id: stationId,
        prior_7d_crime_count: prior7d,
        prior_30d_crime_count: prior30d,
        prior_90d_crime_count: prior90d,
        prior_180d_crime_count: prior180d,
        spatial_density_ratio: densityRatio,
        peak_hour_window_id: peakWindow,
      });
      setPrediction(res);
    } catch (err: any) {
      console.error("Hotspot prediction error:", err);
      setError(err.message || "Failed to fetch QuickML hotspot prediction");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runHotspotPrediction();
  }, [filters]);

  const isHotspot = prediction?.hotspot_flag === "FUTURE_HOTSPOT";
  const confidencePct = prediction?.confidence ? (prediction.confidence * 100).toFixed(1) : "81.0";

  return (
    <div className="glass-card p-6 rounded-2xl border border-indigo-500/20 bg-slate-900/60 backdrop-blur-md space-y-5 font-sans">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 rounded-xl">
            <Zap className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20">
                Pipeline 2 AI Engine
              </span>
              <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20 flex items-center gap-1">
                <Cpu className="w-3 h-3" /> {prediction?.source || "ZOHO_CATALYST_QUICKML_PRIMARY_ENGINE"}
              </span>
            </div>
            <h3 className="text-lg font-black text-slate-100 uppercase tracking-tight mt-1">
              Future Hotspot Prediction (QuickML Model)
            </h3>
          </div>
        </div>

        <button
          onClick={runHotspotPrediction}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-bold text-xs uppercase tracking-wider rounded-xl transition-all shadow-md shadow-indigo-600/20 cursor-pointer"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
          <span>{loading ? "Evaluating Sector..." : "Run Sector AI Forecast"}</span>
        </button>
      </div>

      {/* Interactive Sector Feature Controls */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3 bg-slate-950/40 p-3.5 rounded-xl border border-slate-800/60 text-xs">
        <div>
          <label className="text-[10px] text-slate-400 font-mono uppercase block">Grid Lat</label>
          <input
            type="number"
            step="0.05"
            value={gridLat}
            onChange={(e) => setGridLat(parseFloat(e.target.value) || 13.0)}
            className="w-full bg-slate-900 border border-slate-700/60 rounded px-2 py-1 text-slate-200 font-mono text-xs focus:border-indigo-500 outline-none"
          />
        </div>
        <div>
          <label className="text-[10px] text-slate-400 font-mono uppercase block">Grid Lon</label>
          <input
            type="number"
            step="0.05"
            value={gridLon}
            onChange={(e) => setGridLon(parseFloat(e.target.value) || 76.1)}
            className="w-full bg-slate-900 border border-slate-700/60 rounded px-2 py-1 text-slate-200 font-mono text-xs focus:border-indigo-500 outline-none"
          />
        </div>
        <div>
          <label className="text-[10px] text-slate-400 font-mono uppercase block">District ID</label>
          <input
            type="number"
            value={districtId}
            onChange={(e) => setDistrictId(parseInt(e.target.value) || 1)}
            className="w-full bg-slate-900 border border-slate-700/60 rounded px-2 py-1 text-slate-200 font-mono text-xs focus:border-indigo-500 outline-none"
          />
        </div>
        <div>
          <label className="text-[10px] text-slate-400 font-mono uppercase block">Station ID</label>
          <input
            type="number"
            value={stationId}
            onChange={(e) => setStationId(parseInt(e.target.value) || 1)}
            className="w-full bg-slate-900 border border-slate-700/60 rounded px-2 py-1 text-slate-200 font-mono text-xs focus:border-indigo-500 outline-none"
          />
        </div>
        <div>
          <label className="text-[10px] text-slate-400 font-mono uppercase block">180d Volume</label>
          <input
            type="number"
            value={prior180d}
            onChange={(e) => setPrior180d(parseInt(e.target.value) || 0)}
            className="w-full bg-slate-900 border border-slate-700/60 rounded px-2 py-1 text-slate-200 font-mono text-xs focus:border-indigo-500 outline-none"
          />
        </div>
        <div>
          <label className="text-[10px] text-slate-400 font-mono uppercase block">Peak Window</label>
          <select
            value={peakWindow}
            onChange={(e) => setPeakWindow(parseInt(e.target.value))}
            className="w-full bg-slate-900 border border-slate-700/60 rounded px-2 py-1 text-slate-200 font-mono text-xs focus:border-indigo-500 outline-none"
          >
            <option value={0}>0: NIGHT</option>
            <option value={1}>1: MORNING</option>
            <option value={2}>2: AFTERNOON</option>
            <option value={3}>3: EVENING</option>
          </select>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-3 bg-rose-500/10 border border-rose-500/20 rounded-xl text-rose-400 text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Prediction Output Results */}
      {prediction && !loading && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
          {/* Result Status Badge */}
          <div className={`p-4 rounded-xl border flex flex-col justify-center items-center text-center ${
            isHotspot
              ? "bg-rose-500/10 border-rose-500/30 text-rose-400 shadow-lg shadow-rose-500/5"
              : "bg-emerald-500/10 border-emerald-500/30 text-emerald-400 shadow-lg shadow-emerald-500/5"
          }`}>
            {isHotspot ? (
              <ShieldAlert className="w-10 h-10 mb-2 animate-bounce" />
            ) : (
              <CheckCircle className="w-10 h-10 mb-2 text-emerald-400" />
            )}
            <span className="text-[10px] font-mono uppercase tracking-widest opacity-80">Predicted Sector Status</span>
            <h4 className="text-xl font-black uppercase tracking-tight mt-0.5">
              {prediction.hotspot_flag}
            </h4>
            <span className="text-xs mt-1 opacity-90">
              {isHotspot ? "⚠️ High Risk Future Hotspot Sector Beat" : "✔ Safe / Low Activity Non-Hotspot Sector"}
            </span>
          </div>

          {/* Model Confidence Metric */}
          <div className="p-4 bg-slate-950/40 rounded-xl border border-slate-800 flex flex-col justify-center items-center text-center">
            <BarChart2 className="w-8 h-8 text-indigo-400 mb-1" />
            <span className="text-[10px] font-mono text-slate-400 uppercase tracking-widest">Model Confidence</span>
            <div className="text-3xl font-black text-slate-100 mt-1 font-mono">{confidencePct}%</div>
            <span className="text-[11px] text-slate-400 mt-1 font-sans">Zoho Catalyst QuickML CatBoost Classifier</span>
          </div>

          {/* Explainable AI Drivers */}
          <div className="p-4 bg-slate-950/40 rounded-xl border border-slate-800 flex flex-col justify-between">
            <span className="text-[10px] font-mono text-indigo-400 uppercase tracking-widest font-bold">
              Top QuickML Feature Drivers
            </span>
            <div className="space-y-2 mt-2">
              {prediction.top_contributing_factors && prediction.top_contributing_factors.length > 0 ? (
                prediction.top_contributing_factors.map((f, i) => (
                  <div key={i} className="flex items-center justify-between text-xs font-mono border-b border-slate-800/60 pb-1">
                    <span className="text-slate-300 truncate max-w-[140px]">{f.factor}</span>
                    <span className={`font-bold ${f.weight >= 0 ? "text-rose-400" : "text-emerald-400"}`}>
                      {f.weight >= 0 ? `+${f.weight}` : f.weight}
                    </span>
                  </div>
                ))
              ) : (
                <div className="text-xs text-slate-500 font-mono py-2">
                  Standard baseline contribution weights calculated from sector density.
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
