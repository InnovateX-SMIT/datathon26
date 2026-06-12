import React, { useState } from "react";
import {
  Search,
  Filter,
  RefreshCw,
  ChevronDown,
  ChevronUp,
  AlertOctagon,
  Network,
  Cpu,
  MapPin,
  Clock,
  User,
  Check,
  X,
  Play,
  RotateCcw
} from "lucide-react";
import type { Alert } from "@/types/alert";

interface AlertListProps {
  alerts: Alert[];
  loading: boolean;
  onUpdateStatus: (id: number, status: string) => Promise<void>;
  onRefresh: () => Promise<void>;
  statusFilter: string;
  setStatusFilter: (status: string) => void;
  severityFilter: string;
  setSeverityFilter: (severity: string) => void;
  sourceFilter: string;
  setSourceFilter: (source: string) => void;
}

export default function AlertList({
  alerts,
  loading,
  onUpdateStatus,
  onRefresh,
  statusFilter,
  setStatusFilter,
  severityFilter,
  setSeverityFilter,
  sourceFilter,
  setSourceFilter
}: AlertListProps) {
  const [expandedAlertId, setExpandedAlertId] = useState<number | null>(null);
  const [searchTerm, setSearchTerm] = useState("");

  const toggleExpand = (id: number) => {
    setExpandedAlertId(expandedAlertId === id ? null : id);
  };

  // Filter local search
  const filteredAlerts = alerts.filter((alert) => {
    const term = searchTerm.toLowerCase();
    return (
      alert.title.toLowerCase().includes(term) ||
      alert.description.toLowerCase().includes(term) ||
      alert.severity.toLowerCase().includes(term) ||
      alert.source.toLowerCase().includes(term)
    );
  });

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case "CRITICAL":
        return (
          <span className="px-2 py-0.5 bg-red-500/10 border border-red-500/30 text-red-400 text-[9px] font-black rounded uppercase tracking-wider animate-pulse flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-red-500" />
            Critical
          </span>
        );
      case "HIGH":
        return (
          <span className="px-2 py-0.5 bg-amber-500/10 border border-amber-500/20 text-amber-400 text-[9px] font-bold rounded uppercase tracking-wider flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
            High
          </span>
        );
      case "MEDIUM":
        return (
          <span className="px-2 py-0.5 bg-yellow-500/10 border border-yellow-500/20 text-yellow-400 text-[9px] font-medium rounded uppercase tracking-wider">
            Medium
          </span>
        );
      default:
        return (
          <span className="px-2 py-0.5 bg-slate-500/10 border border-slate-500/20 text-slate-400 text-[9px] font-medium rounded uppercase tracking-wider">
            Low
          </span>
        );
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "NEW":
        return (
          <span className="px-2 py-0.5 bg-rose-500/10 border border-rose-500/20 text-rose-400 text-[9px] font-bold rounded uppercase tracking-wider">
            New
          </span>
        );
      case "ACKNOWLEDGED":
        return (
          <span className="px-2 py-0.5 bg-blue-500/10 border border-blue-500/20 text-blue-400 text-[9px] font-bold rounded uppercase tracking-wider">
            Acknowledged
          </span>
        );
      case "IN_PROGRESS":
        return (
          <span className="px-2 py-0.5 bg-purple-500/10 border border-purple-500/20 text-purple-400 text-[9px] font-bold rounded uppercase tracking-wider">
            Investigating
          </span>
        );
      case "RESOLVED":
        return (
          <span className="px-2 py-0.5 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[9px] font-bold rounded uppercase tracking-wider">
            Resolved
          </span>
        );
      default:
        return (
          <span className="px-2 py-0.5 bg-slate-500/10 border border-slate-500/20 text-slate-400 text-[9px] font-bold rounded uppercase tracking-wider">
            Dismissed
          </span>
        );
    }
  };

  const getSourceIcon = (source: string) => {
    switch (source) {
      case "prediction":
        return <Cpu className="w-4.5 h-4.5 text-indigo-400" />;
      case "network":
        return <Network className="w-4.5 h-4.5 text-violet-400" />;
      case "decision_support":
        return <AlertOctagon className="w-4.5 h-4.5 text-amber-400" />;
      default:
        return <MapPin className="w-4.5 h-4.5 text-cyan-400" />;
    }
  };

  const parseMetadata = (payloadStr: string | null) => {
    if (!payloadStr) return null;
    try {
      return JSON.parse(payloadStr);
    } catch {
      return null;
    }
  };

  return (
    <div className="space-y-6">
      {/* Search & Filtering Control Bar */}
      <div className="flex flex-col xl:flex-row gap-4 justify-between items-stretch xl:items-center bg-slate-950/40 border border-slate-900 rounded-2xl p-4 backdrop-blur-xl">
        <div className="flex flex-1 flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input
              type="text"
              placeholder="Search by title, details..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-slate-950 border border-slate-900 rounded-xl text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-slate-800 transition-all font-medium"
            />
          </div>
          
          <div className="flex flex-wrap gap-2">
            {/* Status Select */}
            <div className="relative">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="appearance-none bg-slate-950 border border-slate-900 rounded-xl pl-4 pr-10 py-2 text-[11px] font-semibold text-slate-300 focus:outline-none focus:border-slate-800 cursor-pointer"
              >
                <option value="">All Statuses</option>
                <option value="NEW">New</option>
                <option value="ACKNOWLEDGED">Acknowledged</option>
                <option value="IN_PROGRESS">Investigating</option>
                <option value="RESOLVED">Resolved</option>
                <option value="DISMISSED">Dismissed</option>
              </select>
              <Filter className="absolute right-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-500 pointer-events-none" />
            </div>

            {/* Severity Select */}
            <div className="relative">
              <select
                value={severityFilter}
                onChange={(e) => setSeverityFilter(e.target.value)}
                className="appearance-none bg-slate-950 border border-slate-900 rounded-xl pl-4 pr-10 py-2 text-[11px] font-semibold text-slate-300 focus:outline-none focus:border-slate-800 cursor-pointer"
              >
                <option value="">All Severities</option>
                <option value="CRITICAL">Critical</option>
                <option value="HIGH">High</option>
                <option value="MEDIUM">Medium</option>
                <option value="LOW">Low</option>
              </select>
              <Filter className="absolute right-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-500 pointer-events-none" />
            </div>

            {/* Source Select */}
            <div className="relative">
              <select
                value={sourceFilter}
                onChange={(e) => setSourceFilter(e.target.value)}
                className="appearance-none bg-slate-950 border border-slate-900 rounded-xl pl-4 pr-10 py-2 text-[11px] font-semibold text-slate-300 focus:outline-none focus:border-slate-800 cursor-pointer"
              >
                <option value="">All Sources</option>
                <option value="prediction">Predictions</option>
                <option value="network">Network Models</option>
                <option value="decision_support">Decision Support</option>
                <option value="geo">Geo Intelligence</option>
              </select>
              <Filter className="absolute right-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-500 pointer-events-none" />
            </div>
          </div>
        </div>

        <button
          onClick={onRefresh}
          disabled={loading}
          className="flex items-center justify-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-extrabold tracking-wide uppercase shadow-lg shadow-indigo-600/10 disabled:opacity-50 transition-all cursor-pointer"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
          Run Detection Rules
        </button>
      </div>

      {/* Alert Feed List */}
      {filteredAlerts.length === 0 ? (
        <div className="bg-slate-950/20 border border-slate-900/60 rounded-3xl py-16 text-center flex flex-col items-center justify-center backdrop-blur-xl">
          <Clock className="w-10 h-10 text-slate-600 mb-4 animate-pulse" />
          <h3 className="text-sm font-extrabold text-slate-300 uppercase tracking-wider">No Alerts Found</h3>
          <p className="text-xs text-slate-500 mt-1.5 max-w-sm px-6 font-medium leading-relaxed">
            There are no operational alerts matching your filter criteria. Click "Run Detection Rules" to evaluate model outputs.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredAlerts.map((alert) => {
            const isExpanded = expandedAlertId === alert.id;
            const meta = parseMetadata(alert.metadata_payload);
            
            return (
              <div
                key={alert.id}
                className={`border rounded-2xl bg-slate-950/40 backdrop-blur-xl transition-all duration-200 ${
                  isExpanded ? "border-slate-800 shadow-xl" : "border-slate-900/80 hover:border-slate-800"
                }`}
              >
                {/* Header click triggers expand */}
                <div
                  onClick={() => toggleExpand(alert.id)}
                  className="p-4 flex items-center justify-between gap-4 cursor-pointer select-none"
                >
                  <div className="flex items-center gap-4 min-w-0">
                    <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-900 shrink-0">
                      {getSourceIcon(alert.source)}
                    </div>
                    <div className="min-w-0">
                      <h4 className="text-xs font-black text-slate-200 tracking-wide uppercase leading-normal">
                        {alert.title}
                      </h4>
                      <p className="text-[10px] text-slate-500 font-mono mt-1">
                        Triggered {new Date(alert.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} • ID: {alert.id}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 shrink-0">
                    {getSeverityBadge(alert.severity)}
                    {getStatusBadge(alert.status)}
                    {isExpanded ? (
                      <ChevronUp className="w-4 h-4 text-slate-500" />
                    ) : (
                      <ChevronDown className="w-4 h-4 text-slate-500" />
                    )}
                  </div>
                </div>

                {/* Expanded Details Panel */}
                {isExpanded && (
                  <div className="px-6 pb-6 pt-2 border-t border-slate-900/80 space-y-5 animate-slide-down">
                    <div>
                      <h5 className="text-[9px] text-slate-500 font-extrabold uppercase tracking-widest mb-1.5">Anomaly Summary</h5>
                      <p className="text-[11px] text-slate-300 font-medium leading-relaxed bg-slate-950/60 border border-slate-900/40 rounded-xl p-3.5">
                        {alert.description}
                      </p>
                    </div>

                    {/* Metadata attributes rendering */}
                    {meta && (
                      <div>
                        <h5 className="text-[9px] text-slate-500 font-extrabold uppercase tracking-widest mb-2">Contextual Intelligence Data</h5>
                        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                          {Object.entries(meta).map(([key, val]) => (
                            <div key={key} className="bg-slate-950/60 border border-slate-900/40 rounded-xl p-3">
                              <span className="text-[8px] text-slate-500 font-mono uppercase tracking-wider block mb-1">
                                {key.replace(/_/g, " ")}
                              </span>
                              <span className="text-[10px] font-black text-slate-200 font-mono">
                                {typeof val === "number" && val <= 1 && val > 0 && key.includes("probability") 
                                  ? `${(val * 100).toFixed(1)}%` 
                                  : String(val)}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* State Lifecycle Updates */}
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-t border-slate-900/80 pt-5">
                      <div className="flex items-center gap-2">
                        <User className="w-3.5 h-3.5 text-indigo-400" />
                        <span className="text-[10px] text-slate-400 font-semibold">
                          Assigned User ID:{" "}
                          <strong className="text-slate-200 font-bold">
                            {alert.assigned_user_id ? `Officer #${alert.assigned_user_id}` : "Unassigned"}
                          </strong>
                        </span>
                      </div>

                      <div className="flex flex-wrap gap-2">
                        {alert.status === "NEW" && (
                          <>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                onUpdateStatus(alert.id, "ACKNOWLEDGED");
                              }}
                              className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-blue-400 border border-blue-500/20 text-[9px] font-black uppercase tracking-wider rounded-xl transition-all cursor-pointer flex items-center gap-1"
                            >
                              <Check className="w-3 h-3" /> Acknowledge
                            </button>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                onUpdateStatus(alert.id, "DISMISSED");
                              }}
                              className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-slate-400 border border-slate-700/20 text-[9px] font-black uppercase tracking-wider rounded-xl transition-all cursor-pointer flex items-center gap-1"
                            >
                              <X className="w-3 h-3" /> Dismiss
                            </button>
                          </>
                        )}

                        {(alert.status === "NEW" || alert.status === "ACKNOWLEDGED") && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              onUpdateStatus(alert.id, "IN_PROGRESS");
                            }}
                            className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-purple-400 border border-purple-500/20 text-[9px] font-black uppercase tracking-wider rounded-xl transition-all cursor-pointer flex items-center gap-1"
                          >
                            <Play className="w-3 h-3" /> Investigate
                          </button>
                        )}

                        {alert.status === "IN_PROGRESS" && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              onUpdateStatus(alert.id, "RESOLVED");
                            }}
                            className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white text-[9px] font-black uppercase tracking-wider rounded-xl transition-all cursor-pointer flex items-center gap-1"
                          >
                            <Check className="w-3 h-3" /> Resolve Anomaly
                          </button>
                        )}

                        {(alert.status === "RESOLVED" || alert.status === "DISMISSED") && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              onUpdateStatus(alert.id, "NEW");
                            }}
                            className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-slate-500 border border-slate-800 text-[9px] font-black uppercase tracking-wider rounded-xl transition-all cursor-pointer flex items-center gap-1"
                          >
                            <RotateCcw className="w-3 h-3" /> Re-open Alert
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
