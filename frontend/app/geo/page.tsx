"use client";

import React, { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import { AlertCircle, ChevronRight, Compass, Map, RefreshCw, ShieldAlert, X } from "lucide-react";
import GeoFilters from "@/features/geo/components/GeoFilters";
import TimeOfDayAnalysis from "@/features/geo/components/TimeOfDayAnalysis";
import { fetchDatasets, DatasetInfo } from "@/services/dataset.service";
import type {
  GeoFiltersState,
  DistrictCrime,
  StationCrime,
  HeatmapPoint,
  HotspotCluster,
  GeoMarker,
  TimeOfDayResponse
} from "@/features/geo/types/geo";
import { fetchGeoIntelligence } from "@/features/geo/services/geoApi";

import CrimeRiskPredictionCard from "@/features/geo/components/CrimeRiskPredictionCard";
import HotspotPredictionCard from "@/features/geo/components/HotspotPredictionCard";

// Dynamically import Leaflet maps with ssr: false to prevent Next.js SSR build crashes
const DistrictMap = dynamic(() => import("@/features/geo/components/DistrictMap"), {
  ssr: false,
  loading: () => <MapLoadingPlaceholder label="District Crime Map (Real Boundary Overlay)" />
});

const StationMap = dynamic(() => import("@/features/geo/components/StationMap"), {
  ssr: false,
  loading: () => <MapLoadingPlaceholder label="Police Station Map (Precinct Distribution)" />
});

const FirMarkerMap = dynamic(() => import("@/features/geo/components/FirMarkerMap"), {
  ssr: false,
  loading: () => <MapLoadingPlaceholder label="Operational Incident Marker Map" />
});

const CrimeHeatmap = dynamic(() => import("@/features/geo/components/CrimeHeatmap"), {
  ssr: false,
  loading: () => <MapLoadingPlaceholder label="Crime Heatmap" />
});

const HotspotMap = dynamic(() => import("@/features/geo/components/HotspotMap"), {
  ssr: false,
  loading: () => <MapLoadingPlaceholder label="Historical Crime Hotspots (Spatiotemporal DBSCAN)" />
});

function MapLoadingPlaceholder({ label }: { label: string }) {
  return (
    <div className="glass-card p-6 rounded-2xl border border-slate-800/60 h-[450px] flex flex-col mb-6 animate-pulse">
      <div className="flex items-center gap-2 mb-4">
        <div className="w-1.5 h-5 bg-indigo-500 rounded" />
        <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-sans">{label}</h3>
      </div>
      <div className="flex-1 bg-slate-800/10 rounded-xl flex items-center justify-center text-slate-500 text-xs font-sans">
        Initializing map layers...
      </div>
    </div>
  );
}

export default function GeoPage() {
  const [filters, setFilters] = useState<GeoFiltersState>({});
  
  const [districtData, setDistrictData] = useState<DistrictCrime[]>([]);
  const [stationData, setStationData] = useState<StationCrime[]>([]);
  const [markerData, setMarkerData] = useState<GeoMarker[]>([]);
  const [heatmapData, setHeatmapData] = useState<HeatmapPoint[]>([]);
  const [hotspotData, setHotspotData] = useState<HotspotCluster[]>([]);
  const [timeOfDayData, setTimeOfDayData] = useState<TimeOfDayResponse | null>(null);
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Active datasets state
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

  const loadData = async (activeFilters: GeoFiltersState, signal?: AbortSignal) => {
    setLoading(true);
    setError(null);
    try {
      const intelligence = await fetchGeoIntelligence(activeFilters, signal);
      setDistrictData(intelligence.districts || []);
      setStationData(intelligence.stations || []);
      setMarkerData(intelligence.markers || []);
      setHeatmapData(intelligence.heatmap || []);
      setHotspotData(intelligence.hotspots || []);
      setTimeOfDayData(intelligence.time_of_day || null);
    } catch (err: any) {
      if (err instanceof DOMException && err.name === "AbortError") return;
      setError(err.message || "Unable to load geospatial intelligence for the active dataset. Verify the API server and dataset status.");
    } finally {
      if (!signal?.aborted) setLoading(false);
    }
  };

  useEffect(() => {
    loadActiveDatasets();
  }, []);

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
      loadActiveDatasets();
      loadData(filters);
    };
    window.addEventListener("activeDatasetChanged", handleDatasetChange);
    return () => {
      window.removeEventListener("activeDatasetChanged", handleDatasetChange);
    };
  }, [filters]);

  const handleRetry = () => {
    loadActiveDatasets();
    loadData(filters);
  };

  // Drill-down callbacks
  const handleSelectDistrict = (districtName: string) => {
    setFilters((prev) => ({
      ...prev,
      district: districtName || undefined,
      police_station: undefined, // Reset station when district changes
    }));
  };

  const handleSelectStation = (stationName: string) => {
    setFilters((prev) => ({
      ...prev,
      police_station: stationName || undefined,
    }));
  };

  const handleClearDrillDown = () => {
    setFilters((prev) => ({
      ...prev,
      district: undefined,
      police_station: undefined,
    }));
  };

  // ── EMPTY STATE RENDERING ──
  const isNoActiveDataset =
    !loading &&
    !activeDatasetsLoading &&
    (error?.includes("No active dataset") || activeDatasets.length === 0);

  if (isNoActiveDataset) {
    return (
      <div className="min-h-[80vh] flex flex-col items-center justify-center p-6 text-center text-slate-200">
        <div className="bg-slate-900/60 p-8 rounded-3xl border border-slate-800/80 max-w-md w-full backdrop-blur-md space-y-6">
          <ShieldAlert className="w-16 h-16 text-indigo-400 mx-auto animate-pulse" />
          <h2 className="text-xl font-bold uppercase tracking-tight font-sans">No active dataset selected</h2>
          <p className="text-sm text-slate-400 leading-relaxed font-sans">
            CrimeNexus operations require at least one active database registry entry to query operational analytics, trend lines, and mapping clusters.
          </p>
          <a
            href="/dataset-manager"
            className="block w-full py-3 px-4 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs uppercase tracking-wider rounded-xl transition-all shadow-lg shadow-indigo-600/10 font-sans"
          >
            Go to Dataset Manager
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Title Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div className="flex items-center gap-3.5">
          <div className="p-3 bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 rounded-2xl">
            <Map className="w-6 h-6" />
          </div>
          <div>
            <div className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest bg-indigo-500/10 border border-indigo-500/20 px-2.5 py-0.5 rounded-full w-fit font-sans">
              Geospatial Mapping Suite
            </div>
            <h1 className="text-2xl font-black text-slate-100 uppercase tracking-tight mt-1.5 font-sans">
              Geo Intelligence Engine
            </h1>
          </div>
        </div>

        {/* Right Info Panel */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 bg-slate-900/40 p-2.5 rounded-xl border border-slate-800/40 w-full sm:w-auto font-sans">
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
          {loading && (
            <div className="flex items-center justify-center gap-2 text-xs font-bold text-indigo-400 bg-indigo-500/10 border border-indigo-500/20 px-4 py-1 rounded-xl">
              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
              <span>Refreshing Maps...</span>
            </div>
          )}
        </div>
      </div>

      {/* Hierarchical Drill-Down Breadcrumb Bar */}
      <div className="glass-card p-3.5 rounded-xl border border-slate-800/60 bg-slate-900/40 backdrop-blur-md flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs font-sans">
        <div className="flex flex-wrap items-center gap-2 text-slate-300">
          <div className="flex items-center gap-1 text-slate-400 font-semibold">
            <Compass className="w-4 h-4 text-indigo-400" />
            <span>Hierarchy:</span>
          </div>

          {/* Root Level: Karnataka */}
          <button
            onClick={handleClearDrillDown}
            className={`px-2 py-1 rounded-md transition-all font-bold cursor-pointer ${
              !filters.district
                ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/20"
                : "text-slate-400 hover:text-white bg-slate-800/40 hover:bg-slate-800"
            }`}
          >
            Karnataka (State Overview)
          </button>

          {/* District Level */}
          {filters.district && (
            <>
              <ChevronRight className="w-3.5 h-3.5 text-slate-600 flex-shrink-0" />
              <button
                onClick={() => handleSelectDistrict(filters.district!)}
                className={`px-2 py-1 rounded-md transition-all font-bold cursor-pointer uppercase ${
                  !filters.police_station
                    ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/20"
                    : "text-slate-400 hover:text-white bg-slate-800/40 hover:bg-slate-800"
                }`}
              >
                District: {filters.district}
              </button>
            </>
          )}

          {/* Police Station Level */}
          {filters.police_station && (
            <>
              <ChevronRight className="w-3.5 h-3.5 text-slate-600 flex-shrink-0" />
              <span className="px-2 py-1 rounded-md bg-blue-600 text-white font-bold uppercase shadow-md shadow-blue-600/20">
                Station: {filters.police_station}
              </span>
            </>
          )}
        </div>

        {(filters.district || filters.police_station) && (
          <button
            onClick={handleClearDrillDown}
            className="flex items-center gap-1 text-[11px] font-bold text-rose-400 hover:text-rose-300 bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/20 px-2.5 py-1 rounded-lg transition-all cursor-pointer font-sans"
          >
            <X className="w-3 h-3" />
            <span>Reset Drill-Down</span>
          </button>
        )}
      </div>

      {/* Query Filters */}
      <GeoFilters filters={filters} onFiltersChange={setFilters} />

      {/* Crime Risk AI Prediction Card (Pipeline 1: Zoho Catalyst QuickML) */}
      <CrimeRiskPredictionCard filters={filters} />

      {/* Error State Banner */}
      {error && (
        <div className="p-4 bg-rose-500/10 border border-rose-500/20 rounded-2xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 text-xs text-rose-400 font-sans">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
          <button
            onClick={handleRetry}
            className="px-3 py-1.5 bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/30 rounded-lg text-[10px] uppercase font-bold transition-all cursor-pointer font-sans"
          >
            Retry Connection
          </button>
        </div>
      )}

      {/* Maps Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* District Crime Map with Real Boundaries */}
        <DistrictMap
          data={districtData}
          loading={loading}
          selectedDistrict={filters.district}
          onSelectDistrict={handleSelectDistrict}
        />
        
        {/* Police Station Map (Connected & Drilldown enabled) */}
        <StationMap
          data={stationData}
          loading={loading}
          selectedStation={filters.police_station}
          onSelectStation={handleSelectStation}
        />
        
        {/* Incident Marker Map */}
        <FirMarkerMap data={markerData} loading={loading} />
        
        {/* Crime Density Heatmap */}
        <CrimeHeatmap data={heatmapData} loading={loading} />
        
        {/* Historical Spatiotemporal DBSCAN Hotspots & QuickML Pipeline 2 Forecast */}
        <div className="lg:col-span-2 space-y-6">
          <HotspotPredictionCard filters={filters} />
          <HotspotMap data={hotspotData} loading={loading} />
        </div>
      </div>

      {/* Time-of-Day Analysis Component */}
      <TimeOfDayAnalysis data={timeOfDayData} loading={loading} />

    </div>
  );
}
