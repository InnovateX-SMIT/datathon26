"use client";

import React, { useEffect, useState } from "react";
import { ShieldAlert, Activity, Users, Shield, RefreshCw } from "lucide-react";
import {
  fetchDashboardSummary,
  fetchCrimeTrend,
  fetchCategoryBreakdown,
  fetchDistrictRanking,
  fetchRecentCrimes,
  fetchSystemStatus,
} from "@/services/dashboardService";
import { fetchDatasets, DatasetInfo } from "@/services/dataset.service";
import type {
  DashboardSummary,
  TrendDataPoint,
  CategoryDataPoint,
  DistrictDataPoint,
  RecentCrimeItem,
  SystemStatus,
} from "@/types/dashboard";

import KPICard from "@/components/dashboard/KPICard";
import CrimeTrendChart from "@/components/dashboard/CrimeTrendChart";
import CategoryChart from "@/components/dashboard/CategoryChart";
import DistrictChart from "@/components/dashboard/DistrictChart";
import RecentCrimesTable from "@/components/dashboard/RecentCrimesTable";
import SystemStatusBar from "@/components/dashboard/SystemStatusBar";

export default function DashboardPage() {
  const [mounted, setMounted] = useState(false);

  // Active datasets state
  const [activeDatasets, setActiveDatasets] = useState<DatasetInfo[]>([]);
  const [activeDatasetsLoading, setActiveDatasetsLoading] = useState(true);

  // Data states
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [trend, setTrend] = useState<TrendDataPoint[]>([]);
  const [categories, setCategories] = useState<CategoryDataPoint[]>([]);
  const [districts, setDistricts] = useState<DistrictDataPoint[]>([]);
  const [recentCrimes, setRecentCrimes] = useState<RecentCrimeItem[]>([]);
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);

  // Loading states
  const [summaryLoading, setSummaryLoading] = useState(true);
  const [trendLoading, setTrendLoading] = useState(true);
  const [categoriesLoading, setCategoriesLoading] = useState(true);
  const [districtsLoading, setDistrictsLoading] = useState(true);
  const [recentLoading, setRecentLoading] = useState(true);
  const [statusLoading, setStatusLoading] = useState(true);

  // Error states
  const [summaryError, setSummaryError] = useState<string | null>(null);
  const [trendError, setTrendError] = useState<string | null>(null);
  const [categoriesError, setCategoriesError] = useState<string | null>(null);
  const [districtsError, setDistrictsError] = useState<string | null>(null);
  const [recentError, setRecentError] = useState<string | null>(null);
  const [statusError, setStatusError] = useState<string | null>(null);

  // Live clock
  const [currentTime, setCurrentTime] = useState<string>("");

  // Set page title and flag mounted
  useEffect(() => {
    document.title = "Command Center | CrimeNexus";
    setMounted(true);
  }, []);

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

  // Parallel Loader
  const loadAll = async () => {
    await Promise.allSettled([
      loadActiveDatasets(),
      loadSummary(),
      loadTrend(),
      loadCategories(),
      loadDistricts(),
      loadRecentCrimes(),
      loadSystemStatus(),
    ]);
  };

  useEffect(() => {
    loadAll();

    const handleDatasetChange = () => {
      loadAll();
    };
    window.addEventListener("activeDatasetChanged", handleDatasetChange);
    return () => {
      window.removeEventListener("activeDatasetChanged", handleDatasetChange);
    };
  }, []);

  // Clock tick effect
  useEffect(() => {
    const tick = () => {
      setCurrentTime(
        new Date().toLocaleTimeString("en-IN", {
          hour: "2-digit",
          minute: "2-digit",
          second: "2-digit",
        })
      );
    };
    tick();
    const interval = setInterval(tick, 1000);
    return () => clearInterval(interval);
  }, []);

  // Loader implementations
  const loadSummary = async () => {
    setSummaryLoading(true);
    setSummaryError(null);
    try {
      const data = await fetchDashboardSummary();
      setSummary(data);
    } catch (err: any) {
      setSummaryError(err.message || "Failed to load summary statistics.");
    } finally {
      setSummaryLoading(false);
    }
  };

  const loadTrend = async () => {
    setTrendLoading(true);
    setTrendError(null);
    try {
      const data = await fetchCrimeTrend(30);
      setTrend(data);
    } catch (err: any) {
      setTrendError(err.message || "Failed to load crime trends.");
    } finally {
      setTrendLoading(false);
    }
  };

  const loadCategories = async () => {
    setCategoriesLoading(true);
    setCategoriesError(null);
    try {
      const data = await fetchCategoryBreakdown();
      setCategories(data);
    } catch (err: any) {
      setCategoriesError(err.message || "Failed to load categories breakdown.");
    } finally {
      setCategoriesLoading(false);
    }
  };

  const loadDistricts = async () => {
    setDistrictsLoading(true);
    setDistrictsError(null);
    try {
      const data = await fetchDistrictRanking();
      setDistricts(data);
    } catch (err: any) {
      setDistrictsError(err.message || "Failed to load district ranks.");
    } finally {
      setDistrictsLoading(false);
    }
  };

  const loadRecentCrimes = async () => {
    setRecentLoading(true);
    setRecentError(null);
    try {
      const data = await fetchRecentCrimes();
      setRecentCrimes(data);
    } catch (err: any) {
      setRecentError(err.message || "Failed to load recent crimes list.");
    } finally {
      setRecentLoading(false);
    }
  };

  const loadSystemStatus = async () => {
    setStatusLoading(true);
    setStatusError(null);
    try {
      const data = await fetchSystemStatus();
      setSystemStatus(data);
    } catch (err: any) {
      setStatusError(err.message || "Failed to load system health.");
    } finally {
      setStatusLoading(false);
    }
  };

  // ── EMPTY STATE RENDERING ──
  const isNoActiveDataset =
    !summaryLoading &&
    !activeDatasetsLoading &&
    (summaryError?.includes("No active dataset") || activeDatasets.length === 0);

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
    <div className="space-y-6 flex flex-col min-w-0">
      {/* 1. Page Header */}
      <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-100 uppercase tracking-tight">
            Command Center
          </h1>
        </div>

        {/* Right Info Panel */}
        <div className="flex flex-col md:flex-row items-stretch md:items-center gap-3 bg-slate-900/40 p-2.5 rounded-xl border border-slate-800/40 w-full md:w-auto">
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
          {mounted && currentTime && (
            <div className="text-xs font-mono font-bold tracking-wider text-indigo-400 px-3 py-1 bg-indigo-500/5 border border-indigo-500/10 rounded-lg text-center">
              {currentTime}
            </div>
          )}
        </div>
      </header>

      {/* 2. KPI Section */}
      {summary?.total_crimes === 0 ? (
        <section className="py-12">
          <div className="p-8 bg-slate-900/45 border border-slate-800/80 rounded-3xl text-center max-w-xl mx-auto space-y-4 backdrop-blur-md">
            <ShieldAlert className="w-12 h-12 text-slate-500 mx-auto animate-pulse" />
            <h3 className="text-base font-extrabold text-slate-200 uppercase tracking-tight">
              Empty Operational Dataset
            </h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              No crime logs, victim listings, or criminal registries are associated with the currently active dataset. To query operational analytics, switch datasets via the Dataset Manager or upload a valid csv/xlsx file.
            </p>
          </div>
        </section>
      ) : (
        <>
          <section className="grid grid-cols-2 lg:grid-cols-4 gap-4 w-full">
            <KPICard
              title="Total Incident Reports"
              value={summary?.total_crimes ?? 0}
              subtitle="Registered crime events"
              icon={ShieldAlert}
              accentColor="indigo"
              loading={summaryLoading}
              error={summaryError ?? undefined}
              onRetry={loadSummary}
            />
            <KPICard
              title="Active Investigations"
              value={summary?.active_cases ?? 0}
              subtitle="Open cases (non-closed)"
              icon={Activity}
              accentColor="amber"
              loading={summaryLoading}
              error={summaryError ?? undefined}
              onRetry={loadSummary}
            />
            <KPICard
              title="Crime Resolution Rate"
              value={
                summary?.crime_resolution_rate !== undefined
                  ? `${summary.crime_resolution_rate.toFixed(2)}%`
                  : "0.00%"
              }
              subtitle="Percentage of cases closed"
              icon={Users}
              accentColor="green"
              loading={summaryLoading}
              error={summaryError ?? undefined}
              onRetry={loadSummary}
            />
            <KPICard
              title="Average Severity Score"
              value={
                summary?.average_severity !== undefined
                  ? `${summary.average_severity.toFixed(2)} / 10`
                  : "0.00 / 10"
              }
              subtitle="Mean severity rating (1-10)"
              icon={Shield}
              accentColor="red"
              loading={summaryLoading}
              error={summaryError ?? undefined}
              onRetry={loadSummary}
            />
          </section>

          {/* Secondary Scope Stats Row */}
          {summary && !summaryLoading && !summaryError && (
            <div className="bg-slate-950/40 p-4 border border-slate-900 rounded-2xl backdrop-blur-md flex flex-wrap items-center justify-around gap-4 text-xs font-semibold text-slate-400">
              <div className="flex items-center gap-2">
                <span className="text-slate-500">Offender Registry:</span>
                <span className="text-slate-200 font-bold">
                  {summary.total_criminals.toLocaleString()} Criminals
                </span>
                <span className="text-[10px] text-rose-400 font-bold bg-rose-500/10 px-1.5 py-0.5 rounded border border-rose-500/20">
                  {summary.high_risk_criminals.toLocaleString()} High Risk
                </span>
              </div>
              <div className="h-4 w-px bg-slate-800 hidden sm:block" />
              <div className="flex items-center gap-2">
                <span className="text-slate-500">Citizen Impact:</span>
                <span className="text-slate-200 font-bold">
                  {summary.total_victims.toLocaleString()} Victims
                </span>
              </div>
              <div className="h-4 w-px bg-slate-800 hidden sm:block" />
              <div className="flex items-center gap-2">
                <span className="text-slate-500">Jurisdictional Coverage:</span>
                <span className="text-slate-200 font-bold">
                  {summary.districts_count.toLocaleString()} Districts
                </span>
                <span className="text-slate-500">/</span>
                <span className="text-slate-200 font-bold">
                  {summary.stations_count.toLocaleString()} Stations
                </span>
              </div>
            </div>
          )}

          {/* 3. Charts Row (Trend 60% + Category 40%) */}
          <section className="grid grid-cols-1 lg:grid-cols-5 gap-4 w-full">
            <div className="lg:col-span-3 min-w-0">
              <CrimeTrendChart
                data={trend}
                loading={trendLoading}
                error={trendError ?? undefined}
                onRetry={loadTrend}
              />
            </div>
            <div className="lg:col-span-2 min-w-0">
              <CategoryChart
                data={categories}
                loading={categoriesLoading}
                error={categoriesError ?? undefined}
                onRetry={loadCategories}
              />
            </div>
          </section>

          {/* 4. District Ranking Chart */}
          <section className="w-full">
            <DistrictChart
              data={districts}
              loading={districtsLoading}
              error={districtsError ?? undefined}
              onRetry={loadDistricts}
            />
          </section>

          {/* 5. Recent Crimes Table */}
          <section className="w-full">
            <RecentCrimesTable
              data={recentCrimes}
              loading={recentLoading}
              error={recentError ?? undefined}
              onRetry={loadRecentCrimes}
            />
          </section>
        </>
      )}

      {/* 6. System Status Bar */}
      <section className="w-full">
        <SystemStatusBar
          status={systemStatus}
          loading={statusLoading}
          error={statusError ?? undefined}
          onRetry={loadSystemStatus}
        />
      </section>
    </div>
  );
}
