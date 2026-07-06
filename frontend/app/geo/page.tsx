"use client";

import React, { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import { AlertCircle, Map, RefreshCw } from "lucide-react";
import GeoFilters from "@/features/geo/components/GeoFilters";
import type { GeoFiltersState, DistrictCrime, StationCrime, HeatmapPoint, HotspotCluster } from "@/features/geo/types/geo";
import { fetchGeoIntelligence } from "@/features/geo/services/geoApi";

// Dynamically import maps with ssr: false to prevent Next.js build crash
const DistrictMap = dynamic(() => import("@/features/geo/components/DistrictMap"), {
  ssr: false,
  loading: () => <MapLoadingPlaceholder label="District Map" />
});

const StationMap = dynamic(() => import("@/features/geo/components/StationMap"), {
  ssr: false,
  loading: () => <MapLoadingPlaceholder label="Police Station Map" />
});

const CrimeHeatmap = dynamic(() => import("@/features/geo/components/CrimeHeatmap"), {
  ssr: false,
  loading: () => <MapLoadingPlaceholder label="Crime Heatmap" />
});

const HotspotMap = dynamic(() => import("@/features/geo/components/HotspotMap"), {
  ssr: false,
  loading: () => <MapLoadingPlaceholder label="Hotspot Map" />
});

function MapLoadingPlaceholder({ label }: { label: string }) {
  return (
    <div className="glass-card p-6 rounded-2xl border border-slate-800/60 h-[450px] flex flex-col mb-6 animate-pulse">
      <div className="flex items-center gap-2 mb-4">
        <div className="w-1.5 h-5 bg-indigo-500 rounded" />
        <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">{label}</h3>
      </div>
      <div className="flex-1 bg-slate-800/10 rounded-xl flex items-center justify-center text-slate-500 text-xs">
        Initializing map layers...
      </div>
    </div>
  );
}

export default function GeoPage() {
  const [filters, setFilters] = useState<GeoFiltersState>({});
  
  const [districtData, setDistrictData] = useState<DistrictCrime[]>([]);
  const [stationData, setStationData] = useState<StationCrime[]>([]);
  const [heatmapData, setHeatmapData] = useState<HeatmapPoint[]>([]);
  const [hotspotData, setHotspotData] = useState<HotspotCluster[]>([]);
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async (activeFilters: GeoFiltersState, signal?: AbortSignal) => {
    setLoading(true);
    setError(null);
    try {
      const intelligence = await fetchGeoIntelligence(activeFilters, signal);
      setDistrictData(intelligence.districts);
      setStationData(intelligence.stations);
      setHeatmapData(intelligence.heatmap);
      setHotspotData(intelligence.hotspots);
    } catch (err) {
      if (err instanceof DOMException && err.name === "AbortError") return;
      setError("Unable to load geospatial intelligence for the active dataset. Verify the API server and dataset status.");
    } finally {
      if (!signal?.aborted) setLoading(false);
    }
  };

  useEffect(() => {
    const controller = new AbortController();
    const timer = window.setTimeout(() => {
      loadData(filters, controller.signal);
    }, 0);
    return () => {
      window.clearTimeout(timer);
      controller.abort();
    };
  }, [filters]);

  useEffect(() => {
    const handleDatasetChange = () => {
      loadData(filters);
    };
    window.addEventListener("activeDatasetChanged", handleDatasetChange);
    return () => {
      window.removeEventListener("activeDatasetChanged", handleDatasetChange);
    };
  }, [filters]);

  const handleRetry = () => {
    loadData(filters);
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Title Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div className="flex items-center gap-3.5">
          <div className="p-3 bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 rounded-2xl">
            <Map className="w-6 h-6" />
          </div>
          <div>
            <div className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest bg-indigo-500/10 border border-indigo-500/20 px-2.5 py-0.5 rounded-full w-fit">
              Geospatial Mapping Suite
            </div>
            <h1 className="text-2xl font-black text-slate-100 uppercase tracking-tight mt-1.5">
              Geo Intelligence Engine
            </h1>
          </div>
        </div>
        
        {loading && (
          <div className="flex items-center gap-2 text-xs font-bold text-indigo-400 bg-indigo-500/10 border border-indigo-500/20 px-4 py-2 rounded-xl">
            <RefreshCw className="w-4 h-4 animate-spin" />
            <span>Refreshing Maps...</span>
          </div>
        )}
      </div>

      {/* Query Filters */}
      <GeoFilters filters={filters} onFiltersChange={setFilters} />

      {/* Error State Banner */}
      {error && (
        <div className="p-4 bg-rose-500/10 border border-rose-500/20 rounded-2xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 text-xs text-rose-400">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
          <button
            onClick={handleRetry}
            className="px-3 py-1.5 bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/30 rounded-lg text-[10px] uppercase font-bold transition-all cursor-pointer"
          >
            Retry Connection
          </button>
        </div>
      )}

      {/* Main Grid Layout for Maps */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* District Crime Map */}
        <DistrictMap data={districtData} loading={loading} />
        
        {/* Police Station Map */}
        <StationMap data={stationData} loading={loading} />
        
        {/* Crime Density Heatmap */}
        <CrimeHeatmap data={heatmapData} loading={loading} />
        
        {/* Crime Hotspots */}
        <HotspotMap data={hotspotData} loading={loading} />
        
      </div>
    </div>
  );
}
