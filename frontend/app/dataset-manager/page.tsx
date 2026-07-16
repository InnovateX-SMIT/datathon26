"use client";

import React, { useState, useEffect, useRef } from "react";
import { createPortal } from "react-dom";
import {
  FileSpreadsheet,
  Upload,
  Trash2,
  Eye,
  RefreshCw,
  Search,
  X,
  AlertCircle,
  CheckCircle2,
  HardDrive,
  Info,
  Layers,
  Database,
  Calendar,
  Sparkles,
  BarChart,
  FileCode,
  Settings,
  ToggleLeft,
  ToggleRight,
  Play,
  Pause
} from "lucide-react";
import {
  fetchDatasets,
  uploadDatasets,
  deleteDataset,
  deleteDatasetPermanent,
  fetchDatasetPreview,
  fetchDatasetStatistics,
  activateDataset,
  deactivateDataset,
  fetchDatasetConfig,
  updateDatasetConfig,
  detectSchemaType,
  importFIRDataset,
  DatasetInfo,
  DatasetPreview,
  DatasetStatistics,
  DatasetConfig
} from "@/services/dataset.service";

type PreviewTabId = "data" | "schema" | "statistics";

const unwrapResponseData = <T,>(res: any): T => {
  if (res && typeof res === "object" && res.success === true && "data" in res) {
    return res.data;
  }
  return res;
};

