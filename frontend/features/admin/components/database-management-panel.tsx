"use client";

import React, { useState, useEffect, useRef } from "react";
import {
  Database,
  Search,
  Plus,
  Trash2,
  Edit,
  Download,
  Upload,
  AlertTriangle,
  CheckCircle,
  RefreshCw,
  FileText,
  FileSpreadsheet,
  ChevronLeft,
  ChevronRight,
  HelpCircle,
  X,
  Layers,
} from "lucide-react";
import {
  fetchDatabaseStats,
  fetchTableRecords,
  createRecord,
  updateRecord,
  deleteRecord,
  bulkUpload,
  exportTable,
  DatabaseStats,
  BulkUploadSummary,
} from "@/features/admin/services/database-service";
import DatasetRegistryManager from "./dataset-registry-manager";

const TABLES = [
  { id: "crime_events", name: "📂 Crime Events", desc: "Incident history, categories, and severity" },
  { id: "criminals", name: "👤 Criminals", desc: "Offender directory, gender, and risk scores" },
  { id: "victims", name: "❤️ Victims", desc: "Victim registry linked to incidents" },
  { id: "locations", name: "📍 Locations", desc: "Geospatial coordinate mapping & districts" },
  { id: "police_stations", name: "🏢 Police Stations", desc: "Police stations, personnel, and beat sectors" },
];

const TABLE_COLUMNS: Record<string, { key: string; label: string; type: string }[]> = {
  crime_events: [
    { key: "id", label: "ID", type: "number" },
    { key: "crime_type", label: "Crime Type", type: "string" },
    { key: "crime_category", label: "Category", type: "string" },
    { key: "crime_subcategory", label: "Subcategory", type: "string" },
    { key: "severity", label: "Severity", type: "float" },
    { key: "status", label: "Status", type: "string" },
    { key: "crime_date", label: "Date", type: "date" },
    { key: "crime_time", label: "Time", type: "time" },
    { key: "location_id", label: "Loc ID", type: "number" },
    { key: "police_station_id", label: "Station ID", type: "number" },
    { key: "victim_count", label: "Victims", type: "number" },
    { key: "accused_count", label: "Accused", type: "number" },
  ],
  criminals: [
    { key: "id", label: "ID", type: "number" },
    { key: "name", label: "Name", type: "string" },
    { key: "gender", label: "Gender", type: "string" },
    { key: "age", label: "Age", type: "float" },
    { key: "occupation", label: "Occupation", type: "string" },
    { key: "caste", label: "Caste", type: "string" },
    { key: "risk_score", label: "Risk Score", type: "float" },
    { key: "status", label: "Status", type: "string" },
  ],
  victims: [
    { key: "id", label: "ID", type: "number" },
    { key: "crime_event_id", label: "Crime Event ID", type: "number" },
    { key: "gender", label: "Gender", type: "string" },
    { key: "age", label: "Age", type: "float" },
    { key: "occupation", label: "Occupation", type: "string" },
    { key: "location_id", label: "Loc ID", type: "number" },
  ],
  locations: [
    { key: "id", label: "ID", type: "number" },
    { key: "state", label: "State", type: "string" },
    { key: "district", label: "District", type: "string" },
    { key: "latitude", label: "Latitude", type: "float" },
    { key: "longitude", label: "Longitude", type: "float" },
  ],
  police_stations: [
    { key: "id", label: "ID", type: "number" },
    { key: "station_name", label: "Station Name", type: "string" },
    { key: "district", label: "District", type: "string" },
    { key: "beat", label: "Beat", type: "string" },
    { key: "location_id", label: "Loc ID", type: "number" },
    { key: "officer_count", label: "Officers", type: "number" },
    { key: "vehicle_count", label: "Vehicles", type: "number" },
    { key: "equipment_count", label: "Equipment", type: "number" },
    { key: "capacity", label: "Capacity", type: "number" },
    { key: "availability", label: "Availability", type: "string" },
  ]
};

