"use client";

import React from "react";
import { Map, Navigation, Locate, AlertTriangle } from "lucide-react";

export default function GeoIntelligence() {
  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div>
        <span className="text-xs font-bold text-indigo-400 uppercase tracking-widest px-2.5 py-1 bg-indigo-500/10 border border-indigo-500/20 rounded-full">
          Geospatial Engine
        </span>
        <h1 className="text-3xl font-extrabold tracking-tight mt-2 text-slate-100">
          Geospatial Crime Maps & Hotspot Detection
        </h1>
        <p className="text-slate-400 mt-1 max-w-2xl">
          Visualizing geographic densities and detecting DBSCAN hotspots across districts.
        </p>
      </div>

      {/* Map Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Left Side Filters Sidebar stub */}
        <div className="glass-card p-6 rounded-2xl space-y-6 lg:col-span-1">
          <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
            <Navigation className="w-4 h-4 text-indigo-400" /> Map Controls
          </h2>
          
          <div className="space-y-4">
            <div className="space-y-1">
              <label className="text-xs text-slate-500 font-semibold uppercase tracking-wider">Select District</label>
              <select className="w-full bg-slate-900 border border-[#1e293b] text-xs font-bold rounded-lg p-2.5 text-slate-400 focus:outline-none" disabled>
                <option>Bengaluru Urban (Stub)</option>
              </select>
            </div>
            
            <div className="space-y-1">
              <label className="text-xs text-slate-500 font-semibold uppercase tracking-wider">Crime Type</label>
              <select className="w-full bg-slate-900 border border-[#1e293b] text-xs font-bold rounded-lg p-2.5 text-slate-400 focus:outline-none" disabled>
                <option>All Types</option>
              </select>
            </div>

            <div className="p-3.5 bg-indigo-950/20 border border-indigo-500/15 rounded-xl text-xs text-slate-400 leading-relaxed flex gap-2">
              <Locate className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
              <span>DBSCAN parameters will update the interactive hotspots overlay dynamically.</span>
            </div>
          </div>
        </div>

        {/* Right Map Canvas Stub */}
        <div className="lg:col-span-3 glass-card rounded-2xl overflow-hidden min-h-[450px] relative border border-[#1e293b]/50 bg-slate-950/40 flex flex-col items-center justify-center text-center p-8 space-y-4">
          <div className="absolute inset-0 opacity-10 bg-[radial-gradient(#38bdf8_1px,transparent_1px)] [background-size:16px_16px] pointer-events-none" />
          
          <div className="w-16 h-16 rounded-full bg-slate-900 border border-[#1e293b] flex items-center justify-center text-slate-500">
            <Map className="w-6 h-6 text-indigo-400 animate-pulse" />
          </div>
          <div>
            <p className="text-slate-200 font-bold text-base">Leaflet Interactive Map Canvas</p>
            <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
              This panel will integrate Leaflet to render District Choropleth layouts and DBSCAN coordinate markers when Phase 2 geospatially aggregates crime logs.
            </p>
          </div>
          <div className="flex items-center gap-2 text-xs font-semibold text-amber-500/80 bg-amber-500/5 px-3.5 py-1.5 border border-amber-500/10 rounded-lg">
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>Map Layers Awaiting DB Sync</span>
          </div>
        </div>
      </div>
    </div>
  );
}
