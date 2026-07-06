"use client";

import React from "react";
import { Database } from "lucide-react";
import DatabaseManagementPanel from "@/features/admin/components/database-management-panel";

export default function DatabaseManagementPage() {
  return (
    <div className="min-h-screen py-8 px-4 sm:px-6 lg:px-8 space-y-8 animate-fade-in relative">
      {/* Background ambient glows */}
      <div className="absolute top-[10%] right-[5%] w-[500px] h-[500px] rounded-full bg-indigo-500/5 blur-[130px] pointer-events-none" />
      <div className="absolute bottom-[10%] left-[8%] w-[400px] h-[400px] rounded-full bg-violet-500/5 blur-[110px] pointer-events-none" />

      {/* ── Header ──────────────────────────────────────────────────────────── */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-900/80 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-indigo-500/10 border border-indigo-500/20 rounded-2xl">
              <Database className="w-6 h-6 text-indigo-400" />
            </div>
            <div>
              <h1 className="text-3xl font-black text-slate-100 uppercase tracking-tight">
                Database Management
              </h1>
              <p className="text-slate-400 text-xs font-semibold uppercase tracking-widest mt-1">
                Administrative CRUD controls & Data Synchronization
              </p>
            </div>
          </div>
          <p className="text-slate-400 text-sm mt-3 max-w-2xl leading-relaxed">
            Perform administrative CRUD adjustments, verify geospatial or incident statistics,
            run bulk dataset imports from spreadsheets, and download exported records.
          </p>
        </div>

        {/* Live Status Badge */}
        <div className="flex items-center gap-2 px-4 py-2.5 bg-indigo-500/10 border border-indigo-500/20 rounded-2xl self-start">
          <span className="w-2 h-2 rounded-full bg-indigo-400 animate-pulse" />
          <span className="text-indigo-400 text-xs font-black uppercase tracking-wider">
            DB Connected
          </span>
        </div>
      </div>

      {/* ── Main Component View ─────────────────────────────────────────────── */}
      <div className="relative z-10">
        <DatabaseManagementPanel />
      </div>

      {/* ── Footer ───────────────────────────────────────────────────────────── */}
      <div className="pt-6 mt-4 border-t border-slate-900/60 flex justify-between items-center text-[9px] font-mono text-slate-700/60 tracking-widest select-none">
        <span>DATABASE ADMINISTRATION ENVIRONMENT</span>
        <span>ENGINE CLOUD ACTIVE</span>
      </div>
    </div>
  );
}
