import React from "react";
import type { Alert } from "../types/report";
import { ShieldAlert, AlertTriangle, Info, BellOff } from "lucide-react";

interface Props {
  alerts: Alert[];
}

export default function ReportAlertsSection({ alerts }: Props) {
  const getSeverityBadgeClass = (severity: string) => {
    switch (severity.toUpperCase()) {
      case "CRITICAL":
        return "bg-red-500/10 border-red-500/25 text-red-400";
      case "HIGH":
        return "bg-amber-500/10 border-amber-500/25 text-amber-400";
      case "MEDIUM":
        return "bg-indigo-500/10 border-indigo-500/25 text-indigo-400";
      default:
        return "bg-slate-500/10 border-slate-500/25 text-slate-400";
    }
  };

  const getAlertIcon = (severity: string) => {
    switch (severity.toUpperCase()) {
      case "CRITICAL":
        return <ShieldAlert className="w-4 h-4 text-red-500 animate-pulse" />;
      case "HIGH":
        return <AlertTriangle className="w-4 h-4 text-amber-500" />;
      default:
        return <Info className="w-4 h-4 text-indigo-400" />;
    }
  };

  return (
    <div className="glass-card p-6 rounded-2xl border border-slate-800/60 animate-fade-in">
      <div className="flex items-center gap-2 mb-5">
        <div className="w-1 h-5 bg-red-500 rounded" />
        <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
          Active Threat & Operational Alerts
        </h3>
      </div>

      {alerts.length === 0 ? (
        <div className="flex flex-col items-center justify-center p-8 border border-dashed border-slate-800 rounded-xl bg-slate-900/25 text-center">
          <BellOff className="w-8 h-8 text-slate-600 mb-2" />
          <p className="text-xs text-slate-500">No active alerts flagged for this report&apos;s timeframe.</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider">
                <th className="py-2.5 px-3">Alert Details</th>
                <th className="py-2.5 px-3 text-center">Severity</th>
                <th className="py-2.5 px-3 text-center">Source Module</th>
                <th className="py-2.5 px-3 text-right">Clearance Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/40 text-slate-300">
              {alerts.map((alert, idx) => (
                <tr key={idx} className="hover:bg-slate-900/35 transition-colors">
                  <td className="py-3 px-3">
                    <div className="font-semibold text-slate-200 flex items-center gap-1.5">
                      {getAlertIcon(alert.severity)}
                      {alert.title}
                    </div>
                    <p className="text-[10px] text-slate-400 mt-1 max-w-[500px] leading-relaxed">
                      {alert.description}
                    </p>
                  </td>
                  <td className="py-3 px-3 text-center">
                    <span className={`inline-block px-2 py-0.5 rounded text-[9px] font-bold border uppercase ${getSeverityBadgeClass(alert.severity)}`}>
                      {alert.severity}
                    </span>
                  </td>
                  <td className="py-3 px-3 text-center text-slate-400 capitalize font-medium">
                    {alert.source.replace("_", " ")}
                  </td>
                  <td className="py-3 px-3 text-right">
                    <span className="px-2 py-0.5 bg-slate-950/60 border border-slate-900 rounded text-[9px] font-bold uppercase text-slate-500 tracking-wider">
                      {alert.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
