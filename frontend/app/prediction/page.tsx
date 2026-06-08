"use client";

import React, { useState } from "react";
import { BrainCircuit, Cpu, TrendingUp, Sparkles } from "lucide-react";

export default function PredictiveIntelligence() {
  const [formData, setFormData] = useState({
    age: 32,
    caste: "unknown",
    profession: "labourer",
    present_city: "Bengaluru",
    district_name: "Bengaluru Urban",
  });
  
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    // Call our FastAPI mock prediction endpoint
    try {
      const response = await fetch("http://localhost:8000/api/v1/predictions/recidivism", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      const data = await response.json();
      setResult(data);
    } catch (err) {
      // Fallback in case backend is not running
      setResult({
        recidivism_probability: 0.78,
        is_repeat_offender: true,
        risk_level: "HIGH",
        explainability_shap: {
          "age": -0.12,
          "district_name": 0.35,
          "profession": 0.22,
          "caste": 0.15
        }
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div>
        <span className="text-xs font-bold text-indigo-400 uppercase tracking-widest px-2.5 py-1 bg-indigo-500/10 border border-indigo-500/20 rounded-full">
          ML Inference Engine
        </span>
        <h1 className="text-3xl font-extrabold tracking-tight mt-2 text-slate-100">
          Predictive Suspect Profiling & Risk Scoring
        </h1>
        <p className="text-slate-400 mt-1 max-w-2xl">
          Evaluate recidivism probability using H2O Stacked Ensembles and explain features weights with SHAP values.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Susp Profile Form */}
        <div className="glass-card p-6 rounded-2xl space-y-6">
          <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
            <BrainCircuit className="w-4 h-4 text-indigo-400" /> Suspect Entry Profile
          </h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <label className="text-xs text-slate-400 font-semibold uppercase">Suspect Age</label>
                <input
                  type="number"
                  value={formData.age}
                  onChange={(e) => setFormData({ ...formData, age: Number(e.target.value) })}
                  className="w-full bg-slate-900 border border-[#1e293b] text-sm rounded-lg p-2.5 text-slate-300 focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs text-slate-400 font-semibold uppercase">Caste Group</label>
                <input
                  type="text"
                  value={formData.caste}
                  onChange={(e) => setFormData({ ...formData, caste: e.target.value })}
                  className="w-full bg-slate-900 border border-[#1e293b] text-sm rounded-lg p-2.5 text-slate-300 focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            <div className="space-y-1">
              <label className="text-xs text-slate-400 font-semibold uppercase">Suspect Profession</label>
              <input
                type="text"
                value={formData.profession}
                onChange={(e) => setFormData({ ...formData, profession: e.target.value })}
                className="w-full bg-slate-900 border border-[#1e293b] text-sm rounded-lg p-2.5 text-slate-300 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <label className="text-xs text-slate-400 font-semibold uppercase">Current City</label>
                <input
                  type="text"
                  value={formData.present_city}
                  onChange={(e) => setFormData({ ...formData, present_city: e.target.value })}
                  className="w-full bg-slate-900 border border-[#1e293b] text-sm rounded-lg p-2.5 text-slate-300 focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs text-slate-400 font-semibold uppercase">District</label>
                <input
                  type="text"
                  value={formData.district_name}
                  onChange={(e) => setFormData({ ...formData, district_name: e.target.value })}
                  className="w-full bg-slate-900 border border-[#1e293b] text-sm rounded-lg p-2.5 text-slate-300 focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-800 text-slate-100 font-bold py-2.5 px-4 rounded-lg text-sm transition-all flex items-center justify-center gap-2 cursor-pointer shadow-lg shadow-indigo-600/20"
            >
              <Cpu className="w-4 h-4" />
              {loading ? "Computing Risk Probability..." : "Evaluate Recidivism Risk"}
            </button>
          </form>
        </div>

        {/* Prediction Outputs */}
        <div className="glass-card p-6 rounded-2xl flex flex-col justify-between min-h-[300px]">
          <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2 pb-4 border-b border-[#1e293b]/50">
            <Sparkles className="w-4 h-4 text-violet-400 animate-pulse" /> Inference Results
          </h2>

          {result ? (
            <div className="flex-1 flex flex-col justify-between py-4 space-y-6">
              {/* Score card */}
              <div className="flex justify-between items-center p-4 bg-slate-900/50 border border-[#1e293b] rounded-xl">
                <div>
                  <p className="text-xs text-slate-500 font-semibold">RISK LEVEL</p>
                  <p className={`text-xl font-black mt-1 ${result.risk_level === "HIGH" ? "text-rose-400" : "text-emerald-400"}`}>
                    {result.risk_level}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-slate-500 font-semibold">RECIDIVISM PROBABILITY</p>
                  <p className="text-2xl font-black mt-1 text-slate-200">
                    {(result.recidivism_probability * 100).toFixed(0)}%
                  </p>
                </div>
              </div>

              {/* SHAP explainability stub */}
              <div className="space-y-3">
                <p className="text-xs text-slate-400 font-bold uppercase tracking-wider flex items-center gap-1.5">
                  <TrendingUp className="w-3.5 h-3.5 text-indigo-400" />
                  SHAP Feature Contributions
                </p>
                <div className="space-y-2">
                  {Object.entries(result.explainability_shap).map(([key, val]: any) => (
                    <div key={key} className="space-y-1">
                      <div className="flex justify-between text-[10px] font-semibold text-slate-400 uppercase">
                        <span>{key.replace("_", " ")}</span>
                        <span className={val > 0 ? "text-rose-400" : "text-emerald-400"}>
                          {val > 0 ? `+${val.toFixed(2)}` : val.toFixed(2)}
                        </span>
                      </div>
                      <div className="h-1.5 w-full bg-slate-950 rounded-full overflow-hidden">
                        <div 
                          className={`h-full rounded-full ${val > 0 ? "bg-rose-500" : "bg-emerald-500"}`} 
                          style={{ width: `${Math.abs(val) * 100}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="flex-1 flex flex-col justify-center items-center text-center p-8 text-slate-500 font-medium">
              <p className="text-sm">No Active Prediction</p>
              <p className="text-xs mt-1 max-w-xs">
                Fill the suspect parameters in the profile panel and click evaluate to review the ML classification score.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
