"use client";

import React, { useEffect, useState } from "react";
import { BrainCircuit, RefreshCw, ShieldAlert } from "lucide-react";
import { fetchDatasets, DatasetInfo } from "@/services/dataset.service";
import SociologicalIntelTab from "@/features/analytics/components/SociologicalIntelTab";

export default function SociologicalPage() {
  const [activeDatasets, setActiveDatasets] = useState<DatasetInfo[]>([]);
  const [activeDatasetsLoading, setActiveDatasetsLoading] = useState(true);

  const loadActiveDatasets = async () => {
    setActiveDatasetsLoading(true);
    try {
      const data = await fetchDatasets();
      setActiveDatasets(data.filter((d) => d.is_active));
    } catch (err) {
      console.error("Failed to load active datasets details", err);
    } finally {
      setActiveDatasetsLoading(false);
    }
  };

  useEffect(() => {
    loadActiveDatasets();

    const handleDatasetChange = () => {
      loadActiveDatasets();
    };
    window.addEventListener("activeDatasetChanged", handleDatasetChange);
    return () => {
      window.removeEventListener("activeDatasetChanged", handleDatasetChange);
    };
  }, []);

  const isNoActiveDataset =
    !activeDatasetsLoading &&
    activeDatasets.length === 0;

  if (isNoActiveDataset) {
    return (
      <div className="min-h-[80vh] flex flex-col items-center justify-center p-6 text-center text-slate-200">
        <div className="bg-slate-900/60 p-8 rounded-3xl border border-slate-800/80 max-w-md w-full backdrop-blur-md space-y-6">
          <ShieldAlert className="w-16 h-16 text-indigo-400 mx-auto animate-pulse" />
          <h2 className="text-xl font-bold uppercase tracking-tight">No active dataset selected</h2>
          <p className="text-sm text-slate-400 leading-relaxed">
            CrimeNexus operations require at least one active database registry entry to query operational analytics, trend lines, and mapping clusters.
          </p>
          <a
            href="/dataset-manager"
            className="block w-full py-3 px-4 bg-indigo-600 hover:bg-indigo-550 text-white font-bold text-xs uppercase tracking-wider rounded-xl transition-all shadow-lg shadow-indigo-600/10"
          >
            Go to Dataset Manager
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
      {/* Header section */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-800/60 pb-6">
        <div>
          <div className="flex flex-wrap items-center gap-2.5">
            <BrainCircuit className="w-6 h-6 text-indigo-400" />
            <h1 className="text-2xl font-extrabold text-white tracking-tight sm:text-3xl">
              Sociological Intelligence
            </h1>
            <span className="px-2.5 py-0.5 text-[10px] font-bold tracking-wider uppercase bg-indigo-500/10 text-indigo-400 rounded-full border border-indigo-500/20">
              Correlation Analysis Engine
            </span>
          </div>
        </div>

        {/* Right Info Panel */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 bg-slate-900/40 p-2.5 rounded-xl border border-slate-800/40">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-[10px] text-slate-500 uppercase tracking-widest font-mono">Using Dataset:</span>
            {activeDatasets.length > 0 ? (
              activeDatasets.map((ds) => (
                <span key={ds.id} className="text-[10px] font-mono text-emerald-400 bg-emerald-500/5 px-2 py-0.5 border border-emerald-500/10 rounded">
                  ✔ {ds.display_name}
                </span>
              ))
            ) : (
              <span className="text-[10px] font-mono text-red-400 bg-red-500/5 px-2 py-0.5 border border-red-500/10 rounded">
                ✘ None Active
              </span>
            )}
          </div>
        </div>
      </div>

      <SociologicalIntelTab />
    </div>
  );
}
