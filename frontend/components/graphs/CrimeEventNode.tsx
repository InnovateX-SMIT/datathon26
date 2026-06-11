import React from "react";
import { Handle, Position } from "@xyflow/react";
import { AlertTriangle, Calendar } from "lucide-react";

interface CrimeEventNodeProps {
  id: string;
  data: {
    label: string;
    type: string;
    metadata?: {
      crime_type?: string;
      crime_category?: string;
      crime_subcategory?: string;
      severity?: number;
      crime_date?: string;
      [key: string]: unknown;
    };
  };
}

export default function CrimeEventNode({ id, data }: CrimeEventNodeProps) {
  const displayId = id.startsWith("crime_") ? id.substring(6) : id;
  const metadata = data.metadata || {};
  const crimeType = data.label || metadata.crime_type || "Unknown Incident";
  const category = metadata.crime_category || "Uncategorized";
  const severity = metadata.severity;
  const crimeDate = metadata.crime_date;

  return (
    <div className="glass-card bg-slate-950/90 border border-amber-500/30 hover:border-amber-500 shadow-[0_4px_20px_rgba(245,158,11,0.1)] hover:shadow-[0_4px_30px_rgba(245,158,11,0.2)] rounded-2xl p-4 min-w-[240px] text-slate-100 transition-all duration-300 relative group">
      {/* Orange Top indicator border */}
      <div className="absolute top-0 left-0 right-0 h-1 bg-amber-500 rounded-t-2xl" />

      {/* Target handle on top (Criminals connect to Crime Events) */}
      <Handle
        type="target"
        position={Position.Top}
        id="target"
        className="!w-3 !h-3 !bg-amber-500 !border-2 !border-slate-950 !rounded-full -top-1.5 transition-transform group-hover:scale-125"
      />

      <div className="flex items-start justify-between gap-3 pt-1">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-amber-500/10 border border-amber-500/20 rounded-xl group-hover:bg-amber-500/20 transition-colors">
            <AlertTriangle className="w-5 h-5 text-amber-400" />
          </div>
          <div>
            <span className="text-[10px] font-mono text-slate-500 uppercase tracking-widest block">
              Crime Event #{displayId}
            </span>
            <h4 className="font-bold text-slate-200 text-sm tracking-tight truncate max-w-[140px] mt-0.5">
              {crimeType}
            </h4>
          </div>
        </div>

        {/* Severity Badge */}
        {severity !== undefined && (
          <div className="flex flex-col items-center border border-amber-500/20 bg-amber-500/5 rounded-xl px-2 py-1">
            <span className="text-[8px] font-bold uppercase tracking-wider block text-slate-500">Severity</span>
            <span className="text-xs font-black tracking-tight text-amber-400">
              {severity.toFixed(1)}
            </span>
          </div>
        )}
      </div>

      {/* Incident details */}
      <div className="mt-3.5 pt-3 border-t border-slate-900 grid grid-cols-2 gap-2 text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
        <div className="col-span-2">
          <span className="text-slate-600 block text-[8px] font-bold">Category</span>
          <span className="text-slate-300 truncate block">{category}</span>
        </div>
        {crimeDate && (
          <div className="col-span-2 mt-1 flex items-center gap-1.5 text-slate-500">
            <Calendar className="w-3.5 h-3.5 text-slate-600 shrink-0" />
            <span className="text-[9px] font-mono tracking-normal text-slate-400">{crimeDate}</span>
          </div>
        )}
      </div>

      {/* Source handle on bottom (Crime Events connect to Locations) */}
      <Handle
        type="source"
        position={Position.Bottom}
        id="source"
        className="!w-3 !h-3 !bg-amber-500 !border-2 !border-slate-950 !rounded-full -bottom-1.5 transition-transform group-hover:scale-125"
      />
    </div>
  );
}
