"use client";

import React, { useState, useEffect } from "react";
import { 
  Scale, 
  ShieldAlert, 
  Award, 
  Database, 
  RefreshCw, 
  BarChart2,
  ListFilter,
  Activity,
  History,
  Cpu
} from "lucide-react";
import { useDecisionSupport } from "@/hooks/useDecisionSupport";
import ResourceOptimizer from "@/components/decision-support/resource-optimizer";
import RecommendationList from "@/components/decision-support/recommendation-list";
import MonitoringPanels from "@/components/decision-support/monitoring-panels";
import { fetchDatasets, DatasetInfo } from "@/services/dataset.service";

export default function DecisionSupportPage() {
  const {
    recommendations,
    history,
    syncHistory,
    solverResult,
    recsLoading,
    solverLoading,
    historyLoading,
    syncHistoryLoading,
    syncPipelineLoading,
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
    runPipelineSync,
    setSolverResult,
  } = useDecisionSupport();

  const [activeTab, setActiveTab] = useState<"actions" | "solver" | "monitoring" | "sync-history">("actions");
  
  // Local state to show active datasets info
  const [activeDatasets, setActiveDatasets] = useState<DatasetInfo[]>([]);
  const [datasetsLoading, setDatasetsLoading] = useState(true);

  useEffect(() => {
    document.title = "Decision Support | CrimeNexus";
    
    // Load dataset info
    const loadDatasets = async () => {
      try {
        const list = await fetchDatasets();
        setActiveDatasets(list.filter(d => d.is_active));
      } catch (err) {
        console.error("Failed to load active datasets details", err);
      } finally {
        setDatasetsLoading(false);
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
    <div className="space-y-8 animate-fade-in relative">
      {/* Background ambient lighting glows */}
      <div className="absolute top-[15%] right-[5%] w-[450px] h-[450px] rounded-full bg-indigo-500/5 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[10%] left-[10%] w-[350px] h-[350px] rounded-full bg-violet-500/5 blur-[100px] pointer-events-none" />

      {/* Header Block */}
      <div className="flex flex-col xl:flex-row xl:items-center justify-between gap-6 border-b border-slate-900/80 pb-6">
        <div className="space-y-2">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-indigo-500/10 border border-indigo-500/20 rounded-2xl">
              <Scale className="w-6 h-6 text-indigo-400" />
            </div>
            <div>
              <h1 className="text-3xl font-black text-slate-100 uppercase tracking-tight">
                Decision Support Center
              </h1>
            </div>
          </div>
          
          {/* Metadata Badges */}
          <div className="flex flex-wrap items-center gap-2.5 pt-1">
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Active Workspace:</span>
            {datasetsLoading ? (
              <span className="text-[10px] font-mono text-slate-600 animate-pulse">Loading datasets...</span>
            ) : activeDatasets.length === 0 ? (
              <span className="px-2 py-0.5 rounded bg-red-500/10 border border-red-500/20 text-red-400 text-[9px] font-bold uppercase tracking-wider">
                No Active Datasets
              </span>
            ) : (
              activeDatasets.map(d => (
                <span key={d.id} className="px-2 py-0.5 rounded bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-[9px] font-mono font-bold uppercase">
                  {d.original_filename}
                </span>
              ))
            )}
            
            {syncHistory.length > 0 && (
              <span className="px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-[9px] font-mono font-bold uppercase flex items-center gap-1">
                <Cpu className="w-3 h-3" />
                Model: {syncHistory[0].model_version}
              </span>
            )}
          </div>
        </div>

        {/* Sync Controls */}
        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={runPipelineSync}
            disabled={syncPipelineLoading || recsLoading}
            className="flex items-center gap-2 px-5 py-3 bg-indigo-650 hover:bg-indigo-650/80 border border-indigo-500/40 text-slate-100 font-extrabold text-xs uppercase tracking-wider rounded-2xl shadow-lg transition-all w-fit cursor-pointer disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${syncPipelineLoading ? "animate-spin" : ""}`} />
            Sync Intelligence Pipeline
          </button>
          
          <button
            onClick={triggerRefresh}
            disabled={recsLoading || syncPipelineLoading}
            className="flex items-center gap-2 px-5 py-3 bg-slate-900 hover:bg-slate-850 border border-slate-800 hover:border-slate-700 text-slate-300 hover:text-slate-100 font-extrabold text-xs uppercase tracking-wider rounded-2xl shadow-lg transition-all w-fit cursor-pointer disabled:opacity-50"
          >
            <Activity className={`w-4 h-4 ${recsLoading ? "animate-spin" : ""}`} />
            Re-run Recs Engine
          </button>
        </div>
      </div>

      {/* Syncing Overlay Loader */}
      {syncPipelineLoading && (
        <div className="p-4 bg-indigo-500/10 border border-indigo-500/20 rounded-3xl text-indigo-300 text-xs flex items-center gap-3 max-w-4xl animate-pulse">
          <RefreshCw className="w-4 h-4 shrink-0 animate-spin" />
          <span>Synchronizing active dataset analytics, retraining predictions, updating alerts registry, and compiling suggestions...</span>
        </div>
      )}

      {/* Metrics Banner */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Total Actions */}
        <div className="glass-card rounded-2xl p-5 border border-slate-800/60 relative overflow-hidden flex items-center justify-between transition-all duration-300 hover:border-slate-700/60">
          <div className="space-y-1">
            <span className="text-[9px] font-bold text-slate-500 uppercase tracking-wider block">Total Suggestions</span>
            <span className="text-3xl font-black text-slate-200 font-mono block">{metrics.totalCount}</span>
          </div>
          <div className="p-3 bg-slate-900 border border-slate-800 rounded-xl text-slate-400">
            <BarChart2 className="w-5 h-5" />
          </div>
        </div>

        {/* Pending Actions */}
        <div className="glass-card rounded-2xl p-5 border border-slate-800/60 relative overflow-hidden flex items-center justify-between transition-all duration-300 hover:border-slate-700/60">
          <div className="space-y-1">
            <span className="text-[9px] font-bold text-slate-500 uppercase tracking-wider block">Pending Actions</span>
            <span className="text-3xl font-black text-amber-400 font-mono block">{metrics.pendingCount}</span>
          </div>
          <div className="p-3 bg-slate-900 border border-slate-800 rounded-xl text-amber-400">
            <ShieldAlert className="w-5 h-5 animate-pulse" />
          </div>
        </div>

        {/* Resolved Actions */}
        <div className="glass-card rounded-2xl p-5 border border-slate-800/60 relative overflow-hidden flex items-center justify-between transition-all duration-300 hover:border-slate-700/60">
          <div className="space-y-1">
            <span className="text-[9px] font-bold text-slate-500 uppercase tracking-wider block">Resolved Items</span>
            <span className="text-3xl font-black text-green-400 font-mono block">{metrics.resolvedCount}</span>
          </div>
          <div className="p-3 bg-slate-900 border border-slate-800 rounded-xl text-green-400">
            <Award className="w-5 h-5" />
          </div>
        </div>

        {/* Solver Runs */}
        <div className="glass-card rounded-2xl p-5 border border-slate-800/60 relative overflow-hidden flex items-center justify-between transition-all duration-300 hover:border-slate-700/60">
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
          <button
            onClick={() => setActiveTab("sync-history")}
            className={`pb-4 px-4 text-xs uppercase tracking-widest font-black transition-all relative cursor-pointer ${
              activeTab === "sync-history"
                ? "text-indigo-400 border-b-2 border-indigo-500"
                : "text-slate-500 hover:text-slate-350"
            }`}
          >
            Sync History
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
        
        {activeTab === "sync-history" && (
          <div className="glass-card rounded-3xl border border-slate-900/80 p-6 space-y-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-slate-900 border border-slate-800 rounded-xl text-slate-400">
                <History className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-md font-bold text-slate-100 uppercase tracking-wider">Sync Registry</h3>
                <p className="text-slate-500 text-xs mt-0.5">Audit trail of system synchronization, datasets updates, model runs and alert metrics.</p>
              </div>
            </div>
            
            {syncHistoryLoading ? (
              <div className="space-y-3">
                {[1, 2].map((n) => (
                  <div key={n} className="bg-slate-950/20 border border-slate-900/60 rounded-2xl h-[50px] animate-pulse" />
                ))}
              </div>
            ) : syncHistory.length === 0 ? (
              <div className="bg-slate-950/20 border border-dashed border-slate-900 rounded-2xl p-8 text-center text-xs text-slate-500 italic">
                No pipeline synchronization history found. Click "Sync Intelligence Pipeline" above.
              </div>
            ) : (
              <div className="overflow-x-auto border border-slate-900/80 rounded-2xl">
                <table className="w-full text-left text-xs text-slate-300 font-medium">
                  <thead>
                    <tr className="border-b border-slate-900 bg-slate-950/40 text-[9px] uppercase tracking-wider text-slate-500">
                      <th className="p-4 pl-5">ID</th>
                      <th className="p-4">Timestamp</th>
                      <th className="p-4">Dataset IDs</th>
                      <th className="p-4">Model Version</th>
                      <th className="p-4 text-center">Alerts Count</th>
                      <th className="p-4 text-center font-bold text-indigo-400">Recs Count</th>
                      <th className="p-4 pr-5 text-right">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {syncHistory.map((log) => (
                      <tr key={log.id} className="border-b border-slate-900 bg-slate-950/20 hover:bg-slate-900/10 transition-colors">
                        <td className="p-4 pl-5 font-mono text-slate-500">#{log.id}</td>
                        <td className="p-4">{new Date(log.created_at).toLocaleString("en-IN")}</td>
                        <td className="p-4 font-mono text-indigo-400">{log.dataset_ids}</td>
                        <td className="p-4 font-semibold text-slate-300">{log.model_version}</td>
                        <td className="p-4 text-center font-mono text-amber-500 font-bold">{log.alert_count}</td>
                        <td className="p-4 text-center font-mono text-indigo-400 font-bold">{log.generated_recommendations_count}</td>
                        <td className="p-4 pr-5 text-right">
                          <span className="px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[10px] font-bold uppercase tracking-wider font-mono">
                            {log.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </div>

    </div>
  );
}