export default function DatasetManagerPage() {
  const [datasets, setDatasets] = useState<DatasetInfo[]>([]);
  const [config, setConfig] = useState<DatasetConfig | null>(null);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);



  const handlePermanentDelete = async (ds: DatasetInfo) => {
    const confirmMsg = `Are you sure you want to PERMANENTLY delete "${ds.display_name}"? \nThis action is irreversible and will delete the file from disk along with all of its associated case, complainant, victim, accused, and event records.`;
    if (!confirm(confirmMsg)) return;

    setActionLoading(true);
    setError(null);
    setSuccess(null);
    try {
      await deleteDatasetPermanent(ds.id);
      setSuccess("Dataset permanently deleted.");
      await loadDatasets();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to permanently delete dataset.");
    } finally {
      setActionLoading(false);
    }
  };

  // Drag and drop state
  const [dragActive, setDragActive] = useState(false);
  const [uploadFiles, setUploadFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [displayNameInput, setDisplayNameInput] = useState("");
  const [descriptionInput, setDescriptionInput] = useState("");
  const [previewSummary, setPreviewSummary] = useState<any>(null);
  const [previewSchemaType, setPreviewSchemaType] = useState<string | null>(null);
  const [hasValidated, setHasValidated] = useState(false);

  // Preview Modal state
  const [previewDataset, setPreviewDataset] = useState<DatasetInfo | null>(null);
  const [previewData, setPreviewData] = useState<DatasetPreview | null>(null);
  const [previewStats, setPreviewStats] = useState<DatasetStatistics | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [previewTab, setPreviewTab] = useState<PreviewTabId>("data");

  // Settings Panel state
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [maxActiveInput, setMaxActiveInput] = useState("1");

  // Delete Confirm Modal state
  const [deleteConfirmDataset, setDeleteConfirmDataset] = useState<DatasetInfo | null>(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [mounted, setMounted] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setMounted(true);
    loadDatasets();
    loadConfig();
  }, []);

  useEffect(() => {
    const hasActiveJob = datasets.some(
      (ds) => ds.status === "Uploading" || ds.status === "Validating" || ds.status === "Importing"
    );

    if (hasActiveJob) {
      const interval = setInterval(() => {
        loadDatasets(true);
      }, 2000);
      return () => clearInterval(interval);
    }
  }, [datasets]);

  const loadDatasets = async (silent = false) => {
    if (!silent) setLoading(true);
    if (!silent) setError(null);
    try {
      const data = await fetchDatasets();
      setDatasets(unwrapResponseData<DatasetInfo[]>(data) || []);
      const list = Array.isArray(data) ? data : (data && typeof data === "object" && "data" in data && Array.isArray((data as any).data) ? (data as any).data : []);
      setDatasets(list);
    } catch (err: any) {
      if (!silent) setError(err.response?.data?.detail || "Failed to fetch dataset registry.");
    } finally {
      if (!silent) setLoading(false);
    }
  };

  const loadConfig = async () => {
    try {
      const cfg = await fetchDatasetConfig();
      const unwrapped = unwrapResponseData<DatasetConfig>(cfg);
      setConfig(unwrapped);
      if (unwrapped) {
        setMaxActiveInput(unwrapped.max_active_datasets);
      }
    } catch (err: any) {
      console.error("Failed to load settings configuration", err);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const files: File[] = [];
      for (let i = 0; i < e.dataTransfer.files.length; i++) {
        const file = e.dataTransfer.files[i];
        const ext = file.name.split(".").pop()?.toLowerCase();
        if (ext === "csv" || ext === "xlsx" || ext === "xls") {
          files.push(file);
        }
      }
      if (files.length > 0) {
        setUploadFiles(prev => [...prev, ...files]);
        setHasValidated(false);
        setPreviewSummary(null);
        setPreviewSchemaType(null);
        setError(null);
      } else {
        setError("Invalid file format. Only CSV and Excel (.xlsx, .xls) files are supported.");
      }
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const files: File[] = [];
      for (let i = 0; i < e.target.files.length; i++) {
        files.push(e.target.files[i]);
      }
      setUploadFiles(prev => [...prev, ...files]);
      setHasValidated(false);
      setPreviewSummary(null);
      setPreviewSchemaType(null);
      setError(null);
    }
  };

  const removeUploadFile = (index: number) => {
    setUploadFiles(prev => prev.filter((_, i) => i !== index));
    setHasValidated(false);
    setPreviewSummary(null);
    setPreviewSchemaType(null);
  };

  const handleValidatePreview = async () => {
    if (uploadFiles.length === 0) {
      setError("Please select or drop at least one file.");
      return;
    }

    setUploading(true);
    setUploadProgress(20);
    setError(null);
    setSuccess(null);

    try {
      const { schema_type } = await detectSchemaType(uploadFiles[0]);
      setPreviewSchemaType(schema_type);
      setUploadProgress(50);

      let summary;
      if (schema_type === "fir_normalized") {
        summary = await importFIRDataset(
          displayNameInput.trim() !== "" ? displayNameInput : null,
          descriptionInput.trim() !== "" ? descriptionInput : null,
          uploadFiles[0],
          true
        );
      } else {
        summary = await uploadDatasets(
          displayNameInput.trim() !== "" ? displayNameInput : null,
          descriptionInput.trim() !== "" ? descriptionInput : null,
          uploadFiles,
          true
        );
      }

      setUploadProgress(100);
      setPreviewSummary(summary);
      setHasValidated(true);
      setSuccess(`File validated: ${summary.valid_count} valid rows, ${summary.invalid_count} row errors found.`);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Validation or detection failed.");
    } finally {
      setUploading(false);
    }
  };

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!hasValidated) {
      await handleValidatePreview();
      return;
    }

    if (uploadFiles.length === 0) {
      setError("Please select or drop at least one file.");
      return;
    }

    setUploading(true);
    setUploadProgress(10);
    setError(null);
    setSuccess(null);

    // Simulate progress increments
    const progressInterval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 90) {
          clearInterval(progressInterval);
          return 90;
        }
        return prev + 10;
      });
    }, 400);

    try {
      if (previewSchemaType === "fir_normalized") {
        await importFIRDataset(
          displayNameInput.trim() !== "" ? displayNameInput : null,
          descriptionInput.trim() !== "" ? descriptionInput : null,
          uploadFiles[0],
          false
        );
      } else {
        await uploadDatasets(
          displayNameInput.trim() !== "" ? displayNameInput : null,
          descriptionInput.trim() !== "" ? descriptionInput : null,
          uploadFiles,
          false
        );
      }

      setUploadProgress(100);
      setTimeout(() => {
        setSuccess(`Successfully uploaded and validated ${uploadFiles.length} dataset(s).`);
        setUploadFiles([]);
        setDisplayNameInput("");
        setDescriptionInput("");
        setPreviewSummary(null);
        setPreviewSchemaType(null);
        setHasValidated(false);
        setUploading(false);
        loadDatasets();
        if (typeof window !== "undefined") {
          window.dispatchEvent(new Event("activeDatasetChanged"));
        }
      }, 400);
    } catch (err: any) {
      clearInterval(progressInterval);
      setError(err.response?.data?.detail || "Dataset validation or upload failed.");
      setUploading(false);
    }
  };

  const handleToggleActive = async (ds: DatasetInfo) => {
    setActionLoading(true);
    setError(null);
    setSuccess(null);
    try {
      if (ds.is_active) {
        await deactivateDataset(ds.id);
        setSuccess(`Dataset "${ds.display_name}" deactivated successfully.`);
      } else {
        await activateDataset(ds.id);
        setSuccess(`Dataset "${ds.display_name}" activated successfully.`);
      }
      await loadDatasets();
      if (typeof window !== "undefined") {
        window.dispatchEvent(new Event("activeDatasetChanged"));
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to switch active status.");
    } finally {
      setActionLoading(false);
    }
  };

  const handleSettingsSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setActionLoading(true);
    setError(null);
    setSuccess(null);
    try {
      await updateDatasetConfig(maxActiveInput);
      setSuccess(`Maximum active dataset limit set to "${maxActiveInput}".`);
      setSettingsOpen(false);
      await loadDatasets();
      await loadConfig();
      if (typeof window !== "undefined") {
        window.dispatchEvent(new Event("activeDatasetChanged"));
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to update settings configuration.");
    } finally {
      setActionLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteConfirmDataset) return;
    setActionLoading(true);
    setError(null);
    setSuccess(null);
    try {
      await deleteDataset(deleteConfirmDataset.id);
      setSuccess(`Dataset "${deleteConfirmDataset.display_name}" archived successfully.`);
      setDeleteConfirmDataset(null);
      await loadDatasets();
      if (typeof window !== "undefined") {
        window.dispatchEvent(new Event("activeDatasetChanged"));
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to delete dataset.");
    } finally {
      setActionLoading(false);
    }
  };

  const handleOpenPreview = async (ds: DatasetInfo) => {
    setPreviewDataset(ds);
    setPreviewData(null);
    setPreviewStats(null);
    setPreviewLoading(true);
    setPreviewTab("data");
    try {
      const data = await fetchDatasetPreview(ds.id);
      setPreviewData(data);

      const stats = await fetchDatasetStatistics(ds.id);
      setPreviewStats(stats);
    } catch (err: any) {
      setError(err.response?.data?.detail || `Failed to fetch preview for dataset "${ds.display_name}".`);
      setPreviewDataset(null);
    } finally {
      setPreviewLoading(false);
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  const getStatusBadge = (ds: DatasetInfo) => {
    if (ds.is_active) {
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          Active
        </span>
      );
    }

    switch (ds.status) {
      case "Ready":
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-slate-800 border border-slate-700 text-slate-400">
            <span className="w-1.5 h-1.5 rounded-full bg-slate-500" />
            Inactive
          </span>
        );
      case "Failed":
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-red-500/10 border border-red-500/20 text-red-400">
            <span className="w-1.5 h-1.5 rounded-full bg-red-400" />
            Failed
          </span>
        );
      case "Archived":
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-slate-900 border border-slate-850 text-slate-500">
            <span className="w-1.5 h-1.5 rounded-full bg-slate-650" />
            Archived
          </span>
        );
      case "Uploading":
      case "Validating":
      case "Importing":
        let progress = 0;
        let progressText: string = ds.status;
        if (ds.import_summary) {
          try {
            const summary = JSON.parse(ds.import_summary);
            if (typeof summary.progress === "number") {
              progress = summary.progress;
              progressText = `${ds.status} (${progress}%)`;
            }
          } catch (e) { }
        }
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-amber-500/10 border border-amber-500/20 text-amber-400 animate-pulse">
            <RefreshCw className="w-3 h-3 animate-spin text-amber-400 shrink-0" />
            {progressText}
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-slate-500/10 border border-slate-500/20 text-slate-400">
            {ds.status}
          </span>
        );
    }
  };

  const activeDatasetsList = (Array.isArray(datasets) ? datasets : []).filter(d => d.is_active);
  const activeCount = activeDatasetsList.length;
  const maxActiveStr = config?.max_active_datasets || "1";

  // Filters search results
  const filteredDatasets = (Array.isArray(datasets) ? datasets : []).filter(
    (ds) =>
      ds.display_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      ds.original_filename.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen py-8 px-4 sm:px-6 lg:px-8 space-y-8 animate-fade-in relative text-slate-200">
      {/* Background ambient glows */}
      <div className="absolute top-[10%] right-[5%] w-[500px] h-[500px] rounded-full bg-violet-500/5 blur-[130px] pointer-events-none" />
      <div className="absolute bottom-[10%] left-[8%] w-[400px] h-[400px] rounded-full bg-indigo-500/5 blur-[110px] pointer-events-none" />

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-900/80 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-violet-500/10 border border-violet-500/20 rounded-2xl">
              <HardDrive className="w-6 h-6 text-violet-400" />
            </div>
            <div>
              <h1 className="text-3xl font-black text-slate-100 uppercase tracking-tight">
                Dataset Manager
              </h1>
            </div>
          </div>
        </div>

        {/* Global Active indicator */}
        <div className="flex items-center gap-2.5 px-4 py-2.5 bg-violet-500/10 border border-violet-500/20 rounded-2xl self-start">
          <span className="w-2 h-2 rounded-full bg-violet-400 animate-pulse" />
          <span className="text-violet-400 text-xs font-black uppercase tracking-wider font-mono">
            Active: {activeCount} / {maxActiveStr}
          </span>
        </div>
      </div>



          {/* Alerts */}
          {error && (
            <div className="p-4 bg-red-500/10 border border-red-500/20 text-red-400 text-xs rounded-2xl flex items-center gap-3 max-w-5xl">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <div className="flex-1">{error}</div>
              <button onClick={() => setError(null)} className="text-red-400 hover:text-red-300">
                <X className="w-4 h-4" />
              </button>
            </div>
          )}

          {success && (
            <div className="p-4 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs rounded-2xl flex items-center gap-3 max-w-5xl">
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <div className="flex-1">{success}</div>
              <button onClick={() => setSuccess(null)} className="text-emerald-400 hover:text-emerald-300">
                <X className="w-4 h-4" />
              </button>
            </div>
          )}

          {/* Upload and controls section */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Upload card (2 cols on large screens) */}
            <div className="lg:col-span-2 bg-gradient-to-br from-slate-900/60 to-slate-950/60 p-6 border border-slate-800/80 rounded-3xl backdrop-blur-md flex flex-col gap-5">
              <div>
                <h3 className="text-sm font-black text-slate-200 uppercase tracking-wider flex items-center gap-2">
                  <Upload className="w-4 h-4 text-violet-400" />
                  <span>Multi-File Upload Portal</span>
                </h3>
              </div>

              <form onSubmit={handleUploadSubmit} className="space-y-4 flex-1 flex flex-col justify-between">
                <div className="space-y-4">
                  {/* Grid Inputs */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="flex flex-col gap-1.5">
                      <label className="text-[9px] font-bold text-slate-550 uppercase tracking-widest">
                        Dataset Name Prefix (Optional)
                      </label>
                      <input
                        type="text"
                        value={displayNameInput}
                        onChange={(e) => setDisplayNameInput(e.target.value)}
                        placeholder="e.g. Crime Dataset"
                        className="bg-slate-950/80 border border-slate-800 text-slate-200 text-xs rounded-xl px-4 py-2.5 outline-none focus:border-violet-500 transition-all font-mono"
                      />
                    </div>

                    <div className="flex flex-col gap-1.5">
                      <label className="text-[9px] font-bold text-slate-550 uppercase tracking-widest">
                        Description / Purpose (Optional)
                      </label>
                      <input
                        type="text"
                        value={descriptionInput}
                        onChange={(e) => setDescriptionInput(e.target.value)}
                        placeholder="e.g. Bangalore incidents analysis Q2"
                        className="bg-slate-950/80 border border-slate-800 text-slate-200 text-xs rounded-xl px-4 py-2.5 outline-none focus:border-violet-500 transition-all font-mono"
                      />
                    </div>
                  </div>

                  {/* Drag Area */}
                  <div
                    onDragEnter={handleDrag}
                    onDragOver={handleDrag}
                    onDragLeave={handleDrag}
                    onDrop={handleDrop}
                    onClick={() => fileInputRef.current?.click()}
                    className={`border-2 border-dashed rounded-2xl p-6 text-center cursor-pointer transition-all bg-slate-950/20 relative group min-h-[140px] flex flex-col justify-center items-center ${dragActive ? "border-violet-500 bg-violet-500/[0.02]" : "border-slate-800 hover:border-violet-500/40"
                      }`}
                  >
                    <input
                      type="file"
                      ref={fileInputRef}
                      multiple
                      accept=".csv,.xlsx,.xls"
                      onChange={handleFileSelect}
                      className="hidden"
                    />
                    <FileSpreadsheet className="w-10 h-10 text-slate-650 group-hover:text-violet-400 mx-auto transition-all" />
                    <div className="mt-2.5">
                      <p className="text-xs text-slate-350">
                        Click to browse or drag & drop files here
                      </p>
                      <p className="text-[10px] text-slate-555 mt-1 uppercase font-mono tracking-widest">
                        Accepts CSV, XLSX or XLS formats
                      </p>
                    </div>
                  </div>

                  {/* Selected Files list */}
                  {uploadFiles.length > 0 && (
                    <div className="space-y-1.5 max-h-[160px] overflow-y-auto pr-1">
                      <p className="text-[9px] font-bold text-slate-500 uppercase tracking-widest">
                        Selected Files ({uploadFiles.length})
                      </p>
                      {uploadFiles.map((file, idx) => (
                        <div
                          key={idx}
                          className="flex items-center justify-between p-2 bg-slate-950/50 border border-slate-900 rounded-xl text-xs font-mono"
                        >
                          <div className="flex items-center gap-2 truncate">
                            <FileCode className="w-3.5 h-3.5 text-violet-400 shrink-0" />
                            <span className="text-slate-300 truncate" title={file.name}>
                              {file.name}
                            </span>
                            <span className="text-[10px] text-slate-600">({formatBytes(file.size)})</span>
                          </div>
                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation();
                              removeUploadFile(idx);
                            }}
                            className="text-slate-505 hover:text-red-400 transition-colors p-1"
                          >
                            <X className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
                {hasValidated && previewSummary && (
                  <div className="space-y-4 bg-slate-950/40 p-4 rounded-2xl border border-slate-800">
                    <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest border-b border-slate-850 pb-1.5">
                      Validation Results ({previewSchemaType === "fir_normalized" ? "FIR Schema" : "Legacy Schema"})
                    </h4>
                    <div className="grid grid-cols-3 gap-2 text-center text-xs">
                      <div className="bg-slate-900/60 p-2 border border-slate-850 rounded-xl font-mono">
                        <p className="text-[8px] font-bold text-slate-500 uppercase tracking-wider">Total Rows</p>
                        <p className="font-bold text-slate-200 mt-0.5">{previewSummary.total_rows}</p>
                      </div>
                      <div className="bg-slate-900/60 p-2 border border-slate-850 rounded-xl font-mono">
                        <p className="text-[8px] font-bold text-slate-500 uppercase tracking-wider">Valid</p>
                        <p className="font-bold text-emerald-400 mt-0.5">{previewSummary.valid_count}</p>
                      </div>
                      <div className="bg-slate-900/60 p-2 border border-slate-850 rounded-xl font-mono">
                        <p className="text-[8px] font-bold text-slate-500 uppercase tracking-wider">Errors</p>
                        <p className="font-bold text-red-400 mt-0.5">{previewSummary.invalid_count}</p>
                      </div>
                    </div>
                    {previewSummary.invalid_count > 0 && (
                      <div className="space-y-1">
                        <p className="text-[9px] font-bold text-red-450 uppercase tracking-wider font-sans">Errors (First 5)</p>
                        <div className="bg-slate-900/40 rounded-xl p-2.5 max-h-28 overflow-y-auto border border-slate-950 font-mono text-[10px] text-slate-400 divide-y divide-slate-850">
                          {previewSummary.errors.slice(0, 5).map((err: any, idx: number) => (
                            <div key={idx} className="py-1">
                              <span className="text-red-450 font-bold">Row {err.row}</span>:{" "}
                              {Object.entries(err.errors).map(([k, v]) => `${k}: ${v}`).join(", ")}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Form actions / progress */}
                <div className="pt-4 border-t border-slate-850 flex flex-col gap-3">
                  {uploading && (
                    <div className="space-y-1.5 w-full">
                      <div className="flex justify-between items-center text-[10px] font-mono text-slate-450 uppercase">
                        <span>Validating & Importing...</span>
                        <span>{uploadProgress}%</span>
                      </div>
                      <div className="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden border border-slate-900">
                        <div
                          className="bg-gradient-to-r from-violet-500 to-indigo-500 h-full rounded-full transition-all duration-300"
                          style={{ width: `${uploadProgress}%` }}
                        />
                      </div>
                    </div>
                  )}

                  <div className="flex justify-end gap-3 self-end">
                    {uploadFiles.length > 0 && (
                      <button
                        type="button"
                        onClick={() => {
                          setUploadFiles([]);
                          setHasValidated(false);
                          setPreviewSummary(null);
                          setPreviewSchemaType(null);
                        }}
                        disabled={uploading}
                        className="px-4 py-2 bg-slate-955 hover:bg-slate-850 border border-slate-850 text-slate-400 hover:text-slate-202 rounded-xl text-xs font-bold transition-all disabled:opacity-50 cursor-pointer"
                      >
                        Clear All
                      </button>
                    )}
                    <button
                      type="submit"
                      disabled={uploading || uploadFiles.length === 0 || (hasValidated && previewSummary?.valid_count === 0)}
                      className="px-6 py-2.5 bg-violet-600 hover:bg-violet-750 text-white rounded-xl text-xs font-bold transition-all disabled:opacity-40 cursor-pointer shadow-md shadow-violet-600/10 flex items-center gap-1.5 uppercase tracking-wider"
                    >
                      {uploading ? (
                        <>
                          <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                          <span>Processing...</span>
                        </>
                      ) : (
                        <>
                          <Upload className="w-3.5 h-3.5" />
                          <span>{hasValidated ? "Commit Ingestion" : "Validate & Preview"}</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </form>
            </div>

            {/* Overview Stats box */}
            <div className="bg-slate-900/60 p-6 border border-slate-800/80 rounded-3xl backdrop-blur-md flex flex-col justify-between gap-5 relative overflow-hidden">
              <div className="absolute top-0 right-0 p-8 opacity-[0.02] pointer-events-none">
                <Database className="w-48 h-48 text-violet-400" />
              </div>
              <div>
                <h3 className="text-sm font-black text-slate-300 uppercase tracking-wider">
                  Registry Summary
                </h3>
                <p className="text-[11px] text-slate-555 mt-1">
                  Active configuration controls for data switching.
                </p>
              </div>

              <div className="space-y-4">
                <div className="bg-slate-950/40 p-4 border border-slate-900 rounded-2xl flex justify-between items-center">
                  <div>
                    <span className="text-[9px] font-bold text-slate-550 uppercase tracking-widest block font-mono">
                      Active Limit config
                    </span>
                    <p className="text-xl font-black text-slate-200 font-mono mt-0.5">
                      Max: {maxActiveStr} Active
                    </p>
                  </div>
                  <button
                    onClick={() => setSettingsOpen(true)}
                    className="p-2 bg-slate-900 hover:bg-slate-850 border border-slate-800 text-slate-400 hover:text-slate-200 rounded-xl cursor-pointer transition-all"
                    title="Open settings panel"
                  >
                    <Settings className="w-4 h-4" />
                  </button>
                </div>

                <div className="bg-slate-950/40 p-4 border border-slate-900 rounded-2xl">
                  <span className="text-[9px] font-bold text-slate-555 uppercase tracking-widest block font-mono">
                    Active Dataset Context ({activeCount} / {maxActiveStr})
                  </span>
                  <div className="mt-1.5 space-y-1 max-h-[80px] overflow-y-auto">
                    {activeDatasetsList.map(ds => (
                      <div key={ds.id} className="flex items-center gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse shrink-0" />
                        <span className="text-[11px] font-bold text-slate-300 font-mono truncate max-w-[200px]" title={ds.display_name}>
                          {ds.display_name}
                        </span>
                      </div>
                    ))}
                    {activeCount === 0 && (
                      <span className="text-[11px] text-slate-600 italic">No datasets are currently active.</span>
                    )}
                  </div>
                </div>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => setSettingsOpen(true)}
                  className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 bg-slate-950 hover:bg-slate-850 border border-slate-800 text-slate-400 hover:text-slate-250 text-xs font-bold rounded-xl cursor-pointer transition-all font-mono uppercase tracking-wider"
                >
                  <Settings className="w-3.5 h-3.5" />
                  <span>Config Limits</span>
                </button>
                <button
                  onClick={() => loadDatasets()}
                  disabled={loading}
                  className="p-2.5 bg-slate-950 hover:bg-slate-850 border border-slate-800 text-slate-400 hover:text-slate-200 rounded-xl cursor-pointer transition-all disabled:opacity-50"
                  title="Sync Directory"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
                </button>
              </div>
            </div>
          </div>

          {/* Dataset Registry Table Section */}
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-3xl overflow-hidden backdrop-blur-md">
            <div className="p-5 border-b border-slate-900/80 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="flex items-center gap-2.5">
                <Layers className="w-4 h-4 text-violet-400" />
                <h4 className="text-xs font-black text-slate-300 uppercase tracking-widest">
                  File Registry Directory
                </h4>
              </div>

              {/* Search Box */}
              <div className="relative max-w-xs w-full">
                <Search className="w-3.5 h-3.5 absolute left-3 top-3 text-slate-500" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search by name or file..."
                  className="bg-slate-950/80 border border-slate-850 rounded-xl pl-9 pr-4 py-2 text-xs text-slate-200 w-full outline-none focus:border-violet-500 transition-all font-mono"
                />
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-900 bg-slate-950/20 text-[10px] font-bold text-slate-500 uppercase tracking-wider font-mono">
                    <th className="px-6 py-3.5 text-left">Dataset Name</th>
                    <th className="px-6 py-3.5 text-left">File Info</th>
                    <th className="px-6 py-3.5 text-left">Status</th>
                    <th className="px-6 py-3.5 text-right">Row Count</th>
                    <th className="px-6 py-3.5 text-right">Col Count</th>
                    <th className="px-6 py-3.5 text-left">Upload Time</th>
                    <th className="px-6 py-3.5 text-center">Active Status</th>
                    <th className="px-6 py-3.5 text-center">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-900/40 font-mono text-xs text-slate-300">
                  {loading && datasets.length === 0 ? (
                    [...Array(3)].map((_, i) => (
                      <tr key={i} className="animate-pulse">
                        <td colSpan={8} className="px-6 py-6 text-center">
                          <div className="h-4 bg-slate-950 rounded w-1/3 mx-auto" />
                        </td>
                      </tr>
                    ))
                  ) : filteredDatasets.length === 0 ? (
                    <tr>
                      <td
                        colSpan={8}
                        className="px-6 py-12 text-center text-slate-550 text-xs uppercase tracking-widest select-none"
                      >
                        {searchQuery ? "No matching files found." : "No datasets uploaded."}
                      </td>
                    </tr>
                  ) : (
                    filteredDatasets.map((ds) => (
                      <tr
                        key={ds.id}
                        className={`hover:bg-slate-950/20 transition-all ${ds.is_active ? "bg-violet-500/[0.01] border-l-2 border-violet-500" : ""
                          }`}
                      >
                        <td className="px-6 py-4 font-sans font-bold text-slate-200">
                          <div className="flex items-center gap-2">
                            <span>{ds.display_name}</span>
                            {ds.is_active && (
                              <span className="w-1.5 h-1.5 rounded-full bg-violet-400 animate-pulse" title="Currently Active" />
                            )}
                          </div>
                          {ds.description && (
                            <div className="text-[10px] text-slate-500 font-sans font-normal mt-0.5 max-w-xs truncate" title={ds.description}>
                              {ds.description}
                            </div>
                          )}
                        </td>
                        <td className="px-6 py-4 text-left">
                          <div className="text-slate-300 max-w-xs truncate font-mono text-[11px]" title={ds.original_filename}>
                            {ds.original_filename}
                          </div>
                          <div className="text-[10px] text-slate-555 mt-0.5">
                            {ds.source_type} • {formatBytes(ds.file_size)}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {getStatusBadge(ds)}
                        </td>
                        <td className="px-6 py-4 text-right font-bold text-slate-200">
                          {ds.status === "Ready" ? ds.row_count.toLocaleString() : "-"}
                        </td>
                        <td className="px-6 py-4 text-right text-slate-400">
                          {ds.status === "Ready" ? (ds.column_count ?? 0) : "-"}
                        </td>
                        <td className="px-6 py-4 text-slate-450 text-[11px]">
                          {ds.upload_time
                            ? new Date(ds.upload_time).toLocaleString("en-IN")
                            : new Date(ds.created_at || "").toLocaleString("en-IN")}
                        </td>
                        <td className="px-6 py-4 text-center">
                          {ds.status === "Ready" ? (
                            <button
                              onClick={() => handleToggleActive(ds)}
                              disabled={actionLoading}
                              className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border text-xs font-bold font-sans cursor-pointer transition-all disabled:opacity-50 ${ds.is_active
                                  ? "bg-violet-600/10 text-violet-400 border-violet-500/20 hover:bg-red-500/10 hover:text-red-400 hover:border-red-500/20"
                                  : "bg-slate-950 border-slate-850 hover:border-violet-500/40 text-slate-300"
                                }`}
                              title={ds.is_active ? "Deactivate dataset" : "Activate dataset"}
                            >
                              {ds.is_active ? (
                                <>
                                  <Pause className="w-3.5 h-3.5 shrink-0" />
                                  <span>Deactivate</span>
                                </>
                              ) : (
                                <>
                                  <Play className="w-3.5 h-3.5 shrink-0 fill-slate-300" />
                                  <span>Activate</span>
                                </>
                              )}
                            </button>
                          ) : (
                            <span className="text-slate-600 text-xs font-sans">—</span>
                          )}
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center justify-center gap-2">
                            {/* Preview button */}
                            {ds.status === "Ready" && (
                              <button
                                onClick={() => handleOpenPreview(ds)}
                                className="p-1.5 bg-slate-950 hover:bg-slate-850 border border-slate-850 hover:border-slate-750 text-slate-400 hover:text-violet-400 rounded-lg cursor-pointer transition-all"
                                title="Preview dataset schema & stats"
                              >
                                <Eye className="w-3.5 h-3.5" />
                              </button>
                            )}

                            {/* Delete/Archive button */}
                            {ds.status !== "Archived" && !ds.is_active && (
                              <button
                                onClick={() => setDeleteConfirmDataset(ds)}
                                className="p-1.5 bg-red-500/10 hover:bg-red-500/15 border border-red-500/20 text-red-400 rounded-lg cursor-pointer transition-all"
                                title="Soft delete / archive"
                              >
                                <Trash2 className="w-3.5 h-3.5" />
                              </button>
                            )}

                            {/* Permanent Delete button */}
                            {ds.status === "Archived" && (
                              <button
                                onClick={() => handlePermanentDelete(ds)}
                                className="p-1.5 bg-red-600/20 hover:bg-red-600/35 border border-red-500/30 text-red-400 rounded-lg cursor-pointer transition-all"
                                title="Permanently delete from database & disk"
                              >
                                <Trash2 className="w-3.5 h-3.5 text-red-500 font-bold" />
                              </button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>



      {/* ── SETTINGS CONFIGURATION MODAL ── */}
      {settingsOpen && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl w-full max-w-md p-6 space-y-6 shadow-2xl relative animate-zoom-in text-slate-200">
            <button
              onClick={() => setSettingsOpen(false)}
              className="absolute top-4 right-4 p-1.5 text-slate-400 hover:text-slate-200 rounded-full hover:bg-slate-800 cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>

            <div>
              <h3 className="text-base font-black text-slate-100 uppercase tracking-tight flex items-center gap-2">
                <Settings className="w-5 h-5 text-violet-400" />
                <span>Dataset Config settings</span>
              </h3>
              <p className="text-xs text-slate-500 mt-1">
                Configure dataset execution constraints for intelligence modules.
              </p>
            </div>

            <form onSubmit={handleSettingsSubmit} className="space-y-5">
              <div className="flex flex-col gap-2.5">
                <span className="text-[10px] font-bold text-slate-450 uppercase tracking-wider block">
                  Maximum Active Datasets *
                </span>
                <div className="grid grid-cols-4 gap-2 font-mono text-xs">
                  {["1", "2", "3", "All"].map((opt) => (
                    <label
                      key={opt}
                      className={`flex flex-col items-center justify-center p-3.5 border rounded-2xl cursor-pointer transition-all ${maxActiveInput === opt
                          ? "bg-violet-600/10 border-violet-500 text-violet-450 font-black shadow-[0_4px_12px_rgba(99,102,241,0.05)]"
                          : "bg-slate-950 border-slate-850 text-slate-400 hover:border-slate-800"
                        }`}
                    >
                      <input
                        type="radio"
                        name="maxActive"
                        value={opt}
                        checked={maxActiveInput === opt}
                        onChange={(e) => setMaxActiveInput(e.target.value)}
                        className="hidden"
                      />
                      <span>{opt}</span>
                    </label>
                  ))}
                </div>
                <div className="bg-slate-950/40 border border-slate-850/60 rounded-xl p-3.5 text-[10px] text-slate-500 leading-normal font-mono uppercase tracking-wider">
                  {maxActiveInput === "1" ? (
                    "Activating any dataset deactivates all others immediately."
                  ) : maxActiveInput === "All" ? (
                    "Unlimited datasets can remain active simultaneously."
                  ) : (
                    `Up to ${maxActiveInput} active. Exceeding deactivates oldest active sets.`
                  )}
                </div>
              </div>

              <div className="pt-4 border-t border-slate-850 flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setSettingsOpen(false)}
                  className="px-5 py-2.5 bg-slate-950 hover:bg-slate-850 border border-slate-850 text-slate-400 hover:text-slate-205 rounded-xl text-xs font-bold cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={actionLoading}
                  className="px-6 py-2.5 bg-violet-600 hover:bg-violet-750 text-white rounded-xl text-xs font-bold cursor-pointer transition-all disabled:opacity-50 uppercase tracking-wider"
                >
                  Save Settings
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ── PREVIEW MODAL ── */}
      {previewDataset && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl w-full max-w-5xl h-[85vh] flex flex-col shadow-2xl relative animate-zoom-in text-slate-200">
            {/* Modal Header */}
            <div className="p-6 border-b border-slate-850 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2.5 bg-violet-500/10 border border-violet-500/20 text-violet-400 rounded-xl">
                  <Info className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-black text-slate-100 uppercase tracking-tight">
                    Dataset Inspector
                  </h3>
                  <p className="text-[10px] text-slate-500 font-mono">
                    {previewDataset.display_name} • {previewDataset.original_filename}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setPreviewDataset(null)}
                className="p-1.5 text-slate-400 hover:text-slate-200 rounded-full hover:bg-slate-800 cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal tabs */}
            <div className="flex border-b border-slate-850 px-6 bg-slate-950/20">
              {(["data", "schema", "statistics"] as PreviewTabId[]).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setPreviewTab(tab)}
                  className={`py-3 px-4 text-[10px] uppercase tracking-widest font-black transition-all border-b-2 relative cursor-pointer ${previewTab === tab
                      ? "text-violet-400 border-violet-500 bg-violet-500/[0.02]"
                      : "text-slate-500 hover:text-slate-350 border-transparent"
                    }`}
                >
                  {tab === "data" ? "Data Preview (20 Rows)" : tab === "schema" ? "Columns Schema" : "Dataset Statistics"}
                </button>
              ))}
            </div>

            {/* Modal content body */}
            <div className="flex-1 overflow-y-auto p-6 min-h-[300px]">
              {previewLoading ? (
                <div className="h-full flex flex-col items-center justify-center text-slate-500 text-xs font-bold gap-3 font-mono">
                  <RefreshCw className="w-7 h-7 animate-spin text-violet-400" />
                  <span>Analyzing dataset properties...</span>
                </div>
              ) : (
                <>
                  {/* Tab 1: Data Preview Table */}
                  {previewTab === "data" && previewData && (
                    <div className="h-full flex flex-col justify-between">
                      <div className="border border-slate-950 rounded-2xl overflow-hidden overflow-x-auto bg-slate-950/30 max-h-[480px]">
                        <table className="w-full text-xs text-left">
                          <thead>
                            <tr className="border-b border-slate-900 bg-slate-950/50 text-[10px] font-bold text-slate-500 uppercase font-mono">
                              <th className="px-4 py-2.5 text-center w-12 border-r border-slate-900">#</th>
                              {previewData.columns.map((col) => (
                                <th key={col} className="px-4 py-2.5 whitespace-nowrap font-mono">{col}</th>
                              ))}
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-slate-900/60 font-mono text-[11px] text-slate-355">
                            {previewData.first_20_rows.map((row, idx) => (
                              <tr key={idx} className="hover:bg-slate-950/40">
                                <td className="px-4 py-2 text-center bg-slate-950/30 text-slate-550 border-r border-slate-900 font-bold">
                                  {idx + 1}
                                </td>
                                {previewData.columns.map((col) => (
                                  <td key={col} className="px-4 py-2 whitespace-nowrap">
                                    {row[col] === null ? (
                                      <span className="text-slate-650 italic">null</span>
                                    ) : (
                                      String(row[col])
                                    )}
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                      <p className="text-[10px] text-slate-505 font-mono mt-3 uppercase tracking-wider">
                        Showing first 20 records • Total Rows: {previewData.total_rows.toLocaleString()} • Columns: {previewData.total_columns}
                      </p>
                    </div>
                  )}

                  {/* Tab 2: Columns Schema */}
                  {previewTab === "schema" && previewData && (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {previewData.columns.map((col) => {
                        const dtype = previewData.data_types[col] || "string";
                        return (
                          <div
                            key={col}
                            className="bg-slate-950/40 border border-slate-850 p-4 rounded-2xl flex items-center justify-between font-mono"
                          >
                            <div>
                              <span className="text-slate-450 block font-bold text-xs truncate max-w-[200px]" title={col}>
                                {col}
                              </span>
                              <span className="text-[9px] text-slate-605 block uppercase tracking-widest mt-1">
                                Column Header
                              </span>
                            </div>
                            <span className={`px-2.5 py-0.5 rounded text-[10px] font-black uppercase tracking-wider ${dtype === "integer" || dtype === "float"
                                ? "bg-cyan-500/10 text-cyan-400 border border-cyan-500/20"
                                : dtype === "boolean"
                                  ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                                  : "bg-violet-500/10 text-violet-400 border border-violet-500/20"
                              }`}>
                              {dtype}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  )}

                  {/* Tab 3: Detailed Statistics */}
                  {previewTab === "statistics" && previewStats && (
                    <div className="space-y-6">
                      {/* Metric cards */}
                      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-center font-mono">
                        <div className="bg-slate-950/50 p-4 border border-slate-850 rounded-2xl">
                          <p className="text-[9px] font-bold text-slate-550 uppercase tracking-widest">Total Rows</p>
                          <p className="text-2xl font-black text-slate-200 mt-1">{previewStats.total_rows.toLocaleString()}</p>
                        </div>
                        <div className="bg-slate-950/50 p-4 border border-slate-850 rounded-2xl">
                          <p className="text-[9px] font-bold text-slate-555 uppercase tracking-widest">Total Columns</p>
                          <p className="text-2xl font-black text-slate-200 mt-1">{previewStats.total_columns}</p>
                        </div>
                        <div className="bg-slate-950/50 p-4 border border-slate-850 rounded-2xl">
                          <p className="text-[9px] font-bold text-slate-555 uppercase tracking-widest">Duplicate Rows</p>
                          <p className={`text-2xl font-black mt-1 ${previewStats.duplicate_rows > 0 ? "text-amber-400" : "text-emerald-400"}`}>
                            {previewStats.duplicate_rows}
                          </p>
                        </div>
                        <div className="bg-slate-950/50 p-4 border border-slate-850 rounded-2xl">
                          <p className="text-[9px] font-bold text-slate-555 uppercase tracking-widest">Corrupted/Empty Cells</p>
                          <p className="text-2xl font-black text-slate-200 mt-1">
                            {Object.values(previewStats.missing_values).reduce((a, b) => a + b, 0).toLocaleString()}
                          </p>
                        </div>
                      </div>

                      {/* Numeric vs Categorical classification */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="bg-slate-950/30 border border-slate-850 rounded-2xl p-5 font-mono">
                          <h5 className="text-[10px] font-black text-violet-400 uppercase tracking-widest mb-3 flex items-center gap-1.5">
                            <BarChart className="w-3.5 h-3.5" />
                            <span>Numeric Features ({previewStats.numeric_columns.length})</span>
                          </h5>
                          <div className="flex flex-wrap gap-1.5">
                            {previewStats.numeric_columns.map(col => (
                              <span key={col} className="bg-slate-900 border border-slate-850 px-2 py-0.5 rounded text-[10px] text-slate-400">
                                {col}
                              </span>
                            ))}
                            {previewStats.numeric_columns.length === 0 && (
                              <span className="text-slate-600 italic text-[11px]">No numeric columns discovered.</span>
                            )}
                          </div>
                        </div>

                        <div className="bg-slate-950/30 border border-slate-850 rounded-2xl p-5 font-mono">
                          <h5 className="text-[10px] font-black text-cyan-400 uppercase tracking-widest mb-3 flex items-center gap-1.5">
                            <FileCode className="w-3.5 h-3.5" />
                            <span>Categorical Features ({previewStats.categorical_columns.length})</span>
                          </h5>
                          <div className="flex flex-wrap gap-1.5">
                            {previewStats.categorical_columns.map(col => (
                              <span key={col} className="bg-slate-900 border border-slate-850 px-2 py-0.5 rounded text-[10px] text-slate-400">
                                {col}
                              </span>
                            ))}
                            {previewStats.categorical_columns.length === 0 && (
                              <span className="text-slate-600 italic text-[11px]">No categorical columns discovered.</span>
                            )}
                          </div>
                        </div>
                      </div>

                      {/* Missing values breakdown */}
                      <div className="bg-slate-950/30 border border-slate-850 rounded-2xl p-5 font-mono">
                        <h5 className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-3">
                          Missing Values Count Per Column
                        </h5>
                        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                          {Object.entries(previewStats.missing_values).map(([col, count]) => (
                            <div key={col} className="flex justify-between items-center text-[11px] p-2 bg-slate-900 rounded-xl border border-slate-850/60">
                              <span className="text-slate-400 truncate max-w-[130px] font-bold" title={col}>{col}</span>
                              <span className={`font-black ${count > 0 ? "text-amber-400" : "text-slate-600"}`}>{count}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>

            {/* Modal Footer */}
            <div className="p-6 border-t border-slate-850 flex justify-end">
              <button
                onClick={() => setPreviewDataset(null)}
                className="px-5 py-2.5 bg-slate-950 hover:bg-slate-850 border border-slate-850 text-slate-400 hover:text-slate-200 rounded-xl text-xs font-bold cursor-pointer"
              >
                Close Inspector
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── DELETE CONFIRMATION DIALOG ── */}
      {deleteConfirmDataset && mounted && createPortal(
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl w-full max-w-md p-6 space-y-6 shadow-2xl relative animate-zoom-in text-slate-200">
            <div>
              <h3 className="text-base font-black text-red-400 uppercase tracking-tight flex items-center gap-2">
                <Trash2 className="w-5 h-5" />
                <span>Archive Dataset?</span>
              </h3>
              <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                Are you sure you want to delete / archive the dataset <span className="font-mono font-bold text-slate-200">"{deleteConfirmDataset.display_name}"</span>?
              </p>
              <div className="bg-red-500/5 border border-red-500/10 rounded-xl p-3 text-[10px] text-red-400/80 leading-normal font-mono mt-3 uppercase tracking-wider">
                Note: This will perform a soft delete. The dataset status will be updated to "Archived", but the physical record file will remain preserved for platform integrity logs.
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-2">
              <button
                onClick={() => setDeleteConfirmDataset(null)}
                disabled={actionLoading}
                className="px-5 py-2.5 bg-slate-950 hover:bg-slate-850 text-slate-400 hover:text-slate-250 border border-slate-850 rounded-xl text-xs font-bold cursor-pointer disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                disabled={actionLoading}
                className="px-6 py-2.5 bg-red-650 hover:bg-red-750 text-white rounded-xl text-xs font-bold cursor-pointer transition-all disabled:opacity-50 uppercase tracking-wider"
              >
                {actionLoading ? "Processing..." : "Confirm Deletion"}
              </button>
            </div>
          </div>
        </div>,
        document.body
      )}
    </div>
  );
}
