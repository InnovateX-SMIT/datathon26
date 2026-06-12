"use client";

import React, { useState } from "react";
import { Scale, ShieldAlert, Award, Database, RefreshCw, BarChart2 } from "lucide-react";
import { useDecisionSupport } from "@/hooks/useDecisionSupport";
import ResourceOptimizer from "@/components/decision-support/resource-optimizer";
import RecommendationList from "@/components/decision-support/recommendation-list";
import MonitoringPanels from "@/components/decision-support/monitoring-panels";

export default function DecisionSupportPage() {
  const {
    recommendations,
    history,
    solverResult,
    recsLoading,
    solverLoading,
    historyLoading,
    error,
    solverError,
    statusFilter,
    setStatusFilter,
    priorityFilter,
    setPriorityFilter,
    metrics,
    runSolver,
    updateStatus,
    triggerRefresh,
    setSolverResult,
  } = useDecisionSupport();

  const [activeTab, setActiveTab] = useState<"actions" | "solver" | "monitoring">("actions");

  return (
    <div className="min-h-screen py-8 px-4 sm:px-6 lg:px-8 space-y-8 animate-fade-in relative">
      {/* Background ambient lighting glows */}
      <div className="absolute top-[15%] right-[5%] w-[450px] h-[450px] rounded-full bg-indigo-500/5 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[10%] left-[10%] w-[350px] h-[350px] rounded-full bg-violet-500/5 blur-[100px] pointer-events-none" />

      {/* Header Block */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-900/80 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-indigo-500/10 border border-indigo-500/20 rounded-2xl">
              <Scale className="w-6 h-6 text-indigo-400" />
            </div>
            <div>
              <h1 className="text-3xl font-black text-slate-100 uppercase tracking-tight">
                Decision Support Center
              </h1>
              <p className="text-slate-400 text-xs font-semibold uppercase tracking-widest mt-1">
                Intelligence-to-Action Layer
              </p>
            </div>
          </div>
          <p className="text-slate-400 text-sm mt-3 max-w-2xl leading-relaxed">
            Bridge analysis and operations by converting hotspot predictions, recidivism probabilities, and criminal network clusters into tactical staffing schedules and check-in procedures.
          </p>
        </div>

        {/* Action Trigger Banner */}
        <button
          onClick={triggerRefresh}
          disabled={recsLoading}
          className="flex items-center gap-2 px-5 py-3 bg-indigo-500/10 hover:bg-indigo-500/15 border border-indigo-500/20 hover:border-indigo-500/40 text-indigo-400 hover:text-indigo-300 font-extrabold text-xs uppercase tracking-wider rounded-2xl shadow-lg transition-all w-fit cursor-pointer disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${recsLoading ? "animate-spin" : ""}`} />
          Run Recs Generator
        </button>
      </div>

      {/* Metrics Banner */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Total Actions */}
        <div className="bg-slate-950/40 border border-slate-900/80 rounded-3xl p-5 backdrop-blur-md relative overflow-hidden flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-[9px] font-bold text-slate-500 uppercase tracking-wider block">Total Suggestions</span>
            <span className="text-3xl font-black text-slate-200 font-mono block">{metrics.totalCount}</span>
          </div>
          <div className="p-3 bg-slate-900 border border-slate-800 rounded-xl text-slate-400">
            <BarChart2 className="w-5 h-5" />
          </div>
        </div>

        {/* Pending Actions */}
        <div className="bg-slate-950/40 border border-slate-900/80 rounded-3xl p-5 backdrop-blur-md relative overflow-hidden flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-[9px] font-bold text-slate-500 uppercase tracking-wider block">Pending Actions</span>
            <span className="text-3xl font-black text-amber-400 font-mono block">{metrics.pendingCount}</span>
          </div>
          <div className="p-3 bg-slate-900 border border-slate-800 rounded-xl text-amber-400">
            <ShieldAlert className="w-5 h-5 animate-pulse" />
          </div>
        </div>

        {/* Resolved Actions */}
        <div className="bg-slate-950/40 border border-slate-900/80 rounded-3xl p-5 backdrop-blur-md relative overflow-hidden flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-[9px] font-bold text-slate-500 uppercase tracking-wider block">Resolved Items</span>
            <span className="text-3xl font-black text-green-400 font-mono block">{metrics.resolvedCount}</span>
          </div>
          <div className="p-3 bg-slate-900 border border-slate-800 rounded-xl text-green-400">
            <Award className="w-5 h-5" />
          </div>
        </div>

        {/* Solver Runs */}
        <div className="bg-slate-950/40 border border-slate-900/80 rounded-3xl p-5 backdrop-blur-md relative overflow-hidden flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-[9px] font-bold text-slate-500 uppercase tracking-wider block">LP Solver Scenarios</span>
            <span className="text-3xl font-black text-indigo-400 font-mono block">{history.length}</span>
          </div>
          <div className="p-3 bg-slate-900 border border-slate-800 rounded-xl text-indigo-400">
            <Database className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Tabs Menu */}
      <div className="flex border-b border-slate-900">
        <div className="flex gap-2">
          <button
            onClick={() => setActiveTab("actions")}
            className={`pb-4 px-4 text-xs uppercase tracking-widest font-black transition-all relative cursor-pointer ${
              activeTab === "actions"
                ? "text-indigo-400 border-b-2 border-indigo-500"
                : "text-slate-500 hover:text-slate-350"
            }`}
          >
            Priority Actions
          </button>
          <button
            onClick={() => setActiveTab("solver")}
            className={`pb-4 px-4 text-xs uppercase tracking-widest font-black transition-all relative cursor-pointer ${
              activeTab === "solver"
                ? "text-indigo-400 border-b-2 border-indigo-500"
                : "text-slate-500 hover:text-slate-350"
            }`}
          >
            Resource Optimizer
          </button>
          <button
            onClick={() => setActiveTab("monitoring")}
            className={`pb-4 px-4 text-xs uppercase tracking-widest font-black transition-all relative cursor-pointer ${
              activeTab === "monitoring"
                ? "text-indigo-400 border-b-2 border-indigo-500"
                : "text-slate-500 hover:text-slate-350"
            }`}
          >
            Target Monitoring
          </button>
        </div>
      </div>

      {/* Global Error Bar */}
      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-3xl text-red-400 text-xs flex gap-2.5 items-center max-w-4xl animate-shake">
          <ShieldAlert className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Tab Panels */}
      <div className="min-h-[400px]">
        {activeTab === "actions" && (
          <RecommendationList
            recommendations={recommendations}
            recsLoading={recsLoading}
            statusFilter={statusFilter}
            setStatusFilter={setStatusFilter}
            priorityFilter={priorityFilter}
            setPriorityFilter={setPriorityFilter}
            updateStatus={updateStatus}
            triggerRefresh={triggerRefresh}
          />
        )}

        {activeTab === "solver" && (
          <ResourceOptimizer
            history={history}
            solverResult={solverResult}
            solverLoading={solverLoading}
            solverError={solverError}
            runSolver={runSolver}
            setSolverResult={setSolverResult}
          />
        )}

        {activeTab === "monitoring" && (
          <MonitoringPanels recommendations={recommendations} />
        )}
      </div>

      {/* Footer System Roster */}
      <div className="pt-8 border-t border-slate-900 flex justify-between items-center text-[10px] font-mono text-slate-600 tracking-wider">
        <span>SECURE INTELLIGENCE-TO-ACTION INFRASTRUCTURE</span>
        <span>PHASE 7 ENGINE ACTIVE</span>
      </div>
    </div>
  );
}
