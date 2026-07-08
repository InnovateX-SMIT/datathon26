"use client";

import React, { useState } from "react";
import { Bell, ShieldAlert, Activity, RefreshCw } from "lucide-react";
import { useAlerts } from "@/hooks/useAlerts";
import AlertStats from "@/components/alerts/alert-stats";
import AlertList from "@/components/alerts/alert-list";
import MonitoringView from "@/components/alerts/monitoring-view";

export default function AlertsPage() {
  const {
    alerts,
    summary,
    alertsLoading,
    summaryLoading,
    actionLoading,
    error,
    statusFilter,
    setStatusFilter,
    severityFilter,
    setSeverityFilter,
    sourceFilter,
    setSourceFilter,
    triggerRefresh,
    updateStatus,
  } = useAlerts();

  const [activeTab, setActiveTab] = useState<"dispatch" | "logs">("dispatch");

  return (
    <div className="min-h-screen py-8 px-4 sm:px-6 lg:px-8 space-y-8 animate-fade-in relative">
      {/* Background glowing gradients */}
      <div className="absolute top-[10%] right-[10%] w-[400px] h-[400px] rounded-full bg-rose-500/5 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[20%] left-[5%] w-[350px] h-[350px] rounded-full bg-indigo-500/5 blur-[100px] pointer-events-none" />

      {/* Header Block */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-900/80 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-rose-500/10 border border-rose-500/20 rounded-2xl">
              <Bell className="w-6 h-6 text-rose-400" />
            </div>
            <div>
              <h1 className="text-3xl font-black text-slate-100 uppercase tracking-tight">
                Operational Alerts Panel
              </h1>
            </div>
          </div>
        </div>

        {/* Global Manual Run Trigger */}
        <button
          onClick={triggerRefresh}
          disabled={alertsLoading}
          className="flex items-center gap-2 px-5 py-3 bg-rose-500/10 hover:bg-rose-500/15 border border-rose-500/20 hover:border-rose-500/40 text-rose-400 hover:text-rose-300 font-extrabold text-xs uppercase tracking-wider rounded-2xl shadow-lg transition-all w-fit cursor-pointer disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${alertsLoading ? "animate-spin" : ""}`} />
          Run Detection Rules
        </button>
      </div>

      {/* Operational Metrics Cards */}
      <AlertStats summary={summary} loading={summaryLoading} />

      {/* Tabs Menu */}
      <div className="flex border-b border-slate-900" role="tablist" aria-label="Alert views">
        <div className="flex gap-2">
          <button
            role="tab"
            aria-selected={activeTab === "dispatch"}
            aria-controls="tab-dispatch"
            onClick={() => setActiveTab("dispatch")}
            className={`pb-4 px-4 text-xs uppercase tracking-widest font-black transition-all relative cursor-pointer flex items-center gap-1.5 ${
              activeTab === "dispatch"
                ? "text-rose-400 border-b-2 border-rose-500"
                : "text-slate-500 hover:text-slate-350"
            }`}
          >
            <Activity className="w-4 h-4" />
            Tactical Dispatch Triage
          </button>
          <button
            role="tab"
            aria-selected={activeTab === "logs"}
            aria-controls="tab-logs"
            onClick={() => setActiveTab("logs")}
            className={`pb-4 px-4 text-xs uppercase tracking-widest font-black transition-all relative cursor-pointer flex items-center gap-1.5 ${
              activeTab === "logs"
                ? "text-rose-400 border-b-2 border-rose-500"
                : "text-slate-500 hover:text-slate-350"
            }`}
          >
            <Bell className="w-4 h-4" />
            Alert Logs & Archive
          </button>
        </div>
      </div>

      {/* Global Error Banner */}
      {error && (
        <div role="alert" className="p-4 bg-rose-500/10 border border-rose-500/20 rounded-3xl text-rose-400 text-xs flex gap-2.5 items-center max-w-4xl animate-shake">
          <ShieldAlert className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Tab Panels */}
      <div className="min-h-[450px]" role="tabpanel" id={activeTab === "dispatch" ? "tab-dispatch" : "tab-logs"}>
        {activeTab === "dispatch" && (
          <MonitoringView
            alerts={alerts}
            onUpdateStatus={updateStatus}
            actionLoading={actionLoading}
          />
        )}

        {activeTab === "logs" && (
          <AlertList
            alerts={alerts}
            loading={alertsLoading}
            onUpdateStatus={updateStatus}
            onRefresh={triggerRefresh}
            statusFilter={statusFilter}
            setStatusFilter={setStatusFilter}
            severityFilter={severityFilter}
            setSeverityFilter={setSeverityFilter}
            sourceFilter={sourceFilter}
            setSourceFilter={setSourceFilter}
          />
        )}
      </div>

      {/* Footer System Roster */}
      <div className="pt-6 mt-4 border-t border-slate-900/60 flex justify-between items-center text-[9px] font-mono text-slate-700/60 tracking-widest select-none">
        <span>CRIME INTELLIGENCE COMMAND INFRASTRUCTURE</span>
        <span>PHASE 8 RULE ENGINE ACTIVE</span>
      </div>
    </div>
  );
}