const TABLE_FORM_FIELDS: Record<string, { name: string; label: string; type: "text" | "number" | "select" | "date" | "time"; required: boolean; options?: string[] }[]> = {
  crime_events: [
    { name: "crime_type", label: "Crime Type", type: "text", required: true },
    { name: "crime_category", label: "Crime Category", type: "text", required: true },
    { name: "crime_subcategory", label: "Crime Subcategory", type: "text", required: false },
    { name: "description", label: "Description", type: "text", required: false },
    { name: "severity", label: "Severity Score (e.g. 1.0)", type: "number", required: true },
    { name: "status", label: "Status", type: "select", required: true, options: ["reported", "investigating", "resolved", "cold"] },
    { name: "crime_date", label: "Crime Date", type: "date", required: true },
    { name: "crime_time", label: "Crime Time", type: "time", required: false },
    { name: "location_id", label: "Location ID", type: "number", required: false },
    { name: "police_station_id", label: "Police Station ID", type: "number", required: false },
    { name: "victim_count", label: "Victim Count", type: "number", required: true },
    { name: "accused_count", label: "Accused Count", type: "number", required: true },
  ],
  criminals: [
    { name: "name", label: "Criminal Name", type: "text", required: true },
    { name: "gender", label: "Gender", type: "select", required: false, options: ["Male", "Female", "Other"] },
    { name: "age", label: "Age", type: "number", required: false },
    { name: "occupation", label: "Occupation", type: "text", required: false },
    { name: "caste", label: "Caste", type: "text", required: false },
    { name: "risk_score", label: "Risk Score (0.0 to 1.0)", type: "number", required: true },
    { name: "status", label: "Status", type: "select", required: true, options: ["accused", "suspect", "arrested", "convicted", "acquitted", "wanted"] },
  ],
  victims: [
    { name: "crime_event_id", label: "Crime Event ID (Required)", type: "number", required: true },
    { name: "gender", label: "Gender", type: "select", required: false, options: ["Male", "Female", "Other"] },
    { name: "age", label: "Age", type: "number", required: false },
    { name: "occupation", label: "Occupation", type: "text", required: false },
    { name: "location_id", label: "Location ID", type: "number", required: false },
  ],
  locations: [
    { name: "state", label: "State", type: "text", required: true },
    { name: "district", label: "District", type: "text", required: true },
    { name: "latitude", label: "Latitude", type: "number", required: false },
    { name: "longitude", label: "Longitude", type: "number", required: false },
  ],
  police_stations: [
    { name: "station_name", label: "Station Name", type: "text", required: true },
    { name: "district", label: "District", type: "text", required: true },
    { name: "beat", label: "Beat / Sector", type: "text", required: false },
    { name: "location_id", label: "Location ID", type: "number", required: false },
    { name: "officer_count", label: "Officer Count", type: "number", required: true },
    { name: "vehicle_count", label: "Vehicle Count", type: "number", required: true },
    { name: "equipment_count", label: "Equipment Count", type: "number", required: true },
    { name: "capacity", label: "Station Capacity", type: "number", required: true },
    { name: "availability", label: "Availability Status", type: "select", required: true, options: ["available", "busy", "offline"] },
  ]
};

type ViewMode = "dashboard" | "datasets" | "records" | "form" | "bulk" | "export";

