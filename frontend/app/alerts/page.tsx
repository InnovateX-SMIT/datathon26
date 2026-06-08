"use client";

import React from "react";
import { Bell, AlertCircle, ShieldAlert, CheckCircle2 } from "lucide-react";

export default function AlertsPanel() {
  const mockAlerts = [
    { id: 1, type: "Severity Threshold", msg: "Spike in theft crimes observed in Beat Alpha", time: "10 mins ago", level: "critical" },
    { id: 2, type: "Recidivism Alert", msg: "Accused B flagged at high probability for repeat offenses", time: "1 hour ago", level: "high" },
    { id: 3, type: "Resource Gap", msg: "Beat Gamma CPC personnel deployment is below safety margins", time: "2 hours ago", level: "medium" },
  ];

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div>
        <span className="text-xs font-bold text-indigo-400 uppercase tracking-widest px-2.5 py-1 bg-indigo-500/10 border border-indigo-500/20 rounded-full">
          Operational Alerts
        </span>
        <h1 className="text-3xl font-extrabold tracking-tight mt-2 text-slate-100">
          Real-Time Threat Alerts & Monitoring
        </h1>
        <p className="text-slate-400 mt-1 max-w-2xl">
          Track operational alarms, severity threshold violations, and predictive system health.
        </p>
      </div>

      <div className="glass-card rounded-2xl overflow-hidden divide-y divide-[#1e293b]/50">
        {mockAlerts.map((alert) => (
          <div key={alert.id} className="p-6 flex items-start gap-4 hover:bg-slate-900/10 transition-colors">
            <div className="p-2 bg-slate-900 rounded-xl border border-slate-800 shrink-0">
              {alert.level === "critical" ? (
                <ShieldAlert className="w-5 h-5 text-rose-400 animate-bounce" />
              ) : alert.level === "high" ? (
                <AlertCircle className="w-5 h-5 text-amber-400" />
              ) : (
                <Bell className="w-5 h-5 text-blue-400" />
              )}
            </div>
            
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${
                  alert.level === "critical" ? "bg-rose-500/10 text-rose-400 border border-rose-500/20" :
                  alert.level === "high" ? "bg-amber-500/10 text-amber-400 border border-amber-500/20" :
                  "bg-blue-500/10 text-blue-400 border border-blue-500/20"
                }`}>
                  {alert.type}
                </span>
                <span className="text-[10px] text-slate-500 font-semibold">{alert.time}</span>
              </div>
              <p className="text-sm font-semibold text-slate-200 mt-2">{alert.msg}</p>
            </div>

            <button className="text-[10px] text-indigo-400 font-bold hover:text-indigo-300 transition-colors px-3 py-1.5 bg-indigo-500/5 border border-indigo-500/15 rounded-lg flex items-center gap-1 cursor-pointer">
              <CheckCircle2 className="w-3.5 h-3.5" /> Acknowledge
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
