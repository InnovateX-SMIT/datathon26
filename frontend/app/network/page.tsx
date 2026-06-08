"use client";

import React from "react";
import { Network, Users, Share2, GitCommit } from "lucide-react";

export default function NetworkIntelligence() {
  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div>
        <span className="text-xs font-bold text-indigo-400 uppercase tracking-widest px-2.5 py-1 bg-indigo-500/10 border border-indigo-500/20 rounded-full">
          NetworkX Graph Engine
        </span>
        <h1 className="text-3xl font-extrabold tracking-tight mt-2 text-slate-100">
          Criminal Network Intelligence & Association Graphs
        </h1>
        <p className="text-slate-400 mt-1 max-w-2xl">
          Dissect crime association patterns and link suspects to shared locations, cases, and accomplices.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Graph Summary Stats */}
        <div className="glass-card p-6 rounded-2xl space-y-6 lg:col-span-1">
          <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
            <Users className="w-4 h-4 text-indigo-400" /> Graph Statistics
          </h2>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 bg-slate-900/40 border border-[#1e293b]/50 rounded-xl">
              <span className="text-[10px] text-slate-500 font-bold uppercase">Nodes</span>
              <h4 className="text-lg font-black text-slate-300 mt-1">12,450</h4>
            </div>
            <div className="p-4 bg-slate-900/40 border border-[#1e293b]/50 rounded-xl">
              <span className="text-[10px] text-slate-500 font-bold uppercase">Edges</span>
              <h4 className="text-lg font-black text-slate-300 mt-1">34,120</h4>
            </div>
          </div>

          <div className="space-y-3">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Top Degree Centrality</h3>
            <div className="space-y-2">
              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-300 font-medium">Suspect: Criminal A</span>
                <span className="text-indigo-400 font-bold">0.85</span>
              </div>
              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-300 font-medium">Suspect: Criminal B</span>
                <span className="text-indigo-400 font-bold">0.68</span>
              </div>
              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-300 font-medium">Suspect: Criminal C</span>
                <span className="text-indigo-400 font-bold">0.55</span>
              </div>
            </div>
          </div>
        </div>

        {/* Network Canvas Stub */}
        <div className="lg:col-span-2 glass-card rounded-2xl overflow-hidden min-h-[400px] relative border border-[#1e293b]/50 bg-slate-950/40 flex flex-col items-center justify-center text-center p-8 space-y-4">
          <div className="absolute inset-0 opacity-10 bg-[radial-gradient(#6366f1_1px,transparent_1px)] [background-size:24px_24px] pointer-events-none" />

          <div className="w-16 h-16 rounded-full bg-slate-900 border border-[#1e293b] flex items-center justify-center text-slate-500">
            <Network className="w-6 h-6 text-indigo-400 animate-pulse" />
          </div>
          <div>
            <p className="text-slate-200 font-bold text-base">React Flow Network Canvas</p>
            <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
              This node canvas will render interactive, draggable connection graphs linking Criminals to FIR Crime Events using React Flow and NetworkX data schemas.
            </p>
          </div>
          <div className="flex gap-4">
            <div className="flex items-center gap-1.5 text-[10px] text-slate-400 bg-slate-900 px-3 py-1.5 border border-slate-800 rounded-full">
              <GitCommit className="w-3.5 h-3.5 text-indigo-400" /> Criminal Node
            </div>
            <div className="flex items-center gap-1.5 text-[10px] text-slate-400 bg-slate-900 px-3 py-1.5 border border-slate-800 rounded-full">
              <Share2 className="w-3.5 h-3.5 text-violet-400" /> Crime Event Node
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
