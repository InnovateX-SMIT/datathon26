"use client";

import React, { useState, useEffect, useRef } from "react";
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
  FileCode
} from "lucide-react";
import {
  fetchDatasets,
  uploadDatasets,
  deleteDataset,
  fetchDatasetPreview,
  fetchDatasetStatistics,
  DatasetInfo,
  DatasetPreview,
  DatasetStatistics
} from "@/features/admin/services/database-service";

type PreviewTabId = "data" | "schema" | "statistics";

export default function DatasetManagerPage() {
  const [datasets, setDatasets] = useState<DatasetInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Drag and drop state
  const [dragActive, setDragActive] = useState(false);
  const [uploadFiles, setUploadFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [displayNameInput, setDisplayNameInput] = useState("");
  const [descriptionInput, setDescriptionInput] = useState("");

  // Preview Modal state
  const [previewDataset, setPreviewDataset] = useState<DatasetInfo | null>(null);
  const [previewData, setPreviewData] = useState<DatasetPreview | null>(null);
  const [previewStats, setPreviewStats] = useState<DatasetStatistics | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [previewTab, setPreviewTab] = useState<PreviewTabId>("data");

  // Delete Confirm Modal state
  const [deleteConfirmDataset, setDeleteConfirmDataset] = useState<DatasetInfo | null>(null);
  const [actionLoading, setActionLoading] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadDatasets();
  }, []);

  const loadDatasets = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchDatasets();
      setDatasets(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to fetch dataset registry.");
    } finally {
      setLoading(false);
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
      setError(null);
    }
  };

  const removeUploadFile = (index: number) => {
    setUploadFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
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
      await uploadDatasets(
        displayNameInput.trim() !== "" ? displayNameInput : null,
        descriptionInput.trim() !== "" ? descriptionInput : null,
        uploadFiles
      );
      
      setUploadProgress(100);
      setTimeout(() => {
        setSuccess(`Successfully uploaded and validated ${uploadFiles.length} dataset(s).`);
        setUploadFiles([]);
        setDisplayNameInput("");
        setDescriptionInput("");
        setUploading(false);
        loadDatasets();
      }, 400);
    } catch (err: any) {
      clearInterval(progressInterval);
      setError(err.response?.data?.detail || "Dataset validation or upload failed.");
      setUploading(false);
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

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "Ready":
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            Ready
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
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-slate-800 border border-slate-700 text-slate-400">
            <span className="w-1.5 h-1.5 rounded-full bg-slate-500" />
            Archived
          </span>
        );
      case "Uploading":
      case "Validating":
      case "Importing":
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-amber-500/10 border border-amber-500/20 text-amber-400 animate-pulse">
            <RefreshCw className="w-3 h-3 animate-spin text-amber-400 shrink-0" />
            {status}
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-slate-500/10 border border-slate-500/20 text-slate-400">
            {status}
          </span>
        );
    }
  };

  // Filters search results
  const filteredDatasets = datasets.filter(
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
              <p className="text-slate-400 text-xs font-semibold uppercase tracking-widest mt-1">
                Phase 1 — Dynamic Dataset Management Foundation
              </p>
            </div>
          </div>
          <p className="text-slate-400 text-sm mt-3 max-w-2xl leading-relaxed">
            Register, validate, preview, and review statistical integrity parameters of incident files. Supported extensions are CSV and Excel.
          </p>
        </div>

        {/* Global Active indicator */}
        <div className="flex items-center gap-2 px-4 py-2.5 bg-violet-500/10 border border-violet-500/20 rounded-2xl self-start">
          <span className="w-2 h-2 rounded-full bg-violet-400 animate-pulse" />
          <span className="text-violet-400 text-xs font-black uppercase tracking-wider">
            Registry Connected
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
            <p className="text-[11px] text-slate-500 mt-1">
              Select or drop multiple spreadsheet datasets simultaneously.
            </p>
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
                className={`border-2 border-dashed rounded-2xl p-6 text-center cursor-pointer transition-all bg-slate-950/20 relative group min-h-[140px] flex flex-col justify-center items-center ${
                  dragActive ? "border-violet-500 bg-violet-500/[0.02]" : "border-slate-800 hover:border-violet-500/40"
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
                  <p className="text-[10px] text-slate-550 mt-1 uppercase font-mono tracking-widest">
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
                        className="text-slate-500 hover:text-red-400 transition-colors p-1"
                      >
                        <X className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

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
                    onClick={() => setUploadFiles([])}
                    disabled={uploading}
                    className="px-4 py-2 bg-slate-950 hover:bg-slate-850 border border-slate-850 text-slate-400 hover:text-slate-200 rounded-xl text-xs font-bold transition-all disabled:opacity-50 cursor-pointer"
                  >
                    Clear All
                  </button>
                )}
                <button
                  type="submit"
                  disabled={uploading || uploadFiles.length === 0}
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
                      <span>Commit Validation</span>
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
            <p className="text-[11px] text-slate-500 mt-1">
              Platform state overview across all registered file contexts.
            </p>
          </div>

          <div className="space-y-4">
            <div className="bg-slate-950/40 p-4 border border-slate-900 rounded-2xl">
              <span className="text-[9px] font-bold text-slate-550 uppercase tracking-widest block font-mono">
                Total Registered Datasets
              </span>
              <p className="text-4xl font-black text-violet-400 font-mono mt-1">
                {datasets.length}
              </p>
            </div>
            <div className="bg-slate-950/40 p-4 border border-slate-900 rounded-2xl">
              <span className="text-[9px] font-bold text-slate-550 uppercase tracking-widest block font-mono">
                Active Dataset Context
              </span>
              <div className="flex items-center gap-2 mt-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                <span className="text-xs font-bold text-slate-200 font-mono truncate max-w-[200px]">
                  {datasets.find(d => d.is_active)?.display_name || "System Seed"}
                </span>
              </div>
            </div>
          </div>

          <button
            onClick={loadDatasets}
            disabled={loading}
            className="w-full flex items-center justify-center gap-1.5 px-4 py-2.5 bg-slate-950 hover:bg-slate-850 border border-slate-800 hover:border-slate-700 text-slate-300 hover:text-slate-100 text-xs font-bold rounded-xl cursor-pointer transition-all disabled:opacity-50 font-mono uppercase tracking-wider"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
            <span>Sync Directory</span>
          </button>
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
                <th className="px-6 py-3.5 text-center">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-900/40 font-mono text-xs text-slate-300">
              {loading && datasets.length === 0 ? (
                [...Array(3)].map((_, i) => (
                  <tr key={i} className="animate-pulse">
                    <td colSpan={7} className="px-6 py-6 text-center">
                      <div className="h-4 bg-slate-950 rounded w-1/3 mx-auto" />
                    </td>
                  </tr>
                ))
              ) : filteredDatasets.length === 0 ? (
                <tr>
                  <td
                    colSpan={7}
                    className="px-6 py-12 text-center text-slate-500 text-xs uppercase tracking-widest select-none"
                  >
                    {searchQuery ? "No matching files found." : "No datasets uploaded."}
                  </td>
                </tr>
              ) : (
                filteredDatasets.map((ds) => (
                  <tr
                    key={ds.id}
                    className={`hover:bg-slate-950/20 transition-all ${
                      ds.is_active ? "bg-violet-500/[0.02]" : ""
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
                      <div className="text-[10px] text-slate-550 mt-0.5">
                        {ds.source_type} • {formatBytes(ds.file_size)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getStatusBadge(ds.status)}
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
                    <td className="px-6 py-4">
                      <div className="flex items-center justify-center gap-2">
                        {/* Preview button */}
                        {ds.status === "Ready" && (
                          <button
                            onClick={() => handleOpenPreview(ds)}
                            className="p-1.5 bg-slate-950 hover:bg-slate-850 border border-slate-850 hover:border-slate-750 text-slate-400 hover:text-violet-400 rounded-lg cursor-pointer transition-all flex items-center gap-1 text-[11px] font-bold font-sans"
                            title="Preview file contents & statistics"
                          >
                            <Eye className="w-3.5 h-3.5" />
                            <span>Preview</span>
                          </button>
                        )}
                        
                        {/* Delete/Archive button */}
                        {ds.name !== "System Seed" && ds.display_name !== "Synthetic 50K" && ds.status !== "Archived" && !ds.is_active && (
                          <button
                            onClick={() => setDeleteConfirmDataset(ds)}
                            className="p-1.5 bg-red-500/10 hover:bg-red-500/15 border border-red-500/20 text-red-400 rounded-lg cursor-pointer transition-all flex items-center gap-1 text-[11px] font-bold font-sans"
                            title="Soft delete / archive"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                            <span>Delete</span>
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
                  <p className="text-[10px] text-slate-550 font-mono">
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
            <div className="flex border-b border-slate-855 px-6 bg-slate-950/20">
              {(["data", "schema", "statistics"] as PreviewTabId[]).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setPreviewTab(tab)}
                  className={`py-3 px-4 text-[10px] uppercase tracking-widest font-black transition-all border-b-2 relative cursor-pointer ${
                    previewTab === tab
                      ? "text-violet-400 border-violet-500 bg-violet-500/[0.02]"
                      : "text-slate-500 hover:text-slate-355 border-transparent"
                  }`}
                >
                  {tab === "data" ? "Data Preview (20 Rows)" : tab === "schema" ? "Columns Schema" : "Dataset Statistics"}
                </button>
              ))}
            </div>

            {/* Modal content body */}
            <div className="flex-1 overflow-y-auto p-6 min-h-[300px]">
              {previewLoading ? (
                <div className="h-full flex flex-col items-center justify-center text-slate-505 text-xs font-bold gap-3 font-mono">
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
                          <tbody className="divide-y divide-slate-900/60 font-mono text-[11px] text-slate-350">
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
                      <p className="text-[10px] text-slate-500 font-mono mt-3 uppercase tracking-wider">
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
                              <span className="text-[9px] text-slate-600 block uppercase tracking-widest mt-1">
                                Column Header
                              </span>
                            </div>
                            <span className={`px-2.5 py-0.5 rounded text-[10px] font-black uppercase tracking-wider ${
                              dtype === "integer" || dtype === "float"
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
                        <div className="bg-slate-950/50 p-4 border border-slate-855 rounded-2xl">
                          <p className="text-[9px] font-bold text-slate-500 uppercase tracking-widest">Total Rows</p>
                          <p className="text-2xl font-black text-slate-200 mt-1">{previewStats.total_rows.toLocaleString()}</p>
                        </div>
                        <div className="bg-slate-950/50 p-4 border border-slate-855 rounded-2xl">
                          <p className="text-[9px] font-bold text-slate-500 uppercase tracking-widest">Total Columns</p>
                          <p className="text-2xl font-black text-slate-200 mt-1">{previewStats.total_columns}</p>
                        </div>
                        <div className="bg-slate-950/50 p-4 border border-slate-855 rounded-2xl">
                          <p className="text-[9px] font-bold text-slate-500 uppercase tracking-widest">Duplicate Rows</p>
                          <p className={`text-2xl font-black mt-1 ${previewStats.duplicate_rows > 0 ? "text-amber-400" : "text-emerald-400"}`}>
                            {previewStats.duplicate_rows}
                          </p>
                        </div>
                        <div className="bg-slate-950/50 p-4 border border-slate-855 rounded-2xl">
                          <p className="text-[9px] font-bold text-slate-500 uppercase tracking-widest">Corrupted/Empty Cells</p>
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
                              <span key={col} className="bg-slate-900 border border-slate-855 px-2 py-0.5 rounded text-[10px] text-slate-400">
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
                            <div key={col} className="flex justify-between items-center text-[11px] p-2 bg-slate-900 rounded-xl border border-slate-855/60">
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
                className="px-5 py-2.5 bg-slate-950 hover:bg-slate-850 border border-slate-855 text-slate-400 hover:text-slate-200 rounded-xl text-xs font-bold cursor-pointer"
              >
                Close Inspector
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── DELETE CONFIRMATION DIALOG ── */}
      {deleteConfirmDataset && (
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
        </div>
      )}
    </div>
  );
}
