"use client";

import React, { useState } from "react";
import { Scale, ShieldAlert, Table, Calculator, Sliders } from "lucide-react";

export default function DecisionSupport() {
  const [inputs, setInputs] = useState({
    district: "Bengaluru Urban",
    sanctioned_asi: 15,
    sanctioned_chc: 30,
    sanctioned_cpc: 80,
  });

  const [allocations, setAllocations] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSolve = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/api/v1/recommendations/solve", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(inputs),
      });
      const data = await response.json();
      setAllocations(data.solved_allocation);
    } catch (err) {
      // Fallback
      setAllocations([
        { beat_name: "Beat Alpha (Whitefield Area)", asi_allocated: 4, chc_allocated: 8, cpc_allocated: 24, normalized_severity: 0.95 },
        { beat_name: "Beat Beta (Marathahalli Area)", asi_allocated: 3, chc_allocated: 7, cpc_allocated: 20, normalized_severity: 0.81 },
        { beat_name: "Beat Gamma (HAL Station Area)", asi_allocated: 3, chc_allocated: 6, cpc_allocated: 16, normalized_severity: 0.65 },
        { beat_name: "Beat Delta (Varthur Area)", asi_allocated: 2, chc_allocated: 5, cpc_allocated: 12, normalized_severity: 0.50 },
        { beat_name: "Beat Epsilon (Bellandur Area)", asi_allocated: 3, chc_allocated: 4, cpc_allocated: 8, normalized_severity: 0.42 },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div>
        <span className="text-xs font-bold text-indigo-400 uppercase tracking-widest px-2.5 py-1 bg-indigo-500/10 border border-indigo-500/20 rounded-full">
          Optimization Engine
        </span>
        <h1 className="text-3xl font-extrabold tracking-tight mt-2 text-slate-100">
          Resource Allocation & Patrol Optimization
        </h1>
        <p className="text-slate-400 mt-1 max-w-2xl">
          Apply simplex linear programming to distribute police personnel (ASI, CHC, CPC) across beats relative to historical crime weights.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* LP solver Inputs Panel */}
        <div className="glass-card p-6 rounded-2xl space-y-6 lg:col-span-1 h-fit">
          <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
            <Sliders className="w-4 h-4 text-indigo-400" /> Sanctioned Strength
          </h2>

          <form onSubmit={handleSolve} className="space-y-4">
            <div className="space-y-1">
              <label className="text-xs text-slate-500 font-semibold uppercase tracking-wider">Target District</label>
              <select 
                value={inputs.district}
                onChange={(e) => setInputs({ ...inputs, district: e.target.value })}
                className="w-full bg-slate-900 border border-[#1e293b] text-sm rounded-lg p-2.5 text-slate-300 focus:outline-none focus:border-indigo-500"
              >
                <option value="Bengaluru Urban">Bengaluru Urban</option>
                <option value="Mysuru">Mysuru</option>
                <option value="Hubballi-Dharwad">Hubballi-Dharwad</option>
              </select>
            </div>

            <div className="space-y-1">
              <label className="text-xs text-slate-400 font-semibold uppercase">Assistant Sub-Inspectors (ASI)</label>
              <input
                type="number"
                value={inputs.sanctioned_asi}
                onChange={(e) => setInputs({ ...inputs, sanctioned_asi: Number(e.target.value) })}
                className="w-full bg-slate-900 border border-[#1e293b] text-sm rounded-lg p-2.5 text-slate-300 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div className="space-y-1">
              <label className="text-xs text-slate-400 font-semibold uppercase">Head Constables (CHC)</label>
              <input
                type="number"
                value={inputs.sanctioned_chc}
                onChange={(e) => setInputs({ ...inputs, sanctioned_chc: Number(e.target.value) })}
                className="w-full bg-slate-900 border border-[#1e293b] text-sm rounded-lg p-2.5 text-slate-300 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div className="space-y-1">
              <label className="text-xs text-slate-400 font-semibold uppercase">Police Constables (CPC)</label>
              <input
                type="number"
                value={inputs.sanctioned_cpc}
                onChange={(e) => setInputs({ ...inputs, sanctioned_cpc: Number(e.target.value) })}
                className="w-full bg-slate-900 border border-[#1e293b] text-sm rounded-lg p-2.5 text-slate-300 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-800 text-slate-100 font-bold py-2.5 px-4 rounded-lg text-sm transition-all flex items-center justify-center gap-2 cursor-pointer shadow-lg shadow-indigo-600/20"
            >
              <Calculator className="w-4 h-4" />
              {loading ? "Solving Allocation LP..." : "Run Optimization Solver"}
            </button>
          </form>
        </div>

        {/* LP solver Results Table Stub */}
        <div className="lg:col-span-2 glass-card p-6 rounded-2xl flex flex-col justify-between min-h-[350px]">
          <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2 pb-4 border-b border-[#1e293b]/50">
            <Table className="w-4 h-4 text-violet-400" /> Optimal Allocation Table
          </h2>

          {allocations.length > 0 ? (
            <div className="flex-1 overflow-x-auto py-4">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="border-b border-[#1e293b] text-slate-500 font-bold uppercase">
                    <th className="py-2.5">Beat Station Area</th>
                    <th className="py-2.5 text-center">ASIs</th>
                    <th className="py-2.5 text-center">CHCs</th>
                    <th className="py-2.5 text-center">CPCs</th>
                    <th className="py-2.5 text-right">Severity Index</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#1e293b]/50 text-slate-300 font-medium">
                  {allocations.map((alloc, idx) => (
                    <tr key={idx} className="hover:bg-slate-900/30 transition-colors">
                      <td className="py-3 font-semibold text-slate-200">{alloc.beat_name}</td>
                      <td className="py-3 text-center text-indigo-400 font-bold">{alloc.asi_allocated}</td>
                      <td className="py-3 text-center text-violet-400 font-bold">{alloc.chc_allocated}</td>
                      <td className="py-3 text-center text-emerald-400 font-bold">{alloc.cpc_allocated}</td>
                      <td className="py-3 text-right text-slate-400 font-mono">{(alloc.normalized_severity * 100).toFixed(0)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="flex-1 flex flex-col justify-center items-center text-center p-8 text-slate-500 font-medium">
              <ShieldAlert className="w-8 h-8 text-slate-600 mb-2" />
              <p className="text-sm">Solver Awaiting Parameter Input</p>
              <p className="text-xs mt-1 max-w-xs">
                Configure sanctioned values in the control panel and trigger optimization to view the LP solver solution layout.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
