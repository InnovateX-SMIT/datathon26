"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { FileText, Plus, ShieldAlert, RefreshCw } from "lucide-react";
import PageHeader from "@/components/layout/page-header";
import FirCaseList from "@/features/fir/components/FirCaseList";
import { fetchDatasets, type DatasetInfo } from "@/services/dataset.service";

export default function FirCasesPage() {
  const [activeDatasets, setActiveDatasets] = useState<DatasetInfo[]>([]);
  const [datasetsLoading, setDatasetsLoading] = useState(true);

  const loadActiveDatasets = async () => {
    setDatasetsLoading(true);
    try {
      const data = await fetchDatasets();
      setActiveDatasets(data.filter((d) => d.is_active));
    } catch (err) {
      console.error("Failed to load datasets", err);
    } finally {
      setDatasetsLoading(false);
    }
  };

  useEffect(() => {
    loadActiveDatasets();
    const handler = () => loadActiveDatasets();
    window.addEventListener("activeDatasetChanged", handler);
    return () => window.removeEventListener("activeDatasetChanged", handler);
  }, []);

  const isFirDataset = activeDatasets.some(
    (d) => d.schema_type === "fir_normalized"
  );

  // No active dataset
  if (!datasetsLoading && activeDatasets.length === 0) {
    return (
      <div className="min-h-[80vh] flex flex-col items-center justify-center p-6 text-center text-slate-200">
        <div className="bg-slate-900/60 p-8 rounded-3xl border border-slate-800/80 max-w-md w-full backdrop-blur-md space-y-6">
          <ShieldAlert className="w-16 h-16 text-indigo-400 mx-auto animate-pulse" />
          <h2 className="text-xl font-bold uppercase tracking-tight">No Active Dataset</h2>
          <p className="text-sm text-slate-400 leading-relaxed">
            FIR case management requires an active FIR-normalized dataset. Please activate one from the Dataset Manager.
          </p>
          <Link
            href="/dataset-manager"
            className="block w-full py-3 px-4 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs uppercase tracking-wider rounded-xl transition-all shadow-lg shadow-indigo-600/10"
          >
            Go to Dataset Manager
          </Link>
        </div>
      </div>
    );
  }

  // Legacy dataset active (not FIR normalized)
  if (!datasetsLoading && !isFirDataset) {
    return (
      <div className="min-h-[80vh] flex flex-col items-center justify-center p-6 text-center text-slate-200">
        <div className="bg-slate-900/60 p-8 rounded-3xl border border-amber-500/30 max-w-md w-full backdrop-blur-md space-y-6">
          <ShieldAlert className="w-16 h-16 text-amber-400 mx-auto" />
          <h2 className="text-xl font-bold uppercase tracking-tight">Legacy Dataset Active</h2>
          <p className="text-sm text-slate-400 leading-relaxed">
            The currently active dataset uses the legacy schema. FIR case management requires an FIR-normalized dataset.
            Switch to an FIR dataset in the Dataset Manager to use this feature.
          </p>
          <Link
            href="/dataset-manager"
            className="block w-full py-3 px-4 bg-amber-600 hover:bg-amber-500 text-white font-bold text-xs uppercase tracking-wider rounded-xl transition-all"
          >
            Switch Dataset
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
      <PageHeader
        icon={FileText}
        iconColor="text-indigo-400"
        iconBg="bg-indigo-500/10 border border-indigo-500/20"
        badge="Case Registry"
        title="FIR Cases"
        subtitle="First Information Report Management"
        description="Browse, search, and manage all registered FIR cases. Click any row to view full case details."
      >
        <Link
          href="/fir/cases/new"
          className="flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs uppercase tracking-wider rounded-xl transition-all shadow-lg shadow-indigo-600/20"
        >
          <Plus className="w-4 h-4" /> Register New FIR
        </Link>
      </PageHeader>

      <FirCaseList />
    </div>
  );
}
