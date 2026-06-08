"use client";

import React from "react";
import { ShieldCheck, BarChart3, Bell, Shield, Layers, Server, Database } from "lucide-react";

export default function Dashboard() {
  const cards = [
    { title: "Crime Events", value: "682,607", desc: "Historical incident records", icon: ShieldCheck, color: "text-indigo-400" },
    { title: "Offender Profiles", value: "53,417", desc: "Suspect profiles loaded", icon: BarChart3, color: "text-violet-400" },
    { title: "Risk Alerts", value: "12 Active", desc: "Real-time anomaly monitoring", icon: Bell, color: "text-amber-400" },
    { title: "Patrol Force", value: "Optimal", desc: "Decision support active", icon: Shield, color: "text-emerald-400" },
  ];

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div>
        <span className="text-xs font-bold text-indigo-400 uppercase tracking-widest px-2.5 py-1 bg-indigo-500/10 border border-indigo-500/20 rounded-full">
          Core Command
        </span>
        <h1 className="text-3xl font-extrabold tracking-tight mt-2 text-slate-100">
          Executive Crime Intelligence Dashboard
        </h1>
        <p className="text-slate-400 mt-1 max-w-2xl">
          National police headquarters operational center for threat analysis, risk forecasting, and tactical resource optimization.
        </p>
      </div>

      {/* Grid Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {cards.map((card, i) => (
          <div key={i} className="glass-card p-6 rounded-2xl flex flex-col justify-between min-h-[140px]">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-xs text-slate-500 font-bold uppercase tracking-wider">{card.title}</p>
                <h3 className="text-2xl font-black mt-2 text-slate-100">{card.value}</h3>
              </div>
              <div className={`p-2.5 bg-slate-900/50 border border-slate-800 rounded-xl ${card.color}`}>
                <card.icon className="w-5 h-5" />
              </div>
            </div>
            <p className="text-xs text-slate-400 font-medium mt-4">{card.desc}</p>
          </div>
        ))}
      </div>

      {/* Blueprint Architecture Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 glass-card p-6 rounded-2xl space-y-6">
          <h2 className="text-lg font-bold text-slate-200 flex items-center gap-2">
            <Layers className="w-4 h-4 text-indigo-400" />
            Phase 0 Foundation Overview
          </h2>
          
          <div className="space-y-4 text-sm text-slate-400 leading-relaxed">
            <p>
              You are currently viewing the **Phase 0 Sandbox Platform Skeleton** built in accordance with the system design layout for Datathon 2026. This blueprint configures the structural architecture that future modules will connect with.
            </p>
            <p>
              All core APIs, routes, databases, and styling engines are active and communicating. The sidebar controls represent role-restricted command views mapping directly to downstream analytical servers.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
            <div className="p-4 bg-slate-950/40 border border-slate-900 rounded-xl flex flex-col gap-2">
              <div className="flex items-center gap-2 text-xs font-bold text-slate-300">
                <Server className="w-3.5 h-3.5 text-indigo-400" /> Backend
              </div>
              <p className="text-[11px] text-slate-500">FastAPI, Versioned Routers, Security, JWT Setup</p>
            </div>
            <div className="p-4 bg-slate-950/40 border border-slate-900 rounded-xl flex flex-col gap-2">
              <div className="flex items-center gap-2 text-xs font-bold text-slate-300">
                <Database className="w-3.5 h-3.5 text-violet-400" /> Database
              </div>
              <p className="text-[11px] text-slate-500">SQLAlchemy models mapping, connection pools</p>
            </div>
            <div className="p-4 bg-slate-950/40 border border-slate-900 rounded-xl flex flex-col gap-2">
              <div className="flex items-center gap-2 text-xs font-bold text-slate-300">
                <Shield className="w-3.5 h-3.5 text-emerald-400" /> Security
              </div>
              <p className="text-[11px] text-slate-500">Superintendent & Officer Role validation</p>
            </div>
          </div>
        </div>

        {/* Status System Logs */}
        <div className="glass-card p-6 rounded-2xl space-y-4">
          <h2 className="text-lg font-bold text-slate-200">System Trace Logs</h2>
          <div className="space-y-3 font-mono text-[10px] text-slate-500">
            <div className="flex justify-between items-center text-slate-400">
              <span>[OK] Core App Initiated</span>
              <span>22:45:00</span>
            </div>
            <div className="flex justify-between items-center text-slate-400">
              <span>[OK] SQLAlchemy Engines Loaded</span>
              <span>22:45:01</span>
            </div>
            <div className="flex justify-between items-center text-slate-400">
              <span>[OK] Next.js Router Configured</span>
              <span>22:45:02</span>
            </div>
            <div className="flex justify-between items-center text-indigo-400 font-semibold">
              <span>[INFO] Active Sandbox Session</span>
              <span>22:45:03</span>
            </div>
            <div className="flex justify-between items-center text-slate-500">
              <span>[INFO] Awaiting Phase 1 Analytics</span>
              <span>22:45:04</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
