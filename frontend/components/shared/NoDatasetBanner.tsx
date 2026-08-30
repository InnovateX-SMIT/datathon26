"use client";

import React from "react";
import Link from "next/link";
import { ShieldAlert, Upload, ArrowRight, Layers } from "lucide-react";

interface NoDatasetBannerProps {
  title?: string;
  description?: string;
}

export default function NoDatasetBanner({
  title = "No Active Dataset Selected",
  description = "CrimeNexus operations require at least one active database registry entry to query operational analytics, trend lines, predictive risk models, and spatial clusters."
}: NoDatasetBannerProps) {
  return (
    <div className="min-h-[75vh] flex flex-col items-center justify-center p-6 text-center text-slate-200">
      <div className="glass-card p-8 md:p-10 rounded-3xl border border-slate-800/80 max-w-lg w-full backdrop-blur-xl shadow-2xl space-y-6 bg-slate-900/60">
        <div className="relative mx-auto w-20 h-20 flex items-center justify-center rounded-2xl bg-indigo-500/10 border border-indigo-500/30 text-indigo-400">
          <ShieldAlert className="w-10 h-10 animate-pulse" />
          <div className="absolute -top-1 -right-1 w-4 h-4 bg-amber-500 rounded-full animate-ping" />
        </div>
        
        <div className="space-y-2">
          <h2 className="text-2xl font-bold uppercase tracking-tight text-white font-sans">
            {title}
          </h2>
          <p className="text-sm text-slate-400 leading-relaxed font-sans px-2">
            {description}
          </p>
        </div>

        <div className="pt-2 flex flex-col sm:flex-row items-center justify-center gap-3">
          <Link
            href="/dataset-manager"
            className="w-full sm:w-auto px-6 py-3.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm transition-all duration-200 shadow-lg shadow-indigo-600/30 flex items-center justify-center gap-2 font-sans group"
          >
            <Upload className="w-4 h-4 group-hover:-translate-y-0.5 transition-transform" />
            <span>Go to Dataset Manager</span>
            <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
          </Link>
        </div>
        
        <div className="pt-4 border-t border-slate-800/60 flex items-center justify-center gap-2 text-xs text-slate-500 font-mono">
          <Layers className="w-3.5 h-3.5" />
          <span>Upload CSV/Excel file in Dataset Manager to activate intelligence models</span>
        </div>
      </div>
    </div>
  );
}