export default function DatabaseManagementPanel() {
  const [activeTable, setActiveTable] = useState<string>("crime_events");
  const [viewMode, setViewMode] = useState<ViewMode>("dashboard");

  // API states
  const [stats, setStats] = useState<DatabaseStats | null>(null);
  const [records, setRecords] = useState<any[]>([]);
  const [totalRecords, setTotalRecords] = useState<number>(0);
  const [page, setPage] = useState<number>(1);
  const [pageSize] = useState<number>(10);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [sortBy, setSortBy] = useState<string>("id");
  const [sortOrder, setSortOrder] = useState<string>("desc");
  const [filters, setFilters] = useState<Record<string, any>>({});

  // Loading & notification states
  const [loading, setLoading] = useState<boolean>(false);
  const [actionLoading, setActionLoading] = useState<boolean>(false);
  const [notification, setNotification] = useState<{ type: "success" | "error"; message: string } | null>(null);

  // Form states
  const [editingId, setEditingId] = useState<number | null>(null);
  const [formData, setFormData] = useState<Record<string, any>>({});
  const [formValidationErrors, setFormValidationErrors] = useState<Record<string, string>>({});

  // Bulk upload states
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [bulkSummary, setBulkSummary] = useState<BulkUploadSummary | null>(null);
  const [bulkIsValidated, setBulkIsValidated] = useState<boolean>(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Export states
  const [exportFormat, setExportFormat] = useState<"csv" | "excel">("csv");

  // Load Dashboard Stats
  const loadStats = async () => {
    setLoading(true);
    try {
      const data = await fetchDatabaseStats();
      setStats(data);
    } catch (e: any) {
      showNotification("error", e.response?.data?.detail || "Failed to load database statistics.");
    } finally {
      setLoading(false);
    }
  };

  // Load Table Records
  const loadRecords = async (targetPage = page, q = searchQuery, order = sortOrder, field = sortBy, colFilters = filters) => {
    setLoading(true);
    try {
      const response = await fetchTableRecords(
        activeTable,
        targetPage,
        pageSize,
        q,
        field,
        order,
        colFilters
      );
      setRecords(response.records);
      setTotalRecords(response.total);
    } catch (e: any) {
      showNotification("error", e.response?.data?.detail || "Failed to retrieve records.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStats();
  }, []);

  // Reload records when table changes or view changes to explorer
  useEffect(() => {
    if (viewMode === "records") {
      setPage(1);
      setSearchQuery("");
      setFilters({});
      loadRecords(1, "", "desc", "id", {});
    } else if (viewMode === "dashboard") {
      loadStats();
    }
    // Reset notification & form on view toggle
    setNotification(null);
    setEditingId(null);
    setFormData({});
    setFormValidationErrors({});
    setUploadFile(null);
    setBulkSummary(null);
    setBulkIsValidated(false);
  }, [activeTable, viewMode]);

  // Utility to push notifications
  const showNotification = (type: "success" | "error", message: string) => {
    setNotification({ type, message });
    setTimeout(() => {
      setNotification((curr) => (curr?.message === message ? null : curr));
    }, 6000);
  };

  // Search input handler
  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    loadRecords(1, searchQuery, sortOrder, sortBy, filters);
  };

  // Grid delete handler
  const handleDelete = async (id: number) => {
    if (!confirm(`Are you sure you want to delete record ID ${id} from ${activeTable}?`)) {
      return;
    }
    setActionLoading(true);
    try {
      await deleteRecord(activeTable, id);
      showNotification("success", `Successfully deleted record ID ${id}.`);
      loadRecords(page, searchQuery, sortOrder, sortBy, filters);
      loadStats();
    } catch (e: any) {
      showNotification("error", e.response?.data?.detail || "Failed to delete record. It may be linked as a foreign key in another table.");
    } finally {
      setActionLoading(false);
    }
  };

  // Edit click handler
  const handleEditClick = (record: any) => {
    setEditingId(record.id);
    // Populate form data
    const fields = TABLE_FORM_FIELDS[activeTable];
    const initialData: Record<string, any> = {};
    fields.forEach((f) => {
      initialData[f.name] = record[f.name] ?? "";
    });
    setFormData(initialData);
    setFormValidationErrors({});
    setViewMode("form");
  };

  // Handle input changes inside Form
  const handleFormChange = (fieldName: string, value: any) => {
    setFormData((prev) => ({ ...prev, [fieldName]: value }));
    if (formValidationErrors[fieldName]) {
      setFormValidationErrors((prev) => {
        const copy = { ...prev };
        delete copy[fieldName];
        return copy;
      });
    }
  };

  // Form Submit (Create or Update)
  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Client-side validations
    const fields = TABLE_FORM_FIELDS[activeTable];
    const errors: Record<string, string> = {};
    fields.forEach((f) => {
      const val = formData[f.name];
      if (f.required && (val === undefined || val === null || String(val).trim() === "")) {
        errors[f.name] = `${f.label} is required.`;
      }
      // Basic type checking
      if (val !== undefined && val !== null && String(val).trim() !== "") {
        if (f.type === "number" && isNaN(Number(val))) {
          errors[f.name] = `${f.label} must be a valid number.`;
        }
      }
    });

    if (Object.keys(errors).length > 0) {
      setFormValidationErrors(errors);
      showNotification("error", "Please fix form validation errors.");
      return;
    }

    setActionLoading(true);
    try {
      if (editingId) {
        await updateRecord(activeTable, editingId, formData);
        showNotification("success", `Successfully updated record ID ${editingId}.`);
      } else {
        const newRecord = await createRecord(activeTable, formData);
        showNotification("success", `Successfully created new record with ID ${newRecord.id}.`);
      }
      setViewMode("records");
    } catch (e: any) {
      showNotification("error", e.response?.data?.detail || "Failed to save record. Validate all fields and key relations.");
    } finally {
      setActionLoading(false);
    }
  };

  // Bulk upload file select
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setUploadFile(e.target.files[0]);
      setBulkSummary(null);
      setBulkIsValidated(false);
    }
  };

  // Bulk preview validation
  const handleBulkValidate = async () => {
    if (!uploadFile) return;
    setActionLoading(true);
    setNotification(null);
    try {
      const summary = await bulkUpload(activeTable, uploadFile, true);
      setBulkSummary(summary);
      setBulkIsValidated(true);
      showNotification("success", `File validated: ${summary.valid_count} valid rows, ${summary.invalid_count} row errors found.`);
    } catch (e: any) {
      showNotification("error", e.response?.data?.detail || "Validation failed. Verify file format and column headers.");
    } finally {
      setActionLoading(false);
    }
  };

  // Bulk import commit
  const handleBulkImport = async () => {
    if (!uploadFile) return;
    setActionLoading(true);
    try {
      const summary = await bulkUpload(activeTable, uploadFile, false);
      showNotification("success", `Import complete. Successfully imported ${summary.valid_count} records. Skipped ${summary.invalid_count} invalid rows.`);
      setViewMode("records");
      loadStats();
    } catch (e: any) {
      showNotification("error", e.response?.data?.detail || "Bulk import failed during database writing.");
    } finally {
      setActionLoading(false);
    }
  };

  // Export handler
  const handleExport = async () => {
    setLoading(true);
    try {
      const blob = await exportTable(activeTable, exportFormat, filters);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute(
        "download",
        `export_${activeTable}_${new Date().toISOString().slice(0, 10)}.${
          exportFormat === "excel" ? "xlsx" : "csv"
        }`
      );
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
      showNotification("success", `Successfully exported data as ${exportFormat.toUpperCase()}.`);
    } catch (e: any) {
      showNotification("error", e.response?.data?.detail || "Data export failed.");
    } finally {
      setLoading(false);
    }
  };

  // Change sort order
  const handleSort = (field: string) => {
    const isAsc = sortBy === field && sortOrder === "asc";
    const order = isAsc ? "desc" : "asc";
    setSortBy(field);
    setSortOrder(order);
    loadRecords(page, searchQuery, order, field, filters);
  };

  // Column filter change
  const handleFilterChange = (field: string, value: any) => {
    const updatedFilters = { ...filters, [field]: value };
    if (value === "") {
      delete updatedFilters[field];
    }
    setFilters(updatedFilters);
    setPage(1);
    loadRecords(1, searchQuery, sortOrder, sortBy, updatedFilters);
  };

  return (
    <div className="space-y-6">
      {/* ── 1. Top Bar / Table & View Selector ───────────────────────────────── */}
      <div className="flex flex-col xl:flex-row gap-4 items-start xl:items-center justify-between bg-slate-950/45 p-4 rounded-3xl border border-slate-900/60 backdrop-blur-md">
        <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center w-full xl:w-auto">
          <div>
            <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-1">
              Select Database Table
            </label>
            <select
              value={activeTable}
              onChange={(e) => setActiveTable(e.target.value)}
              className="bg-slate-900 border border-slate-800 text-slate-200 text-sm font-semibold rounded-2xl px-4 py-2.5 outline-none focus:border-indigo-500 transition-all cursor-pointer min-w-[200px]"
            >
              {TABLES.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name.split(" ")[1]}
                </option>
              ))}
            </select>
          </div>
          <div className="text-slate-400 text-xs mt-1 sm:mt-5">
            {TABLES.find((t) => t.id === activeTable)?.desc}
          </div>
        </div>

        {/* View Mode Buttons */}
        <div className="flex flex-wrap gap-1 bg-slate-900/60 p-1 border border-slate-800/80 rounded-2xl w-full xl:w-auto justify-center">
          {(
            [
              { id: "dashboard", label: "Dashboard", icon: Database },
              { id: "datasets", label: "Dataset Manager", icon: Layers },
              { id: "records", label: "Explorer", icon: Search },
              { id: "form", label: editingId ? "Edit Record" : "Add Record", icon: Plus },
              { id: "bulk", label: "Bulk Import", icon: Upload },
              { id: "export", label: "Export", icon: Download },
            ] as const
          ).map((item) => (
            <button
              key={item.id}
              onClick={() => setViewMode(item.id)}
              className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                viewMode === item.id
                  ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/10"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/40"
              }`}
            >
              <item.icon className="w-3.5 h-3.5" />
              <span>{item.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* ── 2. Notification Toast ────────────────────────────────────────────── */}
      {notification && (
        <div
          className={`p-4 rounded-2xl border text-xs flex gap-3 items-center animate-slide-in-right ${
            notification.type === "success"
              ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-400"
              : "bg-red-500/10 border-red-500/20 text-red-400"
          }`}
        >
          {notification.type === "success" ? (
            <CheckCircle className="w-4 h-4 shrink-0" />
          ) : (
            <AlertTriangle className="w-4 h-4 shrink-0" />
          )}
          <span>{notification.message}</span>
        </div>
      )}

      {/* ── 3. Panel Main Views ──────────────────────────────────────────────── */}
      <div className="min-h-[450px]">
        {/* === VIEW: DASHBOARD === */}
        {viewMode === "dashboard" && (
          <div className="space-y-6">
            {/* Quick Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Card: Total Records */}
              <div className="bg-slate-950/40 border border-slate-900 rounded-3xl p-6 backdrop-blur-md flex flex-col justify-between">
                <div>
                  <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">
                    Active Table Records
                  </p>
                  <h3 className="text-4xl font-black text-indigo-400 font-mono mt-2">
                    {loading ? (
                      <span className="w-16 h-8 bg-slate-800 rounded animate-pulse inline-block" />
                    ) : (
                      (stats?.counts[activeTable] ?? 0).toLocaleString()
                    )}
                  </h3>
                </div>
                <p className="text-[10px] text-slate-600 mt-4 uppercase font-bold tracking-wider">
                  Table: {activeTable.replace("_", " ")}
                </p>
              </div>

              {/* Card: Database Health */}
              <div className="bg-slate-950/40 border border-slate-900 rounded-3xl p-6 backdrop-blur-md flex flex-col justify-between">
                <div>
                  <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">
                    Database Health
                  </p>
                  <div className="flex items-center gap-2 mt-3">
                    <span
                      className={`w-2.5 h-2.5 rounded-full ${
                        stats?.health === "healthy" ? "bg-emerald-500 animate-pulse" : "bg-red-500"
                      }`}
                    />
                    <span className="text-xl font-bold uppercase tracking-wider text-slate-200">
                      {loading ? "Checking..." : stats?.health || "Unknown"}
                    </span>
                  </div>
                </div>
                <p className="text-[10px] text-slate-600 mt-4 uppercase font-bold tracking-wider">
                  Connection: SQLite Operational
                </p>
              </div>

              {/* Card: Last Update */}
              <div className="bg-slate-950/40 border border-slate-900 rounded-3xl p-6 backdrop-blur-md flex flex-col justify-between">
                <div>
                  <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">
                    Last Table Update
                  </p>
                  <p className="text-sm font-semibold text-slate-300 font-mono mt-3">
                    {loading ? (
                      "Loading..."
                    ) : stats?.last_updated[activeTable] ? (
                      new Date(stats.last_updated[activeTable]!).toLocaleString("en-IN")
                    ) : (
                      "No updates recorded"
                    )}
                  </p>
                </div>
                <p className="text-[10px] text-slate-600 mt-4 uppercase font-bold tracking-wider">
                  Auto-Audited Timestamp
                </p>
              </div>
            </div>

            {/* Table distributions */}
            <div className="bg-slate-950/45 p-6 border border-slate-900 rounded-3xl backdrop-blur-md">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-black text-slate-300 uppercase tracking-wider">
                  Database Distribution Stats
                </h3>
                <button
                  onClick={loadStats}
                  className="p-2 bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-400 rounded-xl transition-all"
                  title="Reload Stats"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
                </button>
              </div>
              <div className="space-y-4">
                {TABLES.map((t) => {
                  const count = stats?.counts[t.id] ?? 0;
                  const maxCount = Math.max(...Object.values(stats?.counts ?? {}), 1);
                  const percentage = Math.round((count / maxCount) * 100);
                  return (
                    <div key={t.id} className="space-y-1">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-semibold text-slate-400">
                          {t.name.split(" ")[1]}
                        </span>
                        <span className="font-mono font-bold text-slate-300">
                          {count.toLocaleString()} records
                        </span>
                      </div>
                      <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden">
                        <div
                          className="bg-indigo-500/70 h-2 rounded-full transition-all duration-500"
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* === VIEW: RECORDS === */}
        {viewMode === "records" && (
          <div className="space-y-4">
            {/* Search, Filter inputs */}
            <form
              onSubmit={handleSearchSubmit}
              className="flex flex-col md:flex-row gap-3 bg-slate-950/40 p-4 border border-slate-900 rounded-2xl backdrop-blur-md"
            >
              <div className="flex-1 relative">
                <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="Search by ID or keywords..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800/80 pl-10 pr-4 py-2.5 rounded-xl text-xs text-slate-300 outline-none focus:border-indigo-500 transition-all placeholder:text-slate-600"
                />
              </div>
              
              {/* Dynamic Column Filters (Quick Selector for Status if it exists) */}
              {TABLE_FORM_FIELDS[activeTable].some(f => f.name === "status") && (
                <div className="w-full md:w-48">
                  <select
                    value={filters.status ?? ""}
                    onChange={(e) => handleFilterChange("status", e.target.value)}
                    className="w-full bg-slate-900 border border-slate-800/80 text-slate-400 text-xs rounded-xl px-3 py-2.5 outline-none focus:border-indigo-500 cursor-pointer"
                  >
                    <option value="">All Statuses</option>
                    {TABLE_FORM_FIELDS[activeTable]
                      .find(f => f.name === "status")
                      ?.options?.map((opt) => (
                        <option key={opt} value={opt}>
                          {opt}
                        </option>
                      ))}
                  </select>
                </div>
              )}

              <button
                type="submit"
                className="bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold px-6 py-2.5 rounded-xl transition-all cursor-pointer shadow-md"
              >
                Search
              </button>
            </form>

            {/* Grid Table */}
            <div className="bg-slate-950/40 border border-slate-900 rounded-2xl overflow-hidden backdrop-blur-md">
              <div className="overflow-x-auto">
                <table className="w-full text-xs text-left">
                  <thead>
                    <tr className="border-b border-slate-900 bg-slate-900/30">
                      {TABLE_COLUMNS[activeTable].map((col) => (
                        <th
                          key={col.key}
                          onClick={() => handleSort(col.key)}
                          className="px-4 py-3 text-[10px] font-bold text-slate-500 uppercase tracking-wider cursor-pointer hover:text-slate-300 transition-colors select-none"
                        >
                          <div className="flex items-center gap-1.5">
                            <span>{col.label}</span>
                            {sortBy === col.key && (
                              <span className="text-indigo-400">
                                {sortOrder === "asc" ? "▲" : "▼"}
                              </span>
                            )}
                          </div>
                        </th>
                      ))}
                      <th className="px-4 py-3 text-[10px] font-bold text-slate-500 uppercase tracking-wider text-right w-24">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-900/60">
                    {loading ? (
                      [...Array(5)].map((_, idx) => (
                        <tr key={idx}>
                          {TABLE_COLUMNS[activeTable].map((col) => (
                            <td key={col.key} className="px-4 py-3.5">
                              <div className="h-3 bg-slate-900 rounded animate-pulse w-14" />
                            </td>
                          ))}
                          <td className="px-4 py-3.5">
                            <div className="h-3 bg-slate-900 rounded animate-pulse w-full" />
                          </td>
                        </tr>
                      ))
                    ) : records.length === 0 ? (
                      <tr>
                        <td
                          colSpan={TABLE_COLUMNS[activeTable].length + 1}
                          className="text-center py-16 text-slate-600 uppercase tracking-widest"
                        >
                          No records found — Add new or import data.
                        </td>
                      </tr>
                    ) : (
                      records.map((row) => (
                        <tr key={row.id} className="hover:bg-slate-900/30 transition-colors">
                          {TABLE_COLUMNS[activeTable].map((col) => (
                            <td key={col.key} className="px-4 py-3 text-slate-300 font-mono">
                              {row[col.key] !== null && row[col.key] !== undefined
                                ? String(row[col.key])
                                : "-"}
                            </td>
                          ))}
                          <td className="px-4 py-3 text-right flex items-center justify-end gap-1.5">
                            <button
                              onClick={() => handleEditClick(row)}
                              className="p-1.5 hover:bg-indigo-500/10 text-indigo-400 rounded-lg transition-all"
                              title="Edit Record"
                            >
                              <Edit className="w-3.5 h-3.5" />
                            </button>
                            <button
                              onClick={() => handleDelete(row.id)}
                              disabled={actionLoading}
                              className="p-1.5 hover:bg-red-500/10 text-red-400 rounded-lg transition-all disabled:opacity-50"
                              title="Delete Record"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Pagination Controls */}
            {totalRecords > 0 && (
              <div className="flex items-center justify-between text-xs text-slate-500 px-2">
                <div>
                  Showing {(page - 1) * pageSize + 1} to{" "}
                  {Math.min(page * pageSize, totalRecords)} of {totalRecords} records
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => {
                      if (page > 1) {
                        setPage(page - 1);
                        loadRecords(page - 1, searchQuery, sortOrder, sortBy, filters);
                      }
                    }}
                    disabled={page === 1 || loading}
                    className="p-2 border border-slate-800 rounded-xl hover:bg-slate-900 disabled:opacity-30 cursor-pointer"
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => {
                      if (page * pageSize < totalRecords) {
                        setPage(page + 1);
                        loadRecords(page + 1, searchQuery, sortOrder, sortBy, filters);
                      }
                    }}
                    disabled={page * pageSize >= totalRecords || loading}
                    className="p-2 border border-slate-800 rounded-xl hover:bg-slate-900 disabled:opacity-30 cursor-pointer"
                  >
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* === VIEW: ADD/EDIT FORM === */}
        {viewMode === "form" && (
          <div className="bg-slate-950/40 p-6 border border-slate-900 rounded-3xl backdrop-blur-md max-w-2xl mx-auto space-y-6">
            <div className="flex justify-between items-center border-b border-slate-900 pb-4">
              <div>
                <h3 className="text-base font-black text-slate-100 uppercase tracking-tight">
                  {editingId ? `📝 Edit ${activeTable.replace("_", " ")}` : `➕ Add New ${activeTable.replace("_", " ")}`}
                </h3>
                <p className="text-[10px] text-slate-500 mt-1">
                  Ensure references are valid before saving.
                </p>
              </div>
              {editingId && (
                <span className="text-[10px] font-mono px-2 py-1 bg-slate-900 text-indigo-400 rounded-lg">
                  ID: {editingId}
                </span>
              )}
            </div>

            <form onSubmit={handleFormSubmit} className="space-y-4">
              {TABLE_FORM_FIELDS[activeTable].map((f) => (
                <div key={f.name} className="flex flex-col gap-1">
                  <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                    {f.label} {f.required && <span className="text-red-500">*</span>}
                  </label>
                  {f.type === "select" ? (
                    <select
                      value={formData[f.name] ?? ""}
                      onChange={(e) => handleFormChange(f.name, e.target.value)}
                      className="bg-slate-900 border border-slate-850 text-slate-300 text-xs rounded-xl px-4 py-2.5 outline-none focus:border-indigo-500 cursor-pointer"
                    >
                      <option value="">Select status</option>
                      {f.options?.map((opt) => (
                        <option key={opt} value={opt}>
                          {opt}
                        </option>
                      ))}
                    </select>
                  ) : (
                    <input
                      type={f.type}
                      value={formData[f.name] ?? ""}
                      onChange={(e) => handleFormChange(f.name, e.target.value)}
                      className="bg-slate-900 border border-slate-850 text-slate-300 text-xs rounded-xl px-4 py-2.5 outline-none focus:border-indigo-500 placeholder:text-slate-700"
                      placeholder={f.required ? "(Required)" : "(Optional)"}
                    />
                  )}
                  {formValidationErrors[f.name] && (
                    <span className="text-[10px] text-red-500">{formValidationErrors[f.name]}</span>
                  )}
                </div>
              ))}

              <div className="flex gap-3 justify-end pt-4">
                <button
                  type="button"
                  onClick={() => setViewMode("records")}
                  className="px-5 py-2.5 border border-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-900 rounded-xl text-xs font-bold cursor-pointer transition-all"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={actionLoading}
                  className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold cursor-pointer transition-all disabled:opacity-50"
                >
                  {actionLoading ? "Saving..." : "Save Record"}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* === VIEW: BULK UPLOAD === */}
        {viewMode === "bulk" && (
          <div className="max-w-4xl mx-auto space-y-6">
            <div className="bg-slate-950/40 p-6 border border-slate-900 rounded-3xl backdrop-blur-md space-y-6">
              <div>
                <h3 className="text-base font-black text-slate-100 uppercase tracking-tight">
                  📥 Bulk Data Import
                </h3>
                <p className="text-xs text-slate-500 mt-1">
                  Upload CSV or Excel (.xlsx) files to populate the {activeTable.replace("_", " ")} table. Valid rows will be committed; invalid rows are skipped.
                </p>
              </div>

              {/* Drag-drop or File Picker area */}
              <div
                onClick={() => fileInputRef.current?.click()}
                className="border-2 border-dashed border-slate-800 hover:border-indigo-500/50 bg-slate-900/30 hover:bg-slate-900/50 rounded-3xl p-10 text-center cursor-pointer transition-all"
              >
                <Upload className="w-8 h-8 text-indigo-400 mx-auto mb-3" />
                <p className="text-xs font-bold text-slate-350">
                  {uploadFile ? uploadFile.name : "Select a dataset file (CSV or XLSX)"}
                </p>
                <p className="text-[10px] text-slate-500 mt-1">
                  Click here to browse files. Ensure column headers match table fields.
                </p>
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileChange}
                  accept=".csv,.xlsx"
                  className="hidden"
                />
              </div>

              {uploadFile && (
                <div className="flex gap-3 justify-end">
                  <button
                    onClick={() => {
                      setUploadFile(null);
                      setBulkSummary(null);
                      setBulkIsValidated(false);
                    }}
                    className="px-5 py-2.5 border border-slate-800 text-slate-400 rounded-xl text-xs font-bold cursor-pointer"
                  >
                    Clear File
                  </button>
                  <button
                    onClick={handleBulkValidate}
                    disabled={actionLoading}
                    className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold cursor-pointer"
                  >
                    {actionLoading ? "Validating..." : "Validate & Preview"}
                  </button>
                </div>
              )}
            </div>

            {/* Preview Summary */}
            {bulkIsValidated && bulkSummary && (
              <div className="bg-slate-950/40 p-6 border border-slate-900 rounded-3xl backdrop-blur-md space-y-6">
                <h4 className="text-xs font-black text-slate-350 uppercase tracking-widest border-b border-slate-900 pb-2">
                  Validation Results
                </h4>
                
                {/* Metrics */}
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div className="bg-slate-900/60 p-4 border border-slate-850 rounded-2xl">
                    <p className="text-[9px] font-bold text-slate-500 uppercase tracking-wider">Total Rows</p>
                    <p className="text-2xl font-black text-slate-200 mt-1 font-mono">{bulkSummary.total_rows}</p>
                  </div>
                  <div className="bg-slate-900/60 p-4 border border-slate-850 rounded-2xl">
                    <p className="text-[9px] font-bold text-slate-500 uppercase tracking-wider">Valid Importable</p>
                    <p className="text-2xl font-black text-emerald-400 mt-1 font-mono">{bulkSummary.valid_count}</p>
                  </div>
                  <div className="bg-slate-900/60 p-4 border border-slate-850 rounded-2xl">
                    <p className="text-[9px] font-bold text-slate-500 uppercase tracking-wider">Skipped Errors</p>
                    <p className="text-2xl font-black text-red-400 mt-1 font-mono">{bulkSummary.invalid_count}</p>
                  </div>
                </div>

                {/* Import execution button */}
                <div className="flex items-center justify-between bg-indigo-950/20 border border-indigo-900/40 p-4 rounded-2xl text-xs text-indigo-350">
                  <div className="flex gap-2.5 items-center">
                    <CheckCircle className="w-5 h-5 text-indigo-400" />
                    <div>
                      <p className="font-bold">Ready to import valid data.</p>
                      <p className="text-[10px] text-indigo-500">Only the {bulkSummary.valid_count} valid rows will be imported.</p>
                    </div>
                  </div>
                  <button
                    onClick={handleBulkImport}
                    disabled={actionLoading || bulkSummary.valid_count === 0}
                    className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold px-6 py-2.5 rounded-xl cursor-pointer disabled:opacity-40"
                  >
                    Commit Import
                  </button>
                </div>

                {/* Row-Level Errors */}
                {bulkSummary.invalid_count > 0 && (
                  <div className="space-y-2">
                    <h5 className="text-[10px] font-bold text-red-400 uppercase tracking-wider flex items-center gap-1.5">
                      <AlertTriangle className="w-3.5 h-3.5" />
                      <span>Row-Level Errors (First 15)</span>
                    </h5>
                    <div className="bg-slate-900/40 rounded-xl p-3 max-h-48 overflow-y-auto border border-slate-900/80 font-mono text-[10px] text-slate-400 divide-y divide-slate-800">
                      {bulkSummary.errors.slice(0, 15).map((err, i) => (
                        <div key={i} className="py-2 flex flex-col md:flex-row gap-1 justify-between">
                          <div>
                            <span className="text-red-400 font-bold">Row {err.row}</span>:{" "}
                            {Object.entries(err.errors)
                              .map(([k, v]) => `${k} (${v})`)
                              .join(", ")}
                          </div>
                          <div className="text-[9px] text-slate-600">
                            Raw: {JSON.stringify(err.raw_data)}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Preview sample */}
                {bulkSummary.valid_count > 0 && (
                  <div className="space-y-2">
                    <h5 className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                      Valid Data Preview Sample (First 5 Rows)
                    </h5>
                    <div className="border border-slate-900 rounded-xl overflow-hidden">
                      <table className="w-full text-[10px] text-left">
                        <thead className="bg-slate-900/50">
                          <tr>
                            {TABLE_COLUMNS[activeTable]
                              .filter((c) => c.key !== "id")
                              .slice(0, 5)
                              .map((c) => (
                                <th key={c.key} className="px-3 py-2 text-slate-500 font-bold">
                                  {c.label}
                                </th>
                              ))}
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-900/60 bg-slate-950/20">
                          {bulkSummary.preview.slice(0, 5).map((row, index) => (
                            <tr key={index}>
                              {TABLE_COLUMNS[activeTable]
                                .filter((c) => c.key !== "id")
                                .slice(0, 5)
                                .map((c) => (
                                  <td key={c.key} className="px-3 py-2 text-slate-400 font-mono">
                                    {row[c.key] !== null ? String(row[c.key]) : "-"}
                                  </td>
                                ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* === VIEW: DATASETS === */}
        {viewMode === "datasets" && (
          <DatasetRegistryManager onDatasetSwitched={() => { loadStats(); }} />
        )}

        {/* === VIEW: EXPORT === */}
        {viewMode === "export" && (
          <div className="max-w-xl mx-auto bg-slate-950/40 p-6 border border-slate-900 rounded-3xl backdrop-blur-md space-y-6">
            <div>
              <h3 className="text-base font-black text-slate-100 uppercase tracking-tight">
                📤 Export Table Data
              </h3>
              <p className="text-xs text-slate-500 mt-1">
                Configure formatting and download the complete dataset for {activeTable.replace("_", " ")}.
              </p>
            </div>

            {/* Filter review */}
            <div className="space-y-4">
              <div className="flex flex-col gap-1.5">
                <label className="text-[10px] font-bold text-slate-450 uppercase tracking-wider">
                  Select Format
                </label>
                <div className="flex gap-4">
                  <label className="flex items-center gap-2 text-xs text-slate-350 cursor-pointer select-none">
                    <input
                      type="radio"
                      name="format"
                      checked={exportFormat === "csv"}
                      onChange={() => setExportFormat("csv")}
                      className="accent-indigo-500"
                    />
                    <FileText className="w-4 h-4 text-slate-500" />
                    <span>CSV Format (.csv)</span>
                  </label>
                  <label className="flex items-center gap-2 text-xs text-slate-350 cursor-pointer select-none">
                    <input
                      type="radio"
                      name="format"
                      checked={exportFormat === "excel"}
                      onChange={() => setExportFormat("excel")}
                      className="accent-indigo-500"
                    />
                    <FileSpreadsheet className="w-4 h-4 text-indigo-400" />
                    <span>Excel Sheet (.xlsx)</span>
                  </label>
                </div>
              </div>

              {/* Status filtering check for export */}
              {TABLE_FORM_FIELDS[activeTable].some(f => f.name === "status") && (
                <div className="flex flex-col gap-1.5 pt-2">
                  <label className="text-[10px] font-bold text-slate-455 uppercase tracking-wider">
                    Status Filter
                  </label>
                  <select
                    value={filters.status ?? ""}
                    onChange={(e) => handleFilterChange("status", e.target.value)}
                    className="bg-slate-900 border border-slate-850 text-slate-300 text-xs rounded-xl px-4 py-2.5 outline-none cursor-pointer w-full"
                  >
                    <option value="">Export All Statuses</option>
                    {TABLE_FORM_FIELDS[activeTable]
                      .find(f => f.name === "status")
                      ?.options?.map((opt) => (
                        <option key={opt} value={opt}>
                          Only: {opt}
                        </option>
                      ))}
                  </select>
                </div>
              )}

              <div className="pt-6 border-t border-slate-900 flex justify-end">
                <button
                  onClick={handleExport}
                  disabled={loading}
                  className="flex items-center gap-1.5 px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-xl cursor-pointer"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>{loading ? "Generating..." : "Download Export"}</span>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
