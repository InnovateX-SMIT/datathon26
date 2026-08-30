"use client";

import React, { useState, useEffect } from "react";
import { Network } from "lucide-react";
import NetworkViewer from "@/features/network/components/NetworkViewer";
import RepeatOffenderPredictionCard from "@/features/network/components/RepeatOffenderPredictionCard";
import NoDatasetBanner from "@/components/shared/NoDatasetBanner";
import { fetchDatasets, DatasetInfo } from "@/services/dataset.service";

export default function NetworkIntelligencePage() {
  const [activeDatasets, setActiveDatasets] = useState<DatasetInfo[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    document.title = "Network Intelligence | CrimeNexus";
    const loadDatasets = async () => {
      try {
        const list = await fetchDatasets();
        setActiveDatasets(list.filter(d => d.is_active));
      } catch (err) {
        console.error("Failed to load active datasets", err);
      } finally {
        setLoading(false);
      }
    };
    loadDatasets();

    const handleDatasetChange = () => {
      loadDatasets();
    };
    window.addEventListener("activeDatasetChanged", handleDatasetChange);
    return () => {
      window.removeEventListener("activeDatasetChanged", handleDatasetChange);
    };
  }, []);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/70 pb-6">
        <div className="flex items-start gap-3.5">
          <div className="p-2.5 bg-indigo-500/10 border border-indigo-500/20 rounded-xl shrink-0">
            <Network className="w-5 h-5 text-indigo-400" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-slate-100 uppercase tracking-tight leading-tight">
              Network Intelligence
            </h1>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="p-8 text-center text-slate-500 font-mono text-sm animate-pulse">
          Loading network workspace context...
        </div>
      ) : activeDatasets.length === 0 ? (
        <NoDatasetBanner />
      ) : (
        <>
          {/* Repeat Offender Recidivism Prediction Component (Pipeline 3) */}
          <RepeatOffenderPredictionCard />
          {/* Network Graph */}
          <NetworkViewer />
        </>
      )}
    </div>
  );
}

