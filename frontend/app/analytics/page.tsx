"use client";

import React from "react";
import { BarChart3, TrendingUp, Calendar, AlertCircle } from "lucide-react";

export default function CrimeAnalytics() {
  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div>
        <span className="text-xs font-bold text-indigo-400 uppercase tracking-widest px-2.5 py-1 bg-indigo-500/10 border border-indigo-500/20 rounded-full">
          Crime Analytics Engine
        </span>
        <h1 className="text-3xl font-extrabold tracking-tight mt-2 text-slate-100">
          Statistical Analysis & Crime Trends
        </h1>
        <p className="text-slate-400 mt-1 max-w-2xl">
          Deep temporal trend analysis, categorical profiling, and district breakdown aggregates.
        </p>
      </div>

      {/* Main layout stubs */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Trend Analysis Box */}
        <div className="glass-card p-6 rounded-2xl flex flex-col justify-between min-h-[300px]">
          <div className="flex justify-between items-center pb-4 border-b border-[#1e293b]/50">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-indigo-400" />
              <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider">Temporal Trend Analysis</h2>
            </div>
            <Calendar className="w-4 h-4 text-slate-500" />
          </div>
          
          <div className="flex-1 flex flex-col justify-center items-center text-center p-8 space-y-4">
            <div className="w-12 h-12 rounded-full bg-slate-900 border border-[#1e293b] flex items-center justify-center text-slate-500">
              <BarChart3 className="w-5 h-5" />
            </div>
            <div>
              <p className="text-slate-300 font-semibold text-sm">Temporal Trend Graph Placeholder</p>
              <p className="text-xs text-slate-500 mt-1 max-w-xs">
                This chart will render temporal fluctuations (yearly, monthly, daily) in incident volumes when Phase 1 goes live.
              </p>
            </div>
          </div>
        </div>

        {/* Category Analysis Box */}
        <div className="glass-card p-6 rounded-2xl flex flex-col justify-between min-h-[300px]">
          <div className="flex justify-between items-center pb-4 border-b border-[#1e293b]/50">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-violet-400" />
              <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider">Crime Category Distribution</h2>
            </div>
            <AlertCircle className="w-4 h-4 text-slate-500" />
          </div>

          <div className="flex-1 flex flex-col justify-center items-center text-center p-8 space-y-4">
            <div className="w-12 h-12 rounded-full bg-slate-900 border border-[#1e293b] flex items-center justify-center text-slate-500">
              <BarChart3 className="w-5 h-5" />
            </div>
            <div>
              <p className="text-slate-300 font-semibold text-sm">Category Breakdown Chart Placeholder</p>
              <p className="text-xs text-slate-500 mt-1 max-w-xs">
                This chart will visualizes crime categories (Theft, Burglary, Cybercrime) when data ingestion is completed.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
