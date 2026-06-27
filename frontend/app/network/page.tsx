"use client";

import React from "react";
import { Network } from "lucide-react";
import NetworkViewer from "@/features/network/components/NetworkViewer";

export default function NetworkIntelligencePage() {
  return (
    <div className="space-y-6 animate-fade-in">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/70 pb-6">
        <div className="flex items-start gap-3.5">
          <div className="p-2.5 bg-indigo-500/10 border border-indigo-500/20 rounded-xl shrink-0">
            <Network className="w-5 h-5 text-indigo-400" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-slate-100 uppercase tracking-tight leading-tight">
              Network Intelligence
            </h1>
            <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-widest mt-1">
              Criminal Network Graph Analysis
            </p>
            <p className="text-sm text-slate-400 mt-2.5 max-w-2xl leading-relaxed">
              Explore criminal association networks, gang structures, and relationship clusters extracted from FIR co-accused data.
            </p>
          </div>
        </div>
      </div>
      {/* Network Graph */}
      <NetworkViewer />
    </div>
  );
}
