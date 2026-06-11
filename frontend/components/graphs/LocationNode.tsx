import React from "react";
import { Handle, Position } from "@xyflow/react";
import { MapPin, Navigation } from "lucide-react";

interface LocationNodeProps {
  id: string;
  data: {
    label: string;
    type: string;
    metadata?: {
      state?: string;
      district?: string;
      station?: string;
      area?: string;
      latitude?: number;
      longitude?: number;
      [key: string]: unknown;
    };
  };
}

export default function LocationNode({ id, data }: LocationNodeProps) {
  const displayId = id.startsWith("location_") ? id.substring(9) : id;
  const metadata = data.metadata || {};
  const labelParts = data.label ? data.label.split(",") : [];
  
  const district = metadata.district || labelParts[0]?.trim() || "Unknown District";
  const state = metadata.state || labelParts[1]?.trim() || "Unknown State";
  const station = metadata.station || "Central Station"; // Fallback placeholder to maintain clean styling
  const area = metadata.area || "Downtown Beat"; // Fallback placeholder to maintain clean styling
  const latitude = metadata.latitude;
  const longitude = metadata.longitude;

  return (
    <div className="glass-card bg-slate-950/90 border border-emerald-500/30 hover:border-emerald-500 shadow-[0_4px_20px_rgba(16,185,129,0.1)] hover:shadow-[0_4px_30px_rgba(16,185,129,0.2)] rounded-2xl p-4 min-w-[240px] text-slate-100 transition-all duration-300 relative group">
      {/* Green Top indicator border */}
      <div className="absolute top-0 left-0 right-0 h-1 bg-emerald-500 rounded-t-2xl" />

      {/* Target handle on top (Crime Events connect to Locations) */}
      <Handle
        type="target"
        position={Position.Top}
        id="target"
        className="!w-3 !h-3 !bg-emerald-500 !border-2 !border-slate-950 !rounded-full -top-1.5 transition-transform group-hover:scale-125"
      />

      <div className="flex items-start justify-between gap-3 pt-1">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-emerald-500/10 border border-emerald-500/20 rounded-xl group-hover:bg-emerald-500/20 transition-colors">
            <MapPin className="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <span className="text-[10px] font-mono text-slate-500 uppercase tracking-widest block">
              Location ID #{displayId}
            </span>
            <h4 className="font-bold text-slate-200 text-sm tracking-tight truncate max-w-[140px] mt-0.5">
              {district}
            </h4>
          </div>
        </div>
      </div>

      {/* Location specifics */}
      <div className="mt-3.5 pt-3 border-t border-slate-900 grid grid-cols-2 gap-2 text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
        <div>
          <span className="text-slate-600 block text-[8px] font-bold">Station</span>
          <span className="text-slate-300 truncate block">{station}</span>
        </div>
        <div>
          <span className="text-slate-600 block text-[8px] font-bold">Beat Area</span>
          <span className="text-slate-300 truncate block">{area}</span>
        </div>
        <div className="col-span-2">
          <span className="text-slate-600 block text-[8px] font-bold">Region</span>
          <span className="text-slate-300 truncate block">{state}</span>
        </div>
        {latitude !== undefined && longitude !== undefined && (
          <div className="col-span-2 mt-1.5 flex items-center gap-1 text-slate-500 border-t border-slate-900/60 pt-2">
            <Navigation className="w-3.5 h-3.5 text-slate-600 shrink-0 rotate-45" />
            <span className="text-[9.5px] font-mono tracking-normal text-slate-400">
              {latitude.toFixed(4)}° N, {longitude.toFixed(4)}° E
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
