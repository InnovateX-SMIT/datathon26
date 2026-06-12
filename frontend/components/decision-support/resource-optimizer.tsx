import React, { useState } from "react";
import { Scale, Users, History, Check, AlertCircle, ChevronDown } from "lucide-react";
import type { BeatAllocation, ResourceAllocation } from "@/types/recommendation";

interface ResourceOptimizerProps {
  history: ResourceAllocation[];
  solverResult: BeatAllocation[] | null;
  solverLoading: boolean;
  solverError: string | null;
  runSolver: (payload: {
    district: string;
    sanctioned_asi: number;
    sanctioned_chc: number;
    sanctioned_cpc: number;
  }) => void;
  setSolverResult: (res: BeatAllocation[] | null) => void;
}

const DISTRICTS = [
  "Bengaluru Urban",
  "Ballari",
  "Mysuru",
  "Shivamogga",
  "Belagavi",
  "Dharwad",
  "Mangaluru",
];

export default function ResourceOptimizer({
  history,
  solverResult,
  solverLoading,
  solverError,
  runSolver,
  setSolverResult,
}: ResourceOptimizerProps) {
  const [district, setDistrict] = useState(DISTRICTS[0]);
  const [asi, setAsi] = useState(10);
  const [chc, setChc] = useState(25);
  const [cpc, setCpc] = useState(70);
  const [showHistory, setShowHistory] = useState(false);
  const [selectedHistoryId, setSelectedHistoryId] = useState<number | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSelectedHistoryId(null);
    runSolver({
      district,
      sanctioned_asi: Number(asi),
      sanctioned_chc: Number(chc),
      sanctioned_cpc: Number(cpc),
    });
  };

  const handleSelectHistory = (run: ResourceAllocation) => {
    setSelectedHistoryId(run.id);
    setSolverResult(run.solved_allocation);
  };

  return (
    <div className="space-y-8 animate-fade-in">
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-8 items-start">
        {/* Left Column: Form Controls */}
        <div className="xl:col-span-4 bg-slate-950/40 border border-slate-900/80 rounded-3xl p-6 relative overflow-hidden backdrop-blur-xl">
          <div className="absolute top-0 right-0 w-[150px] h-[150px] rounded-full bg-indigo-500/5 blur-[50px] pointer-events-none" />
          
          <div className="flex items-center gap-2 mb-6">
            <Scale className="w-5 h-5 text-indigo-400" />
            <h2 className="text-lg font-black text-slate-100 uppercase tracking-tight">Optimizer Inputs</h2>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* District Selector */}
            <div className="space-y-1.5">
              <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Target District</label>
              <div className="relative">
                <select
                  value={district}
                  onChange={(e) => setDistrict(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 text-slate-200 text-sm appearance-none outline-none focus:border-indigo-500/50 transition-all cursor-pointer font-medium"
                >
                  {DISTRICTS.map((d) => (
                    <option key={d} value={d}>
                      {d}
                    </option>
                  ))}
                </select>
                <ChevronDown className="absolute right-3.5 top-3.5 w-4 h-4 text-slate-500 pointer-events-none" />
              </div>
            </div>

            {/* ASIs */}
            <div className="space-y-1.5">
              <div className="flex justify-between items-center">
                <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Assistant Sub-Inspectors (ASI)</label>
                <span className="text-xs font-mono font-bold text-indigo-400">{asi}</span>
              </div>
              <input
                type="number"
                min="0"
                value={asi}
                onChange={(e) => setAsi(Number(e.target.value))}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-slate-200 text-sm outline-none focus:border-indigo-500/50 transition-all font-mono font-bold"
              />
            </div>

            {/* CHCs */}
            <div className="space-y-1.5">
              <div className="flex justify-between items-center">
                <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Head Constables (CHC)</label>
                <span className="text-xs font-mono font-bold text-indigo-400">{chc}</span>
              </div>
              <input
                type="number"
                min="0"
                value={chc}
                onChange={(e) => setChc(Number(e.target.value))}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-slate-200 text-sm outline-none focus:border-indigo-500/50 transition-all font-mono font-bold"
              />
            </div>

            {/* CPCs */}
            <div className="space-y-1.5">
              <div className="flex justify-between items-center">
                <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Police Constables (CPC)</label>
                <span className="text-xs font-mono font-bold text-indigo-400">{cpc}</span>
              </div>
              <input
                type="number"
                min="0"
                value={cpc}
                onChange={(e) => setCpc(Number(e.target.value))}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-slate-200 text-sm outline-none focus:border-indigo-500/50 transition-all font-mono font-bold"
              />
            </div>

            <button
              type="submit"
              disabled={solverLoading}
              className="w-full py-3.5 bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 disabled:from-slate-800 disabled:to-slate-800 border border-indigo-500/20 text-white rounded-xl text-xs font-black uppercase tracking-wider shadow-lg shadow-indigo-600/10 hover:shadow-indigo-500/20 transition-all cursor-pointer flex items-center justify-center gap-2 mt-4"
            >
              {solverLoading ? (
                <>
                  <Users className="w-4 h-4 animate-spin text-slate-300" />
                  Solving LP Model...
                </>
              ) : (
                <>
                  <Scale className="w-4 h-4" />
                  Optimize Allocation
                </>
              )}
            </button>
          </form>

          {/* Solver Logs Error */}
          {solverError && (
            <div className="mt-4 p-3.5 bg-red-500/10 border border-red-500/20 rounded-2xl flex items-start gap-2.5 text-xs text-red-400">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{solverError}</span>
            </div>
          )}

          {/* Solver Logs success indicator */}
          {solverResult && !solverLoading && !solverError && (
            <div className="mt-4 p-3.5 bg-green-500/10 border border-green-500/20 rounded-2xl flex items-start gap-2.5 text-xs text-green-400">
              <Check className="w-4 h-4 shrink-0 mt-0.5" />
              <span>Optimal deployment solved successfully. Ratios satisfy constraints.</span>
            </div>
          )}

          {/* Toggle History Log List */}
          <div className="border-t border-slate-900 mt-6 pt-5">
            <button
              onClick={() => setShowHistory(!showHistory)}
              className="w-full flex items-center justify-between text-[10px] font-bold text-slate-500 hover:text-slate-300 uppercase tracking-widest transition-all"
            >
              <span className="flex items-center gap-1.5">
                <History className="w-3.5 h-3.5" />
                Solver Logs ({history.length})
              </span>
              <ChevronDown className={`w-3.5 h-3.5 transform transition-transform ${showHistory ? "rotate-180" : ""}`} />
            </button>

            {showHistory && (
              <div className="mt-4 space-y-2 max-h-[220px] overflow-y-auto pr-1">
                {history.length === 0 ? (
                  <p className="text-[10px] text-slate-600 font-medium py-2">No historical solver runs logged.</p>
                ) : (
                  history.map((run) => (
                    <div
                      key={run.id}
                      onClick={() => handleSelectHistory(run)}
                      className={`p-3 border rounded-xl flex flex-col gap-1 cursor-pointer transition-all ${selectedHistoryId === run.id ? "bg-indigo-500/10 border-indigo-500/30" : "bg-slate-950/60 border-slate-900 hover:border-slate-800"}`}
                    >
                      <div className="flex justify-between items-center">
                        <span className="text-xs font-bold text-slate-300">{run.district}</span>
                        <span className="text-[9px] font-mono text-slate-600">{new Date(run.created_at).toLocaleDateString()}</span>
                      </div>
                      <div className="flex items-center gap-4 text-[9px] font-mono text-slate-500">
                        <span>ASI: <strong className="text-slate-400 font-bold">{run.allocated_asi}</strong></span>
                        <span>CHC: <strong className="text-slate-400 font-bold">{run.allocated_chc}</strong></span>
                        <span>CPC: <strong className="text-slate-400 font-bold">{run.allocated_cpc}</strong></span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Allocation Result Grid */}
        <div className="xl:col-span-8 space-y-6">
          {solverResult ? (
            <div className="bg-slate-950/40 border border-slate-900/80 rounded-3xl p-6 backdrop-blur-xl relative overflow-hidden">
              <div className="absolute bottom-0 left-0 w-[200px] h-[200px] rounded-full bg-violet-500/5 blur-[60px] pointer-events-none" />

              <div className="flex items-center justify-between border-b border-slate-900 pb-4 mb-6">
                <div>
                  <h3 className="text-md font-extrabold text-slate-100 uppercase tracking-tight">Optimal Deployment Map</h3>
                  <p className="text-[10px] text-slate-400 font-semibold uppercase tracking-widest mt-0.5">District resource distribution details</p>
                </div>
                {selectedHistoryId && (
                  <span className="px-2.5 py-1 bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-[10px] font-mono font-bold rounded-lg uppercase tracking-wider">
                    Viewing Log Record #{selectedHistoryId}
                  </span>
                )}
              </div>

              {/* Table Roster */}
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="border-b border-slate-900 text-[10px] font-bold text-slate-500 uppercase tracking-wider">
                      <th className="pb-3 pl-2">Beat/Station Name</th>
                      <th className="pb-3 text-center">Normalized Severity</th>
                      <th className="pb-3 text-center">ASI Allocated</th>
                      <th className="pb-3 text-center">CHC Allocated</th>
                      <th className="pb-3 text-center">CPC Allocated</th>
                      <th className="pb-3 text-right pr-2">Roster Share</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-950/80">
                    {solverResult.map((alloc, idx) => (
                      <tr key={idx} className="text-slate-300 hover:bg-slate-900/30 transition-colors">
                        <td className="py-4 pl-2 font-bold text-slate-200 text-sm">
                          {alloc.beat_name}
                        </td>
                        <td className="py-4 text-center">
                          <div className="inline-flex flex-col items-center gap-1.5">
                            <span className="text-xs font-mono font-bold text-slate-400">
                              {(alloc.normalized_severity * 100).toFixed(1)}%
                            </span>
                            <div className="w-16 h-1.5 bg-slate-900 rounded-full overflow-hidden border border-slate-800">
                              <div
                                className="h-full bg-gradient-to-r from-indigo-500 to-violet-500"
                                style={{ width: `${alloc.normalized_severity * 100}%` }}
                              />
                            </div>
                          </div>
                        </td>
                        <td className="py-4 text-center text-sm font-mono font-black text-slate-300">
                          {alloc.asi_allocated}
                        </td>
                        <td className="py-4 text-center text-sm font-mono font-black text-slate-300">
                          {alloc.chc_allocated}
                        </td>
                        <td className="py-4 text-center text-sm font-mono font-black text-slate-300">
                          {alloc.cpc_allocated}
                        </td>
                        <td className="py-4 text-right pr-2">
                          <span className="px-2 py-1 bg-slate-900 border border-slate-800 rounded-lg text-xs font-mono font-bold text-indigo-400">
                            {alloc.asi_allocated + alloc.chc_allocated + alloc.cpc_allocated} Officers
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            <div className="bg-slate-950/20 border border-dashed border-slate-800 rounded-3xl p-12 text-center flex flex-col items-center justify-center min-h-[300px]">
              <div className="p-4 bg-slate-900/40 rounded-2xl border border-slate-800/60 mb-4 text-slate-500">
                <Scale className="w-8 h-8" />
              </div>
              <h4 className="text-sm font-bold text-slate-300 uppercase tracking-wider">No Optimization Solved</h4>
              <p className="text-xs text-slate-500 mt-2 max-w-sm leading-relaxed">
                Select a district and input the sanctioned personnel sizes on the left, then click Optimize to run the linear programming solver.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
