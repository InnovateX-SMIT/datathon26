"use client";

import React, { useState, useEffect } from "react";
import {
  HardDrive,
  RefreshCw,
  Upload,
  Play,
  Trash2,
  AlertCircle,
  CheckCircle2,
  FileSpreadsheet,
  Calendar,
  Layers,
  Users,
  Eye,
  X,
  MapPin,
  ChevronRight,
  Info
} from "lucide-react";
import {
  fetchDatasets,
  uploadDataset,
  activateDataset,
  deleteDataset,
  fetchDatasetSummary,
  detectSchemaType,
  importFIRDataset,
  DatasetInfo,
  DatasetSummary
} from "@/features/admin/services/database-service";

interface DatasetRegistryManagerProps {
  onDatasetSwitched?: () => void;
}

export default function DatasetRegistryManager({ onDatasetSwitched }: DatasetRegistryManagerProps) {
  const [datasets, setDatasets] = useState<DatasetInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Upload Form State
  const [uploadOpen, setUploadOpen] = useState(false);
  const [displayName, setDisplayName] = useState("");
  const [description, setDescription] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewSummary, setPreviewSummary] = useState<any>(null);
  const [previewSchemaType, setPreviewSchemaType] = useState<string | null>(null);
  const [isValidated, setIsValidated] = useState<boolean>(false);

  // Details / Summary Modal State
  const [selectedDataset, setSelectedDataset] = useState<DatasetInfo | null>(null);
  const [summaryData, setSummaryData] = useState<DatasetSummary | null>(null);
  const [summaryLoading, setSummaryLoading] = useState(false);

  useEffect(() => {
    loadDatasets();
  }, []);
  async function loadDatasets() {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchDatasets();
      setDatasets(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to fetch registered datasets.");
    } finally {
      setLoading(false);
    }
  }

  const handleActivate = async (id: number) => {
    setActionLoading(true);
    setError(null);
    setSuccess(null);
    try {
      await activateDataset(id);
      setSuccess("Active dataset switched successfully.");
      await loadDatasets();
      if (onDatasetSwitched) {
        onDatasetSwitched();
      }
      // Emit a global event to notify all components to refresh their queries
      window.dispatchEvent(new Event("activeDatasetChanged"));
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to switch active dataset.");
    } finally {
      setActionLoading(false);
    }
  };

  const handleDelete = async (ds: DatasetInfo) => {
    if (ds.is_active) {
      setError("Active dataset must be deactivated before archiving.");
      return;
    }

    const confirmMsg = `Are you sure you want to archive "${ds.display_name}"? \nAll records will remain stored for auditability, but the dataset status will be marked as Archived.`;
    if (!confirm(confirmMsg)) return;

    setActionLoading(true);
    setError(null);
    setSuccess(null);
    try {
      await deleteDataset(ds.id);
      setSuccess("Dataset archived successfully.");
      await loadDatasets();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to archive dataset.");
    } finally {
      setActionLoading(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFile(e.target.files[0]);
      if (!displayName) {
        // Auto fill displayName from file name
        const nameWithoutExt = e.target.files[0].name.replace(/\.[^/.]+$/, "");
        setDisplayName(nameWithoutExt.replace(/[_-]/g, " ").replace(/\b\w/g, c => c.toUpperCase()));
      }
    }
  };

  const handleValidatePreview = async () => {
    if (!selectedFile || !displayName.trim()) {
      setError("Please select a file and enter a display name.");
      return;
    }
    setActionLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const { schema_type } = await detectSchemaType(selectedFile);
      setPreviewSchemaType(schema_type);
      
      let summary;
      if (schema_type === "fir_normalized") {
        summary = await importFIRDataset(displayName, description || null, selectedFile, true);
      } else {
        summary = await uploadDataset(displayName, description || null, selectedFile, true);
      }
      setPreviewSummary(summary);
      setIsValidated(true);
      setSuccess(`File validated: ${summary.valid_count} valid rows, ${summary.invalid_count} row errors found.`);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Validation failed. Verify file format and column headers.");
    } finally {
      setActionLoading(false);
    }
  };

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile || !displayName.trim()) {
      setError("Please select a file and enter a display name.");
      return;
    }

    setActionLoading(true);
    setError(null);
    setSuccess(null);
    try {
      if (previewSchemaType === "fir_normalized") {
        await importFIRDataset(displayName, description || null, selectedFile, false);
      } else {
        await uploadDataset(displayName, description || null, selectedFile, false);
      }
      setSuccess(`Dataset "${displayName}" uploaded and registered successfully.`);
      setUploadOpen(false);
      setDisplayName("");
      setDescription("");
      setSelectedFile(null);
      setPreviewSummary(null);
      setPreviewSchemaType(null);
      setIsValidated(false);
      await loadDatasets();
      if (onDatasetSwitched) {
        onDatasetSwitched();
      }
      window.dispatchEvent(new Event("activeDatasetChanged"));
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to upload dataset.");
    } finally {
      setActionLoading(false);
    }
  };

  const handleViewSummary = async (ds: DatasetInfo) => {
    setSelectedDataset(ds);
    setSummaryData(null);
    if (ds.status !== "Ready") return;

    setSummaryLoading(true);
    try {
      const summary = await fetchDatasetSummary(ds.id);
      setSummaryData(summary);
    } catch (err) {
      console.error("Failed to load dataset summary", err);
    } finally {
      setSummaryLoading(false);
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
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            Ready
          </span>
        );
      case "Failed":
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-red-500/10 border border-red-500/20 text-red-400">
            <span className="w-1.5 h-1.5 rounded-full bg-red-400" />
            Failed
          </span>
        );
      case "Archived":
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-slate-800 border border-slate-700 text-slate-400">
            <span className="w-1.5 h-1.5 rounded-full bg-slate-500" />
            Archived
          </span>
        );
      case "Uploading":
      case "Validating":
      case "Importing":
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-500/10 border border-amber-500/20 text-amber-400 animate-pulse">
            <RefreshCw className="w-3 h-3 animate-spin" />
            {status}
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-slate-500/10 border border-slate-500/20 text-slate-400">
            {status}
          </span>
        );
    }
  };

  const activeDataset = datasets.find(d => d.is_active);

  return (
    <div className="space-y-6">
      {/* Messages */}
      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/20 text-red-400 text-xs rounded-2xl flex items-center gap-3">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <div className="flex-1">{error}</div>
          <button onClick={() => setError(null)} className="text-red-400 hover:text-red-300">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {success && (
        <div className="p-4 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs rounded-2xl flex items-center gap-3">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <div className="flex-1">{success}</div>
          <button onClick={() => setSuccess(null)} className="text-emerald-400 hover:text-emerald-300">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* ── Active Dataset Header ────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-gradient-to-r from-indigo-950/40 to-slate-950/40 p-6 border border-indigo-500/20 rounded-3xl backdrop-blur-md flex flex-col justify-between relative overflow-hidden">
          <div className="absolute top-0 right-0 p-8 opacity-[0.03] pointer-events-none">
            <Layers className="w-48 h-48 text-indigo-400" />
          </div>
          
          <div>
            <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest bg-indigo-500/10 px-3 py-1 rounded-full border border-indigo-500/20">
              Active Environment Dataset
            </span>
            {activeDataset ? (
              <div className="mt-4">
                <h3 className="text-2xl font-black text-slate-100 uppercase tracking-tight font-mono">
                  {activeDataset.display_name}
                </h3>
                <p className="text-slate-400 text-xs mt-1 leading-relaxed max-w-xl">
                  {activeDataset.description || "No description provided."}
                </p>
                <div className="flex flex-wrap gap-x-6 gap-y-2 mt-4 text-[11px] text-slate-500 font-semibold font-mono">
                  <div>File: <span className="text-slate-300">{activeDataset.original_filename}</span></div>
                  <div>Size: <span className="text-slate-300">{formatBytes(activeDataset.file_size)}</span></div>
                  <div>Rows: <span className="text-slate-300">{(activeDataset.row_count).toLocaleString()}</span></div>
                </div>
              </div>
            ) : (
              <div className="mt-4 text-slate-400 text-sm">
                No dataset is currently active. Please upload or activate a dataset to restore analytical functions.
              </div>
            )}
          </div>
        </div>

        {/* Action controls */}
        <div className="bg-slate-950/40 p-6 border border-slate-900 rounded-3xl backdrop-blur-md flex flex-col justify-between gap-4">
          <div>
            <h4 className="text-xs font-black text-slate-300 uppercase tracking-wider">
              Registry Controls
            </h4>
            <p className="text-[11px] text-slate-500 mt-1">
              Switch the active data context or upload spreadsheets to insert new records.
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => {
                setPreviewSummary(null);
                setPreviewSchemaType(null);
                setIsValidated(false);
                setUploadOpen(true);
              }}
              className="flex-1 flex items-center justify-center gap-1.5 px-4 py-3 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-2xl cursor-pointer transition-all shadow-md shadow-indigo-600/10"
            >
              <Upload className="w-4 h-4" />
              <span>Import Dataset</span>
            </button>
            <button
              onClick={loadDatasets}
              disabled={loading}
              className="px-4 py-3 bg-slate-900 border border-slate-800 hover:bg-slate-850 text-slate-300 rounded-2xl cursor-pointer transition-all disabled:opacity-50"
              title="Refresh Registry"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
            </button>
          </div>
        </div>
      </div>

      {/* ── Datasets Table ─────────────────────────────────────────────────── */}
      <div className="bg-slate-950/40 border border-slate-900 rounded-3xl overflow-hidden backdrop-blur-md">
        <div className="p-5 border-b border-slate-900/60 flex items-center justify-between">
          <h4 className="text-xs font-black text-slate-300 uppercase tracking-widest">
            Dataset Registry Directory
          </h4>
          <span className="text-[10px] text-slate-500 font-mono">
            {datasets.length} Registrations
          </span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-900 bg-slate-950/20 text-[10px] font-bold text-slate-500 uppercase tracking-wider">
                <th className="px-6 py-3.5 text-left">Display Name / File</th>
                <th className="px-6 py-3.5 text-left">Status</th>
                <th className="px-6 py-3.5 text-right">Row Count</th>
                <th className="px-6 py-3.5 text-right">File Size</th>
                <th className="px-6 py-3.5 text-left">Upload Date</th>
                <th className="px-6 py-3.5 text-center">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-900/40">
              {loading && datasets.length === 0 ? (
                [...Array(3)].map((_, i) => (
                  <tr key={i} className="animate-pulse">
                    <td colSpan={6} className="px-6 py-5 text-center">
                      <div className="h-4 bg-slate-900 rounded w-1/3 mx-auto" />
                    </td>
                  </tr>
                ))
              ) : datasets.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-slate-500 text-xs font-mono uppercase tracking-widest">
                    No datasets registered in system registry.
                  </td>
                </tr>
              ) : (
                datasets.map(ds => (
                  <tr
                    key={ds.id}
                    className={`hover:bg-slate-900/20 transition-all ${
                      ds.is_active ? "bg-indigo-500/[0.02]" : ""
                    }`}
                  >
                    <td className="px-6 py-4.5">
                      <div className="flex items-center gap-3">
                        <div className={`p-2 rounded-xl border ${
                          ds.is_active
                            ? "bg-indigo-500/10 border-indigo-500/20 text-indigo-400"
                            : "bg-slate-900 border-slate-800 text-slate-400"
                        }`}>
                          <FileSpreadsheet className="w-4 h-4" />
                        </div>
                        <div>
                          <div className="font-bold text-slate-200 flex items-center gap-2">
                            <span>{ds.display_name}</span>
                            {ds.is_active && (
                              <span className="inline-block w-2 h-2 rounded-full bg-indigo-400 animate-pulse" />
                            )}
                          </div>
                          <div className="text-[10px] text-slate-500 mt-0.5 font-mono">
                            {ds.original_filename}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4.5 whitespace-nowrap">
                      {getStatusBadge(ds.status)}
                    </td>
                    <td className="px-6 py-4.5 text-right font-mono font-bold text-slate-300">
                      {ds.status === "Ready" ? ds.row_count.toLocaleString() : "-"}
                    </td>
                    <td className="px-6 py-4.5 text-right font-mono text-slate-400">
                      {formatBytes(ds.file_size)}
                    </td>
                    <td className="px-6 py-4.5 text-slate-400 font-mono text-xs">
                      {(ds.upload_time || ds.created_at) ? new Date(ds.upload_time || ds.created_at || "").toLocaleString("en-IN") : "—"}
                    </td>
                    <td className="px-6 py-4.5">
                      <div className="flex items-center justify-center gap-2">
                        {/* Switch / Activate */}
                        {ds.status === "Ready" && !ds.is_active && (
                          <button
                            onClick={() => handleActivate(ds.id)}
                            disabled={actionLoading}
                            className="flex items-center gap-1 px-3 py-1.5 text-xs font-bold text-indigo-400 bg-indigo-500/10 hover:bg-indigo-500/15 border border-indigo-500/20 rounded-lg cursor-pointer transition-all disabled:opacity-50"
                            title="Activate dataset"
                          >
                            <Play className="w-3 h-3 fill-indigo-400" />
                            <span>Activate</span>
                          </button>
                        )}
                        {ds.is_active && (
                          <span className="px-3 py-1.5 text-[10px] font-black text-indigo-400 font-mono uppercase tracking-widest bg-indigo-500/5 border border-indigo-500/10 rounded-lg select-none">
                            ✓ Active
                          </span>
                        )}
                        {/* Info / Diagnostics */}
                        <button
                          onClick={() => handleViewSummary(ds)}
                          className="p-1.5 bg-slate-900 hover:bg-slate-850 border border-slate-800 text-slate-400 hover:text-slate-200 rounded-lg cursor-pointer transition-all"
                          title="View summary / diagnostic info"
                        >
                          <Eye className="w-3.5 h-3.5" />
                        </button>
                        {/* Delete / Archive */}
                        {ds.status !== "Archived" && !ds.is_active && (
                          <button
                            onClick={() => handleDelete(ds)}
                            disabled={actionLoading}
                            className="p-1.5 bg-red-500/10 hover:bg-red-500/15 border border-red-500/20 text-red-400 rounded-lg cursor-pointer transition-all disabled:opacity-50"
                            title="Soft delete / archive dataset"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
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

      {/* ── UPLOAD MODAL ───────────────────────────────────────────────────── */}
      {uploadOpen && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl w-full max-w-lg p-6 space-y-6 shadow-2xl relative animate-zoom-in">
            <button
              onClick={() => setUploadOpen(false)}
              className="absolute top-4 right-4 p-1.5 text-slate-400 hover:text-slate-200 rounded-full hover:bg-slate-800 cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>

            <div>
              <h3 className="text-lg font-black text-slate-100 uppercase tracking-tight flex items-center gap-2">
                <Upload className="w-5 h-5 text-indigo-400" />
                <span>Import Dataset spreadsheet</span>
              </h3>
              <p className="text-xs text-slate-500 mt-1">
                Upload a CSV or Excel (.xlsx) file containing crime, criminal, and victim columns.
              </p>
            </div>

            <form onSubmit={handleUploadSubmit} className="space-y-4">
              <div className="flex flex-col gap-1.5">
                <label className="text-[10px] font-bold text-slate-450 uppercase tracking-wider">
                  Dataset Display Name *
                </label>
                <input
                  type="text"
                  required
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                  placeholder="e.g. Bangalore North Q2 2026"
                  className="bg-slate-950 border border-slate-850 text-slate-200 text-xs rounded-xl px-4 py-3 outline-none focus:border-indigo-500 transition-all"
                />
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="text-[10px] font-bold text-slate-450 uppercase tracking-wider">
                  Description / Notes
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="e.g. Seeded patrol incidents compiled by administrative station head"
                  rows={3}
                  className="bg-slate-950 border border-slate-850 text-slate-200 text-xs rounded-xl px-4 py-3 outline-none focus:border-indigo-500 transition-all resize-none"
                />
              </div>

              {/* Drag Drop File Input */}
              <div className="flex flex-col gap-1.5">
                <label className="text-[10px] font-bold text-slate-450 uppercase tracking-wider">
                  Upload spreadsheet file *
                </label>
                <div className="border-2 border-dashed border-slate-800 hover:border-indigo-500/40 rounded-2xl p-6 text-center cursor-pointer transition-all relative group bg-slate-950/30">
                  <input
                    type="file"
                    required
                    accept=".csv,.xlsx,.xls"
                    onChange={handleFileChange}
                    className="absolute inset-0 opacity-0 cursor-pointer"
                  />
                  <div className="space-y-2">
                    <FileSpreadsheet className="w-10 h-10 text-slate-600 group-hover:text-indigo-400 mx-auto transition-all" />
                    {selectedFile ? (
                      <div>
                        <p className="text-xs font-bold text-slate-300">{selectedFile.name}</p>
                        <p className="text-[10px] text-slate-500 font-mono mt-1">{formatBytes(selectedFile.size)}</p>
                      </div>
                    ) : (
                      <div>
                        <p className="text-xs text-slate-350">Click to browse or drag file here</p>
                        <p className="text-[10px] text-slate-600 font-mono mt-1">Accepts CSV, XLSX, or XLS formats</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {isValidated && previewSummary && (
                <div className="space-y-4 bg-slate-955/60 p-4 rounded-2xl border border-slate-800">
                  <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest border-b border-slate-850 pb-1.5">
                    Validation Results ({previewSchemaType === "fir_normalized" ? "FIR Schema" : "Legacy Schema"})
                  </h4>
                  <div className="grid grid-cols-3 gap-2 text-center text-xs">
                    <div className="bg-slate-900/60 p-2 border border-slate-850 rounded-xl">
                      <p className="text-[8px] font-bold text-slate-500 uppercase tracking-wider font-mono">Total Rows</p>
                      <p className="font-bold text-slate-200 mt-0.5 font-mono">{previewSummary.total_rows}</p>
                    </div>
                    <div className="bg-slate-900/60 p-2 border border-slate-850 rounded-xl">
                      <p className="text-[8px] font-bold text-slate-500 uppercase tracking-wider font-mono">Valid</p>
                      <p className="font-bold text-emerald-400 mt-0.5 font-mono">{previewSummary.valid_count}</p>
                    </div>
                    <div className="bg-slate-900/60 p-2 border border-slate-850 rounded-xl">
                      <p className="text-[8px] font-bold text-slate-500 uppercase tracking-wider font-mono">Errors</p>
                      <p className="font-bold text-red-400 mt-0.5 font-mono">{previewSummary.invalid_count}</p>
                    </div>
                  </div>
                  {previewSummary.invalid_count > 0 && (
                    <div className="space-y-1">
                      <p className="text-[9px] font-bold text-red-450 uppercase tracking-wider">Errors (First 5)</p>
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

              <div className="pt-4 border-t border-slate-850 flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => {
                    setUploadOpen(false);
                    setDisplayName("");
                    setDescription("");
                    setSelectedFile(null);
                    setPreviewSummary(null);
                    setPreviewSchemaType(null);
                    setIsValidated(false);
                  }}
                  className="px-5 py-2.5 bg-slate-950 hover:bg-slate-850 text-slate-400 hover:text-slate-205 rounded-xl text-xs font-bold cursor-pointer"
                >
                  Cancel
                </button>
                {selectedFile && !isValidated && (
                  <button
                    type="button"
                    onClick={handleValidatePreview}
                    disabled={actionLoading}
                    className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold cursor-pointer transition-all disabled:opacity-50"
                  >
                    {actionLoading ? "Validating..." : "Validate & Preview"}
                  </button>
                )}
                {isValidated && (
                  <button
                    type="submit"
                    disabled={actionLoading || previewSummary?.valid_count === 0}
                    className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold cursor-pointer transition-all disabled:opacity-50"
                  >
                    {actionLoading ? "Processing Import..." : "Commit Import"}
                  </button>
                )}
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ── DETAILS & DIAGNOSTICS SIDEBAR/MODAL ──────────────────────────────── */}
      {selectedDataset && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-end">
          <div className="bg-slate-900 border-l border-slate-800 h-full w-full max-w-lg p-6 space-y-6 shadow-2xl overflow-y-auto animate-slide-in-right flex flex-col justify-between">
            <div className="space-y-6">
              <div className="flex items-center justify-between border-b border-slate-850 pb-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 rounded-xl">
                    <Info className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-base font-black text-slate-100 uppercase tracking-tight">
                      Dataset Properties
                    </h3>
                    <p className="text-[10px] text-slate-500 font-mono">
                      ID: {selectedDataset.id} • Status: {selectedDataset.status}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedDataset(null)}
                  className="p-1.5 text-slate-400 hover:text-slate-200 rounded-full hover:bg-slate-800 cursor-pointer"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Basic metadata */}
              <div className="space-y-3 bg-slate-950/30 p-4 border border-slate-850 rounded-2xl">
                <div className="grid grid-cols-2 gap-4 text-xs font-mono">
                  <div>
                    <span className="text-slate-650 block uppercase tracking-wider text-[9px] font-bold">Display Name</span>
                    <span className="text-slate-300 font-bold">{selectedDataset.display_name}</span>
                  </div>
                  <div>
                    <span className="text-slate-650 block uppercase tracking-wider text-[9px] font-bold">Original File</span>
                    <span className="text-slate-300 text-[11px] truncate block" title={selectedDataset.original_filename}>
                      {selectedDataset.original_filename}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-650 block uppercase tracking-wider text-[9px] font-bold">Registry Name</span>
                    <span className="text-slate-350">{selectedDataset.name}</span>
                  </div>
                  <div>
                    <span className="text-slate-650 block uppercase tracking-wider text-[9px] font-bold">Format Type</span>
                    <span className="text-slate-350">{selectedDataset.source_type}</span>
                  </div>
                </div>
                <div className="text-xs border-t border-slate-900 pt-3">
                  <span className="text-slate-650 block uppercase tracking-wider text-[9px] font-bold mb-1">Description</span>
                  <p className="text-slate-400 italic leading-relaxed text-[11px]">
                    {selectedDataset.description || "No description / notes recorded for this dataset."}
                  </p>
                </div>
              </div>

              {/* Import Statistics & Diagnostics */}
              {selectedDataset.import_summary && (() => {
                try {
                  const summary = JSON.parse(selectedDataset.import_summary);
                  
                  return (
                    <div className="space-y-4">
                      <h4 className="text-xs font-black text-slate-300 uppercase tracking-widest border-b border-slate-850 pb-2">
                        Import Statistics
                      </h4>
                      
                      {/* Grid metrics */}
                      <div className="grid grid-cols-3 gap-3 text-center">
                        <div className="bg-slate-950/50 p-3.5 border border-slate-850 rounded-2xl">
                          <p className="text-[9px] font-bold text-slate-500 uppercase tracking-wider">Spreadsheet Rows</p>
                          <p className="text-xl font-black text-slate-300 mt-1 font-mono">{summary.total_rows ?? 0}</p>
                        </div>
                        <div className="bg-slate-950/50 p-3.5 border border-slate-850 rounded-2xl">
                          <p className="text-[9px] font-bold text-slate-500 uppercase tracking-wider">Imported Rows</p>
                          <p className="text-xl font-black text-emerald-400 mt-1 font-mono">{summary.successful_imports ?? 0}</p>
                        </div>
                        <div className="bg-slate-950/50 p-3.5 border border-slate-850 rounded-2xl">
                          <p className="text-[9px] font-bold text-slate-500 uppercase tracking-wider">Validation Errors</p>
                          <p className="text-xl font-black text-red-400 mt-1 font-mono">{summary.failed_imports ?? 0}</p>
                        </div>
                      </div>

                      {/* Error details panel */}
                      {summary.errors && summary.errors.length > 0 && (
                        <div className="space-y-2">
                          <h5 className="text-[10px] font-black text-red-400 uppercase tracking-wider flex items-center gap-1.5">
                            <AlertCircle className="w-3.5 h-3.5" />
                            <span>First Logged Error Detail</span>
                          </h5>
                          <div className="bg-red-500/[0.02] border border-red-500/10 rounded-2xl p-4 space-y-2 text-[11px] leading-relaxed">
                            {summary.errors.map((err: any, i: number) => (
                              <div key={i} className="font-mono text-slate-300">
                                <div><span className="text-red-400 font-black uppercase tracking-wider text-[9px] mr-1.5">[Error]</span>Row {err.row}</div>
                                <div className="text-slate-400 mt-1 bg-slate-950/60 p-2.5 rounded-xl border border-slate-900">{err.error}</div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  );
                } catch (e) {
                  return (
                    <div className="text-xs font-mono text-slate-500 bg-slate-950/30 p-4 border border-slate-850 rounded-2xl">
                      Failed to parse import summary log. Raw: {selectedDataset.import_summary}
                    </div>
                  );
                }
              })()}

              {/* Dynamic Database Statistics for Ready dataset */}
              {selectedDataset.status === "Ready" && (
                <div className="space-y-4">
                  <h4 className="text-xs font-black text-slate-300 uppercase tracking-widest border-b border-slate-850 pb-2">
                    Live Database Summary
                  </h4>
                  {summaryLoading ? (
                    <div className="flex flex-col items-center justify-center py-6 text-slate-500 text-xs font-bold gap-2 font-mono">
                      <RefreshCw className="w-5 h-5 animate-spin text-indigo-400" />
                      <span>Retrieving summary metrics...</span>
                    </div>
                  ) : summaryData ? (
                    <div className="space-y-4">
                      {/* Metric cards */}
                      <div className="grid grid-cols-2 gap-4">
                        <div className="bg-slate-950/30 p-4 border border-slate-850 rounded-2xl flex items-center gap-3">
                          <div className="p-2.5 bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 rounded-xl">
                            <Layers className="w-4 h-4" />
                          </div>
                          <div>
                            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Crimes</span>
                            <span className="text-base font-black text-slate-200 font-mono">{summaryData.total_crimes.toLocaleString()}</span>
                          </div>
                        </div>

                        <div className="bg-slate-950/30 p-4 border border-slate-850 rounded-2xl flex items-center gap-3">
                          <div className="p-2.5 bg-violet-500/10 border border-violet-500/20 text-violet-400 rounded-xl">
                            <Users className="w-4 h-4" />
                          </div>
                          <div>
                            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Criminals</span>
                            <span className="text-base font-black text-slate-200 font-mono">{summaryData.criminals.toLocaleString()}</span>
                          </div>
                        </div>
                      </div>

                      {/* Districts and Dates */}
                      <div className="bg-slate-950/30 border border-slate-850 rounded-2xl p-4 space-y-3 font-mono text-[11px] text-slate-300 leading-relaxed">
                        <div className="flex justify-between items-start">
                          <span className="text-slate-500 uppercase text-[9px] font-bold flex items-center gap-1"><Calendar className="w-3 h-3 text-slate-600" /> Date Coverage</span>
                          <span className="text-right">
                            {summaryData.date_range.min ? new Date(summaryData.date_range.min).toLocaleDateString("en-IN") : "-"}
                            {" → "}
                            {summaryData.date_range.max ? new Date(summaryData.date_range.max).toLocaleDateString("en-IN") : "-"}
                          </span>
                        </div>
                        <div className="border-t border-slate-900 pt-3">
                          <span className="text-slate-500 uppercase text-[9px] font-bold block mb-1.5 flex items-center gap-1">
                            <MapPin className="w-3 h-3 text-slate-600" /> Districts ({summaryData.districts.length})
                          </span>
                          {summaryData.districts.length > 0 ? (
                            <div className="flex flex-wrap gap-1.5">
                              {summaryData.districts.map((d, idx) => (
                                <span key={idx} className="bg-slate-900 border border-slate-850 px-2 py-0.5 rounded text-[10px] font-semibold text-slate-400">
                                  {d}
                                </span>
                              ))}
                            </div>
                          ) : (
                            <span className="text-slate-600 italic">No district mapping records found.</span>
                          )}
                        </div>
                      </div>
                    </div>
                  ) : null}
                </div>
              )}
            </div>

            <div className="pt-4 border-t border-slate-850 flex justify-end">
              <button
                onClick={() => setSelectedDataset(null)}
                className="px-5 py-2 bg-slate-950 hover:bg-slate-850 border border-slate-850 text-slate-400 hover:text-slate-200 rounded-xl text-xs font-bold cursor-pointer"
              >
                Close properties
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
