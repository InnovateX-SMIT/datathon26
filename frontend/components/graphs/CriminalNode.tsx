import React from "react";
import { Handle, Position } from "@xyflow/react";
import { User } from "lucide-react";

interface CriminalNodeProps {
  id: string;
  data: {
    label: string;
    type: string;
    metadata?: {
      risk_score?: number;
      gender?: string;
      age?: number;
      status?: string;
      occupation?: string;
      [key: string]: unknown;
    };
  };
}

export default function CriminalNode({ id, data }: CriminalNodeProps) {
  const name = data.label || "Unknown Criminal";
  const displayId = id.startsWith("criminal_") ? id.substring(9) : id;
  const metadata = data.metadata || {};
  const riskScore = metadata.risk_score;

  // Color logic for risk score badge
  const getRiskBadgeStyles = (score?: number) => {
    if (score === undefined) return "bg-slate-800 text-slate-400 border-slate-700";
    if (score >= 0.7) return "bg-red-500/10 text-red-400 border-red-500/20";
    if (score >= 0.4) return "bg-amber-500/10 text-amber-400 border-amber-500/20";
    return "bg-green-500/10 text-green-400 border-green-500/20";
  };

  return (
    <div className="glass-card bg-slate-950/90 border border-blue-500/30 hover:border-blue-500 shadow-[0_4px_20px_rgba(59,130,246,0.1)] hover:shadow-[0_4px_30px_rgba(59,130,246,0.2)] rounded-2xl p-4 min-w-[240px] text-slate-100 transition-all duration-300 relative group">
      {/* Blue Top indicator border */}
      <div className="absolute top-0 left-0 right-0 h-1 bg-blue-500 rounded-t-2xl" />

      <div className="flex items-start justify-between gap-3 pt-1">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-500/10 border border-blue-500/20 rounded-xl group-hover:bg-blue-500/20 transition-colors">
            <User className="w-5 h-5 text-blue-400" />
          </div>
          <div>
            <span className="text-[10px] font-mono text-slate-500 uppercase tracking-widest block">
              Criminal ID #{displayId}
            </span>
            <h4 className="font-bold text-slate-200 text-sm tracking-tight truncate max-w-[140px] mt-0.5">
              {name}
            </h4>
          </div>
        </div>

        {/* Risk Score Badge */}
        {riskScore !== undefined && (
          <div className={`flex flex-col items-center border rounded-xl px-2 py-1 ${getRiskBadgeStyles(riskScore)}`}>
            <span className="text-[8px] font-bold uppercase tracking-wider block">Risk</span>
            <span className="text-xs font-black tracking-tight">
              {Math.round(riskScore * 100)}%
            </span>
          </div>
        )}
      </div>

      {/* Profile Details */}
      {(metadata.age || metadata.gender || metadata.status) && (
        <div className="mt-3.5 pt-3 border-t border-slate-900 grid grid-cols-2 gap-2 text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
          {metadata.age !== undefined && (
            <div>
              <span className="text-slate-600 block text-[8px] font-bold">Age</span>
              <span className="text-slate-300">{metadata.age} yrs</span>
            </div>
          )}
          {metadata.gender && (
            <div>
              <span className="text-slate-600 block text-[8px] font-bold">Gender</span>
              <span className="text-slate-300 truncate block">{metadata.gender}</span>
            </div>
          )}
          {metadata.status && (
            <div className="col-span-2 mt-1">
              <span className="text-slate-600 block text-[8px] font-bold">Status</span>
              <span className="text-blue-400 text-[9px] font-extrabold">{metadata.status}</span>
            </div>
          )}
        </div>
      )}

      {/* React Flow Connection Handles */}
      {/* Criminal is always source pointing to Crime Events */}
      <Handle
        type="source"
        position={Position.Bottom}
        id="source"
        className="!w-3 !h-3 !bg-blue-500 !border-2 !border-slate-950 !rounded-full -bottom-1.5 transition-transform group-hover:scale-125"
      />
    </div>
  );
}
