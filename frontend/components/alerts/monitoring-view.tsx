import React, { useState } from "react";
import {
  ShieldAlert,
  Send,
  Users,
  Compass,
  AlertTriangle,
  Play,
  CheckCircle,
  XCircle,
  Clock,
  MapPin,
  Activity
} from "lucide-react";
import type { Alert } from "@/types/alert";

interface MonitoringViewProps {
  alerts: Alert[];
  onUpdateStatus: (id: number, status: string) => Promise<void>;
  actionLoading: boolean;
}

export default function MonitoringView({
  alerts,
  onUpdateStatus,
  actionLoading
}: MonitoringViewProps) {
  const activeAlerts = alerts
    .filter((a) => ["NEW", "ACKNOWLEDGED", "IN_PROGRESS"].includes(a.status))
    .sort((a, b) => {
      const severityWeights: Record<string, number> = {
        CRITICAL: 4,
        HIGH: 3,
        MEDIUM: 2,
        LOW: 1
      };
      return (severityWeights[b.severity] || 0) - (severityWeights[a.severity] || 0);
    });

  const [selectedAlertId, setSelectedAlertId] = useState<number | null>(
    activeAlerts.length > 0 ? activeAlerts[0].id : null
  );
  const [dispatchStatus, setDispatchStatus] = useState<string | null>(null);

  // Sync selection if the active list changes and selection is invalid
  const selectedAlert = activeAlerts.find((a) => a.id === selectedAlertId) || activeAlerts[0];

  const handleDispatch = (squad: string) => {
    setDispatchStatus(`Squad "${squad}" dispatched to incident site.`);
    setTimeout(() => {
      setDispatchStatus(null);
    }, 4000);
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "CRITICAL":
        return "text-red-400 border-red-500/20 bg-red-500/10";
      case "HIGH":
        return "text-amber-400 border-amber-500/20 bg-amber-500/10";
      case "MEDIUM":
        return "text-yellow-400 border-yellow-500/20 bg-yellow-500/10";
      default:
        return "text-slate-400 border-slate-700/20 bg-slate-800/20";
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch min-h-[550px] animate-fade-in">
      {/* Active Alerts List Pane */}
      <div className="lg:col-span-5 bg-slate-950/40 border border-slate-900 rounded-3xl p-6 backdrop-blur-xl flex flex-col h-full">
        <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-900">
          <div className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-indigo-400 animate-pulse" />
            <div>
              <h3 className="text-md font-extrabold text-slate-100 uppercase tracking-tight">Active Dispatch Triage</h3>
              <p className="text-[9px] text-slate-400 font-semibold uppercase tracking-widest mt-0.5">Unresolved items ordered by severity</p>
            </div>
          </div>
          <span className="px-2.5 py-0.5 bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-[10px] font-black rounded-lg uppercase tracking-wider">
            {activeAlerts.length} Active
          </span>
        </div>

        {activeAlerts.length === 0 ? (
          <div className="flex-1 flex flex-col items-center justify-center py-12 text-center">
            <CheckCircle className="w-10 h-10 text-emerald-500/60 mb-3" />
            <h4 className="text-xs font-black text-slate-400 uppercase tracking-wider">No Active Emergencies</h4>
            <p className="text-[10px] text-slate-600 mt-1 max-w-[200px] leading-relaxed">
              All triggered anomalies are acknowledged, resolved, or dismissed.
            </p>
          </div>
        ) : (
          <div className="flex-1 overflow-y-auto space-y-3 max-h-[450px] pr-2">
            {activeAlerts.map((alert) => {
              const isSelected = selectedAlert && selectedAlert.id === alert.id;
              return (
                <div
                  key={alert.id}
                  onClick={() => setSelectedAlertId(alert.id)}
                  className={`p-4 border rounded-2xl cursor-pointer select-none transition-all ${
                    isSelected
                      ? "bg-slate-950/80 border-slate-800 shadow-md scale-[0.99]"
                      : "bg-slate-950/20 border-slate-900/60 hover:bg-slate-950/40 hover:border-slate-800"
                  }`}
                >
                  <div className="flex justify-between items-start gap-3 mb-2">
                    <h4 className="text-xs font-black text-slate-200 tracking-wide uppercase leading-snug">
                      {alert.title}
                    </h4>
                    <span className={`px-2 py-0.5 text-[8px] font-black rounded uppercase tracking-wider shrink-0 ${getSeverityColor(alert.severity)}`}>
                      {alert.severity}
                    </span>
                  </div>
                  <p className="text-[10.5px] text-slate-400 line-clamp-2 leading-relaxed">
                    {alert.description}
                  </p>
                  <div className="flex items-center justify-between mt-3 text-[9px] font-mono text-slate-500">
                    <span>Source: {alert.source}</span>
                    <span>{new Date(alert.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Selected Alert Operational Console */}
      <div className="lg:col-span-7 bg-slate-950/40 border border-slate-900 rounded-3xl p-6 backdrop-blur-xl flex flex-col justify-between h-full relative overflow-hidden">
        <div className="absolute top-0 right-0 w-[200px] h-[200px] rounded-full bg-indigo-500/5 blur-[60px] pointer-events-none" />

        {selectedAlert ? (
          <div className="space-y-6 flex-1 flex flex-col justify-between">
            {/* Header & Meta */}
            <div>
              <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-slate-900">
                <div>
                  <h3 className="text-sm font-black text-slate-100 uppercase tracking-wide">
                    {selectedAlert.title}
                  </h3>
                  <div className="flex flex-wrap gap-x-4 gap-y-1 mt-1.5 text-[9px] font-mono text-slate-500">
                    <span className="flex items-center gap-1">
                      <Clock className="w-3 h-3 text-indigo-400" />
                      Triggered: {new Date(selectedAlert.created_at).toLocaleString()}
                    </span>
                    <span>•</span>
                    <span>ID: {selectedAlert.id}</span>
                  </div>
                </div>
                
                <span className={`px-2.5 py-1 text-[9px] font-black rounded-lg uppercase tracking-wider ${getSeverityColor(selectedAlert.severity)}`}>
                  {selectedAlert.severity} PRIORITY
                </span>
              </div>

              {/* Description box */}
              <div className="mt-5 space-y-4">
                <div>
                  <h5 className="text-[9px] text-slate-500 font-extrabold uppercase tracking-widest mb-1.5">Description</h5>
                  <p className="text-[11px] text-slate-300 font-medium leading-relaxed bg-slate-950/60 border border-slate-900/40 rounded-xl p-4">
                    {selectedAlert.description}
                  </p>
                </div>

                {/* Dispatch Status alert */}
                {dispatchStatus && (
                  <div className="bg-emerald-500/15 border border-emerald-500/25 text-emerald-400 text-[10px] font-semibold rounded-xl p-3 flex items-center gap-2 animate-pulse">
                    <CheckCircle className="w-4 h-4 shrink-0" />
                    <span>{dispatchStatus}</span>
                  </div>
                )}

                {/* Mock Dispatch Options */}
                <div>
                  <h5 className="text-[9px] text-slate-500 font-extrabold uppercase tracking-widest mb-2.5">Immediate Tactical Dispatches</h5>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <button
                      onClick={() => handleDispatch("Emergency Patrol Jeep 4")}
                      className="p-3 bg-slate-950/80 hover:bg-slate-900 border border-slate-900 hover:border-slate-800 rounded-xl text-left transition-all cursor-pointer group"
                    >
                      <div className="flex items-center gap-2.5">
                        <div className="p-1.5 bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 rounded-lg group-hover:scale-105 transition-transform">
                          <Compass className="w-3.5 h-3.5" />
                        </div>
                        <div>
                          <span className="text-[10px] font-bold text-slate-200 block">Dispatch Patrol Jeep</span>
                          <span className="text-[8px] text-slate-500 font-mono">Immediate response team</span>
                        </div>
                      </div>
                    </button>

                    <button
                      onClick={() => handleDispatch("Crime Intelligence Squad B")}
                      className="p-3 bg-slate-950/80 hover:bg-slate-900 border border-slate-900 hover:border-slate-800 rounded-xl text-left transition-all cursor-pointer group"
                    >
                      <div className="flex items-center gap-2.5">
                        <div className="p-1.5 bg-violet-500/10 border border-violet-500/20 text-violet-400 rounded-lg group-hover:scale-105 transition-transform">
                          <Users className="w-3.5 h-3.5" />
                        </div>
                        <div>
                          <span className="text-[10px] font-bold text-slate-200 block">Deploy Investigation Unit</span>
                          <span className="text-[8px] text-slate-500 font-mono">Investigate co-offender links</span>
                        </div>
                      </div>
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Actions Footer */}
            <div className="border-t border-slate-900 pt-5 mt-6 flex flex-wrap gap-3 justify-end items-center">
              {selectedAlert.status === "NEW" && (
                <>
                  <button
                    disabled={actionLoading}
                    onClick={() => onUpdateStatus(selectedAlert.id, "ACKNOWLEDGED")}
                    className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-blue-400 border border-blue-500/20 text-[9px] font-black uppercase tracking-wider rounded-xl transition-all cursor-pointer flex items-center gap-1.5 disabled:opacity-50"
                  >
                    <Send className="w-3 h-3" /> Acknowledge Alert
                  </button>
                  <button
                    disabled={actionLoading}
                    onClick={() => onUpdateStatus(selectedAlert.id, "DISMISSED")}
                    className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-slate-500 border border-slate-800 text-[9px] font-black uppercase tracking-wider rounded-xl transition-all cursor-pointer flex items-center gap-1.5 disabled:opacity-50"
                  >
                    <XCircle className="w-3 h-3" /> Dismiss Alert
                  </button>
                </>
              )}

              {(selectedAlert.status === "NEW" || selectedAlert.status === "ACKNOWLEDGED") && (
                <button
                  disabled={actionLoading}
                  onClick={() => onUpdateStatus(selectedAlert.id, "IN_PROGRESS")}
                  className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-purple-400 border border-purple-500/20 text-[9px] font-black uppercase tracking-wider rounded-xl transition-all cursor-pointer flex items-center gap-1.5 disabled:opacity-50"
                >
                  <Play className="w-3 h-3" /> Start Investigation
                </button>
              )}

              {selectedAlert.status === "IN_PROGRESS" && (
                <button
                  disabled={actionLoading}
                  onClick={() => onUpdateStatus(selectedAlert.id, "RESOLVED")}
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-[9px] font-black uppercase tracking-wider rounded-xl transition-all cursor-pointer flex items-center gap-1.5 disabled:opacity-50"
                >
                  <CheckCircle className="w-3.5 h-3.5" /> Resolve Anomaly
                </button>
              )}

              {selectedAlert.status === "RESOLVED" && (
                <div className="flex items-center gap-2 text-emerald-400 bg-emerald-500/10 border border-emerald-500/25 px-3 py-1.5 rounded-xl">
                  <CheckCircle className="w-4 h-4" />
                  <span className="text-[10px] font-bold uppercase tracking-wider">Alert Resolved</span>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-center">
            <ShieldAlert className="w-12 h-12 text-slate-700 mb-4 animate-pulse" />
            <h4 className="text-xs font-black text-slate-400 uppercase tracking-wider">No Incident Selected</h4>
            <p className="text-[10px] text-slate-600 mt-1 max-w-[220px] leading-relaxed">
              Select an incident from the dispatch triage board to inspect details and assign squads.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
