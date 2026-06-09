"use client";

import React, { useEffect, useState } from "react";
import { ShieldAlert, Activity, Users, Shield } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import {
  fetchDashboardSummary,
  fetchCrimeTrend,
  fetchCategoryBreakdown,
  fetchDistrictRanking,
  fetchRecentCrimes,
  fetchSystemStatus,
} from "@/services/dashboardService";
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
  const { user } = useAuth();
  const [mounted, setMounted] = useState(false);

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
    document.title = "Command Center | Predictive Guardians";
    setMounted(true);
  }, []);

  // Parallel Loader
  const loadAll = async () => {
    await Promise.allSettled([
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
    } catch {
      setSummaryError("Failed to load summary statistics.");
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
    } catch {
      setTrendError("Failed to load crime trends.");
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
    } catch {
      setCategoriesError("Failed to load categories breakdown.");
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
    } catch {
      setDistrictsError("Failed to load district ranks.");
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
    } catch {
      setRecentError("Failed to load recent crimes list.");
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
    } catch {
      setStatusError("Failed to load system health.");
    } finally {
      setStatusLoading(false);
    }
  };

  const getRoleBadgeClass = (role: string) => {
    switch (role) {
      case "ADMIN":
        return "bg-indigo-500/20 text-indigo-400 border border-indigo-500/30";
      case "SUPERINTENDENT":
        return "bg-amber-500/20 text-amber-400 border border-amber-500/30";
      case "OFFICER":
        return "bg-green-500/20 text-green-400 border border-green-500/30";
      default:
        return "bg-slate-500/20 text-slate-400 border border-slate-500/30";
    }
  };

  return (
    <div className="space-y-6 flex flex-col min-w-0">
      {/* 1. Page Header */}
      <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-100 uppercase tracking-tight">
            Command Center
          </h1>
          <p className="text-xs font-semibold text-slate-400 tracking-wide mt-0.5">
            Real-Time Crime Intelligence Overview
          </p>
        </div>
        
        {/* Right Info Panel */}
        <div className="flex items-center gap-4 self-stretch md:self-auto justify-between bg-slate-900/40 p-2.5 rounded-xl border border-slate-800/40">
          {mounted && currentTime && (
            <div className="text-xs font-mono font-bold tracking-wider text-indigo-400 px-3 py-1 bg-indigo-500/5 border border-indigo-500/10 rounded-lg">
              {currentTime}
            </div>
          )}
          {user && (
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-slate-200 uppercase truncate max-w-[150px]">
                {user.name}
              </span>
              <span className={`text-[10px] font-extrabold tracking-wider px-2 py-0.5 rounded border ${getRoleBadgeClass(user.role)}`}>
                {user.role}
              </span>
            </div>
          )}
        </div>
      </header>

      {/* 2. KPI Section */}
      <section className="grid grid-cols-2 lg:grid-cols-4 gap-4 w-full">
        <KPICard
          title="Total Crimes"
          value={summary?.total_crimes ?? 0}
          subtitle="Registered cases"
          icon={ShieldAlert}
          accentColor="indigo"
          loading={summaryLoading}
          error={summaryError ?? undefined}
          onRetry={loadSummary}
        />
        <KPICard
          title="Active Cases"
          value={summary?.active_cases ?? 0}
          subtitle="Under active review"
          icon={Activity}
          accentColor="amber"
          loading={summaryLoading}
          error={summaryError ?? undefined}
          onRetry={loadSummary}
        />
        <KPICard
          title="Citizen Impact"
          value={summary?.total_victims ?? 0}
          subtitle="Recorded victims"
          icon={Users}
          accentColor="red"
          loading={summaryLoading}
          error={summaryError ?? undefined}
          onRetry={loadSummary}
        />
        <KPICard
          title="High-Risk Offenders"
          value={summary?.high_risk_criminals ?? 0}
          subtitle="Risk rating >= 7.0"
          icon={Shield}
          accentColor="red"
          loading={summaryLoading}
          error={summaryError ?? undefined}
          onRetry={loadSummary}
        />
      </section>

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
