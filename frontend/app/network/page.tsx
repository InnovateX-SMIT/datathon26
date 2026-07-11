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
          </div>
        </div>
      </div>
      {/* Network Graph */}
      <NetworkViewer />
    </div>
  );
}
