"use client";

import React from "react";
import { LucideIcon, Cpu } from "lucide-react";

interface PlaceholderProps {
  title: string;
  badge?: string;
  icon?: LucideIcon;
  description?: string;
}

export default function Placeholder({
  title,
  badge = "System Intelligence Module",
  icon: Icon = Cpu,
  description = "This module will ingest, structure, and analyze real-time police incident data streams when the downstream phases are deployed."
}: PlaceholderProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[70vh] py-12 px-4 relative overflow-hidden animate-fade-in">
      {/* Background ambient lighting glow */}
      <div className="absolute top-[50%] left-[50%] translate-x-[-50%] translate-y-[-50%] w-[350px] h-[350px] rounded-full bg-indigo-500/5 blur-[80px] pointer-events-none" />
      <div className="absolute inset-0 opacity-[0.02] bg-[radial-gradient(#6366f1_1px,transparent_1px)] [background-size:16px_16px] pointer-events-none" />

      <div className="glass-card max-w-lg w-full p-8 rounded-3xl border border-[#1e293b]/60 shadow-[0_15px_30px_rgba(0,0,0,0.4)] text-center relative overflow-hidden">
        {/* Top glowing stripe */}
        <div className="absolute top-0 left-0 w-full h-[1.5px] bg-gradient-to-r from-transparent via-indigo-500/40 to-transparent" />

        {/* Dynamic Glowing Icon Container */}
        <div className="mx-auto bg-indigo-600/10 border border-indigo-500/20 p-4 rounded-2xl w-fit mb-6 shadow-[0_0_15px_rgba(99,102,241,0.1)] group hover:border-indigo-500/40 transition-all duration-300">
          <Icon className="w-10 h-10 text-indigo-400 animate-pulse" />
        </div>

        {/* Category Badge */}
        <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest px-3 py-1 bg-indigo-500/10 border border-indigo-500/20 rounded-full">
          {badge}
        </span>

        {/* Title & Page Header */}
        <h1 className="text-2xl font-black tracking-tight mt-4 text-slate-100 uppercase">
          {title}
        </h1>

        {/* Coming in future phases banner */}
        <div className="py-2.5 px-4 bg-slate-950/45 border border-slate-900 rounded-xl font-bold text-xs text-slate-400 mt-5 inline-flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-indigo-500 animate-ping" />
          <span>Coming in future phases</span>
        </div>

        {/* Description details */}
        <p className="text-slate-400 text-xs mt-6 leading-relaxed max-w-sm mx-auto font-medium">
          {description}
        </p>

        {/* Subtle decorative grid logs */}
        <div className="mt-8 pt-6 border-t border-[#1e293b]/40 flex justify-between items-center text-[9px] font-mono text-slate-600 tracking-wider">
          <span>SECURE SYSTEM GRID</span>
          <span>PHASE 1 ACTIVE</span>
        </div>
      </div>
    </div>
  );
}
