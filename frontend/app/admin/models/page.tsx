"use client";

import React, { useEffect, useState, useRef } from "react";
import {
  BrainCircuit,
  RefreshCw,
  Trash2,
  CheckCircle,
  AlertCircle,
  Play,
  FileText,
  GitCompare,
  TrendingUp,
  Activity,
  Layers,
  ArrowRight,
  ShieldCheck,
  Zap,
  Sliders,
  History
} from "lucide-react";
import { fetchDatasets, DatasetInfo } from "@/features/admin/services/database-service";
import {
  fetchModelHistory,
  trainModel,
  markProductionModel,
  deleteModel,
  compareModels,
  fetchModelLogs,
  MLModelInfo,
  CompareResult
} from "@/features/admin/services/model-service";

const MODEL_LABELS: Record<string, string> = {
  repeat_offender: "Suspect Recidivism Classifier",
  crime_type: "Incident Category Classifier",
  crime_risk: "Incident Severity Regressor",
  hotspot: "Emerging Hotspot Classifier"
};

export default function MLModelRegistryPage() {
  const [mounted, setMounted] = useState(false);
  const [activeDatasets, setActiveDatasets] = useState<DatasetInfo[]>([]);
  const [history, setHistory] = useState<MLModelInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  // Errors/Success
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Logs modal
  const [logModalOpen, setLogModalOpen] = useState(false);
  const [selectedModelForLogs, setSelectedModelForLogs] = useState<MLModelInfo | null>(null);
  const [logsText, setLogsText] = useState("");
  const [logsLoading, setLogsLoading] = useState(false);

  // Comparison
  const [compareType, setCompareType] = useState<string>("repeat_offender");
  const [compareModel1, setCompareModel1] = useState<number | null>(null);
  const [compareModel2, setCompareModel2] = useState<number | null>(null);
  const [compareResult, setCompareResult] = useState<CompareResult | null>(null);
  const [compareError, setCompareError] = useState<string | null>(null);
  const [compareLoading, setCompareLoading] = useState(false);

  // Polling interval ref
  const pollingRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    document.title = "ML Model Registry | Predictive Guardians";
    setMounted(true);
    loadAll();

    // Setup polling every 4 seconds to watch training tasks
    pollingRef.current = setInterval(() => {
      silentReloadHistory();
    }, 4000);

    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current);
    };
  }, []);

  const loadAll = async () => {
    setLoading(true);
    setError(null);
    try {
      await Promise.all([loadActiveDatasets(), reloadHistory()]);
    } catch (err: any) {
      setError(err.message || "Failed to load ML registry console.");
    } finally {
      setLoading(false);
    }
  };

  const loadActiveDatasets = async () => {
    const data = await fetchDatasets();
    setActiveDatasets(data.filter((d) => d.is_active));
  };

  const reloadHistory = async () => {
    const data = await fetchModelHistory();
    setHistory(data);
  };

  const silentReloadHistory = async () => {
    try {
      const data = await fetchModelHistory();
      setHistory(data);
    } catch (err) {
      console.error("Failed silent reload of ML history", err);
    }
  };

  const handleTrain = async (type: string) => {
    setActionLoading(`train_${type}`);
    setError(null);
    setSuccess(null);
    try {
      const record = await trainModel(type);
      setSuccess(`Model retraining task for "${MODEL_LABELS[type]}" successfully queued (ID: ${record.id}).`);
      await reloadHistory();
    } catch (err: any) {
      setError(err.message || "Failed to trigger retraining.");
    } finally {
      setActionLoading(null);
    }
  };

  const handleMarkProduction = async (modelId: number, version: string, type: string) => {
    setActionLoading(`prod_${modelId}`);
    setError(null);
    setSuccess(null);
    try {
      await markProductionModel(modelId);
      setSuccess(`Model version "${version}" promoted to Production successfully.`);
      await reloadHistory();
    } catch (err: any) {
      setError(err.message || "Failed to promote model.");
    } finally {
      setActionLoading(null);
    }
  };

  const handleDelete = async (modelId: number, version: string) => {
    if (!confirm(`Are you sure you want to delete model version "${version}"? This action cannot be undone.`)) return;
    setActionLoading(`del_${modelId}`);
    setError(null);
    setSuccess(null);
    try {
      await deleteModel(modelId);
      setSuccess(`Model version "${version}" deleted successfully.`);
      await reloadHistory();
    } catch (err: any) {
      setError(err.message || "Failed to delete model registry entry.");
    } finally {
      setActionLoading(null);
    }
  };

  const handleOpenLogs = async (model: MLModelInfo) => {
    setSelectedModelForLogs(model);
    setLogsText("");
    setLogsLoading(true);
    setLogModalOpen(true);
    try {
      const text = await fetchModelLogs(model.id);
      setLogsText(text);
    } catch (err: any) {
      setLogsText(`Failed to load logs: ${err.message}`);
    } finally {
      setLogsLoading(false);
    }
  };

  const handleCompare = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!compareModel1 || !compareModel2) {
      setCompareError("Please select two distinct model versions to compare.");
      return;
    }
    if (compareModel1 === compareModel2) {
      setCompareError("Please select two different model versions.");
      return;
    }
    setCompareLoading(true);
    setCompareError(null);
    setCompareResult(null);
    try {
      const res = await compareModels(compareModel1, compareModel2);
      setCompareResult(res);
    } catch (err: any) {
      setCompareError(err.message || "Failed to compare model versions.");
    } finally {
      setCompareLoading(false);
    }
  };

  // Get active models of each type
  const getActiveModel = (type: string): MLModelInfo | null => {
    // 1. Production model
    const prod = history.find((m) => m.model_type === type && m.is_production && m.status === "Completed");
    if (prod) return prod;
    // 2. Latest completed model
    return history.find((m) => m.model_type === type && m.status === "Completed") || null;
  };

  // Get active training models
  const getTrainingModels = (): MLModelInfo[] => {
    const trainingStatuses = ["Queued", "Preparing Data", "Preprocessing", "Training", "Evaluating", "Saving Model"];
    return history.filter((m) => trainingStatuses.includes(m.status));
  };

  // Available models for comparison dropdown
  const getCompareOptions = (type: string) => {
    return history.filter((m) => m.model_type === type && m.status === "Completed");
  };

  if (!mounted) return null;

  return (
    <div className="space-y-6 flex flex-col min-w-0 pb-12">
      {/* Background ambient lighting glows */}
      <div className="absolute top-[10%] right-[10%] w-[350px] h-[350px] rounded-full bg-indigo-500/5 blur-[90px] pointer-events-none" />
      <div className="absolute bottom-[20%] left-[5%] w-[350px] h-[350px] rounded-full bg-violet-500/5 blur-[90px] pointer-events-none" />

      {/* 1. Page Header */}
      <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-slate-800 pb-5">
        <div className="flex items-center gap-3.5">
          <div className="p-3 bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 rounded-2xl">
            <BrainCircuit className="w-6 h-6" />
          </div>
          <div>
            <div className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest bg-indigo-500/10 border border-indigo-500/20 px-2.5 py-0.5 rounded-full w-fit">
              Model Registry Console
            </div>
            <h1 className="text-2xl font-black text-slate-100 uppercase tracking-tight mt-1.5">
              ML Engine & Retraining Manager
            </h1>
          </div>
        </div>

        {/* Right Info Panel - Dynamic Inputs display */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 bg-slate-900/40 p-2.5 rounded-xl border border-slate-800/40 w-full md:w-auto">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-[10px] text-slate-500 uppercase tracking-widest font-mono flex items-center gap-1">
              <Layers className="w-3 h-3 text-indigo-400" /> Input Data:
            </span>
            {activeDatasets.length > 0 ? (
              activeDatasets.map((ds) => (
                <span key={ds.id} className="text-[10px] font-mono text-indigo-400 bg-indigo-500/10 px-2 py-0.5 border border-indigo-500/20 rounded">
                  ✔ {ds.display_name}
                </span>
              ))
            ) : (
              <span className="text-[10px] font-mono text-red-400 bg-red-500/5 px-2 py-0.5 border border-red-500/10 rounded">
                ✘ No Active Data
              </span>
            )}
          </div>
          <button
            onClick={loadAll}
            className="flex items-center justify-center gap-2 py-1.5 px-3 bg-indigo-600/10 hover:bg-indigo-600/20 border border-indigo-500/30 text-indigo-300 text-xs font-bold rounded-lg transition-all cursor-pointer"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Sync Registry
          </button>
        </div>
      </header>

      {/* Error / Success Notifications */}
      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-2xl flex items-start gap-3 text-xs text-red-400 animate-fade-in">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <div className="space-y-1">
            <p className="font-extrabold uppercase tracking-wide text-red-500">Pipeline Error</p>
            <p className="leading-relaxed text-slate-300">{error}</p>
          </div>
        </div>
      )}

      {success && (
        <div className="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-2xl flex items-start gap-3 text-xs text-emerald-400 animate-fade-in">
          <CheckCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <div className="space-y-1">
            <p className="font-extrabold uppercase tracking-wide text-emerald-500">Task Success</p>
            <p className="leading-relaxed text-slate-300">{success}</p>
          </div>
        </div>
      )}

      {/* ── 2. ACTIVE TRAINING TASKS PROGRESS SECTION ── */}
      {getTrainingModels().length > 0 && (
        <section className="bg-indigo-500/5 border border-indigo-500/20 p-5 rounded-3xl space-y-4 backdrop-blur-md animate-pulse-slow">
          <div className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-indigo-400 animate-spin" />
            <h3 className="text-sm font-black text-slate-200 uppercase tracking-wider">
              Asynchronous Retraining Executing
            </h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {getTrainingModels().map((m) => (
              <div key={m.id} className="bg-slate-950/60 p-4 border border-slate-900 rounded-2xl space-y-3">
                <div className="flex justify-between items-center text-xs">
                  <span className="font-bold text-slate-300">{MODEL_LABELS[m.model_type]}</span>
                  <span className="px-2 py-0.5 bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 rounded-full font-bold font-mono text-[9px] uppercase tracking-wider">
                    {m.status}
                  </span>
                </div>
                <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden">
                  <div
                    className="bg-indigo-500 h-1.5 rounded-full transition-all duration-500"
                    style={{
                      width:
                        m.status === "Queued" ? "10%" :
                        m.status === "Preparing Data" ? "30%" :
                        m.status === "Preprocessing" ? "50%" :
                        m.status === "Training" ? "70%" :
                        m.status === "Evaluating" ? "85%" :
                        m.status === "Saving Model" ? "95%" : "100%"
                    }}
                  />
                </div>
                <div className="flex justify-between items-center text-[10px] text-slate-500">
                  <span className="font-mono">{m.version}</span>
                  <button
                    onClick={() => handleOpenLogs(m)}
                    className="text-indigo-400 hover:text-indigo-300 underline font-bold transition-all cursor-pointer"
                  >
                    View Real-Time Logs
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* ── 3. PRODUCTION MODELS STATUS CARDS GRID ── */}
      <section className="space-y-3">
        <h2 className="text-sm font-black text-slate-400 uppercase tracking-widest flex items-center gap-1.5">
          <Zap className="w-4 h-4 text-amber-500" /> Active Engines Models
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 w-full">
          {Object.keys(MODEL_LABELS).map((type) => {
            const active = getActiveModel(type);
            const isTrainLoading = actionLoading === `train_${type}`;
            return (
              <div key={type} className="glass-card p-5 rounded-3xl border border-slate-800/80 bg-slate-900/30 flex flex-col justify-between h-[230px] relative overflow-hidden group">
                <div className="space-y-3">
                  <div className="flex justify-between items-start">
                    <span className="text-[10px] font-extrabold text-indigo-400 uppercase tracking-wider bg-indigo-500/5 border border-indigo-500/10 px-2 py-0.5 rounded">
                      {type === "crime_risk" ? "Regressor" : "Classifier"}
                    </span>
                    {active?.is_production && (
                      <span className="text-[9px] font-black uppercase text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded-full flex items-center gap-1">
                        <ShieldCheck className="w-3 h-3" /> Prod Active
                      </span>
                    )}
                  </div>
                  <div>
                    <h3 className="font-extrabold text-sm text-slate-100 group-hover:text-indigo-400 transition-colors">
                      {MODEL_LABELS[type]}
                    </h3>
                    <p className="text-[10px] text-slate-500 font-mono tracking-wide mt-1">
                      {active ? active.version : "No version trained"}
                    </p>
                  </div>
                </div>

                {active ? (
                  <div className="grid grid-cols-3 gap-2 bg-slate-950/40 p-2 rounded-xl border border-slate-900/40 text-center text-[10px]">
                    <div>
                      <span className="text-slate-500 block text-[9px] uppercase font-bold tracking-wider">Accuracy</span>
                      <span className="font-bold text-slate-300 font-mono">
                        {active.accuracy !== null ? `${(active.accuracy * 100).toFixed(1)}%` : "N/A"}
                      </span>
                    </div>
                    <div>
                      <span className="text-slate-500 block text-[9px] uppercase font-bold tracking-wider">F1 Score</span>
                      <span className="font-bold text-slate-300 font-mono">
                        {active.f1_score !== null ? active.f1_score.toFixed(2) : "N/A"}
                      </span>
                    </div>
                    <div>
                      <span className="text-slate-500 block text-[9px] uppercase font-bold tracking-wider">ROC AUC</span>
                      <span className="font-bold text-slate-300 font-mono">
                        {active.roc_auc !== null ? active.roc_auc.toFixed(2) : "N/A"}
                      </span>
                    </div>
                  </div>
                ) : (
                  <div className="py-2.5 px-4 bg-rose-500/5 border border-rose-500/10 text-rose-400 rounded-xl text-center text-[10px]">
                    ⚠ Model not trained. Predictions using standard static seeds.
                  </div>
                )}

                <button
                  onClick={() => handleTrain(type)}
                  disabled={isTrainLoading || getTrainingModels().some((m) => m.model_type === type)}
                  className="w-full flex items-center justify-center gap-2 py-2.5 px-3 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 disabled:text-slate-600 text-white font-bold text-[10px] uppercase tracking-wider rounded-xl transition-all cursor-pointer"
                >
                  {isTrainLoading ? (
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  ) : (
                    <Play className="w-3 h-3 fill-current" />
                  )}
                  {active ? "Retrain Engine" : "Initiate Training"}
                </button>
              </div>
            );
          })}
        </div>
      </section>

      {/* ── 4. COMPARISON AND HISTORICAL REGISTRY (2-Column Layout) ── */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Registry Table */}
        <section className="lg:col-span-8 space-y-3">
          <h2 className="text-sm font-black text-slate-400 uppercase tracking-widest flex items-center gap-1.5">
            <History className="w-4 h-4 text-indigo-400" /> Registry Version History
          </h2>
          <div className="bg-slate-900/30 border border-slate-800/80 rounded-3xl overflow-hidden backdrop-blur-md min-w-0">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-slate-950/60 border-b border-slate-800 text-[10px] uppercase font-bold text-slate-400 tracking-wider">
                    <th className="p-4">Model Engine / Version</th>
                    <th className="p-4 text-center">Dataset IDs</th>
                    <th className="p-4 text-center">Metrics (Acc/F1)</th>
                    <th className="p-4 text-center">Status</th>
                    <th className="p-4 text-center">Production</th>
                    <th className="p-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/40 text-slate-300">
                  {loading ? (
                    <tr>
                      <td colSpan={6} className="p-8 text-center text-slate-500">
                        <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-indigo-400" />
                        Querying model registry...
                      </td>
                    </tr>
                  ) : history.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="p-8 text-center text-slate-500">
                        No model version history recorded in registry. Trigger retraining above to seed models.
                      </td>
                    </tr>
                  ) : (
                    history.map((model) => {
                      const isAction = actionLoading === `prod_${model.id}` || actionLoading === `del_${model.id}`;
                      return (
                        <tr key={model.id} className="hover:bg-slate-900/10 transition-colors">
                          <td className="p-4">
                            <div className="font-extrabold text-slate-200">{MODEL_LABELS[model.model_type]}</div>
                            <div className="text-[10px] font-mono text-slate-500 mt-0.5">{model.version}</div>
                            <div className="text-[9px] text-slate-500 mt-1">
                              {new Date(model.created_at).toLocaleString()} | {model.training_duration !== null ? `${model.training_duration.toFixed(1)}s` : ""}
                            </div>
                          </td>
                          <td className="p-4 text-center font-mono text-[10px] text-indigo-300">
                            {model.training_dataset_ids}
                          </td>
                          <td className="p-4 text-center font-mono">
                            {model.status === "Completed" ? (
                              <div className="space-y-0.5">
                                <div>Acc: {model.accuracy !== null ? `${(model.accuracy * 100).toFixed(1)}%` : "N/A"}</div>
                                {model.f1_score !== null && <div className="text-[10px] text-slate-500">F1: {model.f1_score.toFixed(2)}</div>}
                              </div>
                            ) : (
                              <span className="text-slate-600">—</span>
                            )}
                          </td>
                          <td className="p-4 text-center">
                            <span
                              className={`px-2 py-0.5 rounded-full text-[9px] font-black uppercase tracking-wider border ${
                                model.status === "Completed"
                                  ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-400"
                                  : model.status === "Failed"
                                  ? "bg-rose-500/10 border-rose-500/20 text-rose-400"
                                  : "bg-amber-500/10 border-amber-500/20 text-amber-400 animate-pulse"
                              }`}
                            >
                              {model.status}
                            </span>
                          </td>
                          <td className="p-4 text-center">
                            {model.is_production ? (
                              <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 font-extrabold text-[9px] uppercase tracking-wider inline-flex items-center gap-1 shadow-sm shadow-emerald-500/5">
                                <ShieldCheck className="w-3 h-3" /> Production
                              </span>
                            ) : (
                              <span className="text-slate-600 font-mono text-[10px]">Inactive</span>
                            )}
                          </td>
                          <td className="p-4 text-right">
                            <div className="flex items-center justify-end gap-2">
                              <button
                                onClick={() => handleOpenLogs(model)}
                                className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition-all cursor-pointer"
                                title="View training logs"
                              >
                                <FileText className="w-4 h-4" />
                              </button>
                              
                              {model.status === "Completed" && !model.is_production && (
                                <button
                                  onClick={() => handleMarkProduction(model.id, model.version, model.model_type)}
                                  disabled={isAction}
                                  className="py-1 px-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-extrabold text-[9px] uppercase tracking-wider rounded-lg transition-all cursor-pointer disabled:opacity-50"
                                  title="Mark as active production model"
                                >
                                  Activate
                                </button>
                              )}

                              {!model.is_production && (
                                <button
                                  onClick={() => handleDelete(model.id, model.version)}
                                  disabled={isAction}
                                  className="p-1.5 bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/20 hover:border-rose-500/40 rounded-lg transition-all cursor-pointer disabled:opacity-50"
                                  title="Delete model version"
                                >
                                  <Trash2 className="w-4 h-4" />
                                </button>
                              )}
                            </div>
                          </td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </section>

        {/* Right Column: Comparative Dashboard */}
        <section className="lg:col-span-4 space-y-3">
          <h2 className="text-sm font-black text-slate-400 uppercase tracking-widest flex items-center gap-1.5">
            <GitCompare className="w-4 h-4 text-indigo-400" /> Compare Model Versions
          </h2>
          <div className="bg-slate-900/30 border border-slate-800/80 p-5 rounded-3xl backdrop-blur-md space-y-4">
            <form onSubmit={handleCompare} className="space-y-4">
              <div className="space-y-1">
                <label className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">Model Classifier Engine</label>
                <select
                  value={compareType}
                  onChange={(e) => {
                    setCompareType(e.target.value);
                    setCompareModel1(null);
                    setCompareModel2(null);
                    setCompareResult(null);
                  }}
                  className="w-full p-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs font-semibold text-slate-300 focus:outline-none focus:border-indigo-500 transition-all cursor-pointer"
                >
                  {Object.entries(MODEL_LABELS).map(([k, v]) => (
                    <option key={k} value={k}>{v}</option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">Model 1 (Baseline)</label>
                  <select
                    value={compareModel1 || ""}
                    onChange={(e) => setCompareModel1(e.target.value ? Number(e.target.value) : null)}
                    className="w-full p-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs font-mono text-slate-300 focus:outline-none focus:border-indigo-500 transition-all cursor-pointer"
                  >
                    <option value="">Select version</option>
                    {getCompareOptions(compareType).map((m) => (
                      <option key={m.id} value={m.id}>
                        {m.version.substring(0, 15)}... {m.is_production ? "(Prod)" : ""}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="space-y-1">
                  <label className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">Model 2 (Target)</label>
                  <select
                    value={compareModel2 || ""}
                    onChange={(e) => setCompareModel2(e.target.value ? Number(e.target.value) : null)}
                    className="w-full p-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs font-mono text-slate-300 focus:outline-none focus:border-indigo-500 transition-all cursor-pointer"
                  >
                    <option value="">Select version</option>
                    {getCompareOptions(compareType).map((m) => (
                      <option key={m.id} value={m.id}>
                        {m.version.substring(0, 15)}... {m.is_production ? "(Prod)" : ""}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <button
                type="submit"
                disabled={compareLoading || !compareModel1 || !compareModel2}
                className="w-full py-2.5 px-3 bg-indigo-600 hover:bg-indigo-550 text-white font-bold text-xs uppercase tracking-wider rounded-xl transition-all cursor-pointer disabled:bg-slate-800 disabled:text-slate-600 shadow-lg shadow-indigo-600/10"
              >
                {compareLoading ? "Computing Differentials..." : "Compare Versions"}
              </button>
            </form>

            {compareError && (
              <div className="p-3 bg-red-500/5 border border-red-500/10 text-red-400 text-[11px] rounded-xl">
                {compareError}
              </div>
            )}

            {compareResult && (
              <div className="bg-slate-950/60 p-4 border border-slate-900 rounded-2xl space-y-3.5 animate-fade-in text-xs">
                <div className="flex justify-between items-center border-b border-slate-900 pb-2 text-[10px] font-mono text-slate-500">
                  <span>BASELINE ({compareResult.model_1.version.substring(0, 8)})</span>
                  <ArrowRight className="w-3.5 h-3.5 text-slate-600" />
                  <span>TARGET ({compareResult.model_2.version.substring(0, 8)})</span>
                </div>
                
                <div className="space-y-2.5 font-mono">
                  {Object.entries(compareResult.metrics_difference).map(([metric, val]) => {
                    const baseline = (compareResult.model_1 as any)[metric];
                    const target = (compareResult.model_2 as any)[metric];
                    if (baseline === null || target === null) return null;

                    const percentDiff = val !== null ? val * 100 : 0;
                    return (
                      <div key={metric} className="flex justify-between items-center text-[11px]">
                        <span className="text-slate-500 uppercase text-[9px] font-bold tracking-wider">{metric.replace("_", " ")}</span>
                        <div className="flex items-center gap-2">
                          <span className="text-slate-400">{baseline.toFixed(3)}</span>
                          <ArrowRight className="w-3 h-3 text-slate-600" />
                          <span className="text-slate-200 font-bold">{target.toFixed(3)}</span>
                          <span
                            className={`text-[9px] font-extrabold px-1.5 py-0.2 rounded font-sans ${
                              val === null
                                ? "text-slate-500 bg-slate-900"
                                : val >= 0
                                ? "text-emerald-400 bg-emerald-500/10"
                                : "text-rose-400 bg-rose-500/10"
                            }`}
                          >
                            {val === null ? "—" : `${val >= 0 ? "+" : ""}${percentDiff.toFixed(1)}%`}
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        </section>
      </div>

      {/* ── 5. RUNNING LOGS MODAL ── */}
      {logModalOpen && selectedModelForLogs && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fade-in">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-2xl w-full flex flex-col h-[550px] shadow-2xl relative">
            <header className="p-5 border-b border-slate-850 flex justify-between items-start">
              <div>
                <h3 className="text-sm font-black text-slate-100 uppercase tracking-wider flex items-center gap-2">
                  <FileText className="w-4 h-4 text-indigo-400" /> Model Pipeline Log Viewer
                </h3>
                <p className="text-[10px] font-mono text-slate-500 tracking-wide mt-1">
                  {selectedModelForLogs.version} | Type: {selectedModelForLogs.model_type}
                </p>
              </div>
              <button
                onClick={() => setLogModalOpen(false)}
                className="text-slate-500 hover:text-slate-300 text-sm font-bold bg-slate-950 px-2.5 py-1 rounded-lg border border-slate-800 transition-all cursor-pointer"
              >
                ✕ Close
              </button>
            </header>

            <div className="flex-1 p-5 overflow-y-auto font-mono text-[10px] leading-relaxed bg-slate-950 text-indigo-300 p-4 rounded-b-2xl select-text select-all whitespace-pre">
              {logsLoading ? (
                <div className="flex items-center justify-center h-full gap-2 text-slate-500">
                  <RefreshCw className="w-4 h-4 animate-spin text-indigo-500" />
                  Loading execution trace logs...
                </div>
              ) : (
                logsText || "No logs available for this model version task run."
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
