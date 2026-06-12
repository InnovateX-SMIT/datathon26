import React from "react";
import type { ReportSummary } from "../types/report";
import { FileText, Calendar } from "lucide-react";

interface Props {
  summary: ReportSummary;
  isSelected: boolean;
  onSelect: (id: number) => void;
}

export default function ReportSummaryCard({ summary, isSelected, onSelect }: Props) {
  const formatDate = (dateStr: string) => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return dateStr;
    }
  };

  const getReportTypeLabel = (type: string) => {
    switch (type.toLowerCase()) {
      case "district_intelligence":
        return "District Intelligence";
      case "crime_trend":
        return "Crime Trend Analysis";
      case "risk_assessment":
        return "Risk Assessment";
      case "network_intelligence":
        return "Network Intelligence";
      case "executive_summary":
        return "Executive Summary";
      default:
        return type;
    }
  };

  return (
    <button
      onClick={() => onSelect(summary.report_id)}
      className={`w-full text-left p-4 rounded-xl border transition-all duration-200 cursor-pointer ${
        isSelected
          ? "bg-indigo-600/15 border-indigo-500/50 shadow-md shadow-indigo-500/5"
          : "bg-slate-900/40 border-slate-900 hover:bg-slate-900/60 hover:border-slate-800"
      }`}
    >
      <div className="flex items-start gap-3">
        <div className={`p-2 rounded-lg ${isSelected ? "bg-indigo-500/20 text-indigo-400" : "bg-slate-950 text-slate-400"}`}>
          <FileText className="w-4 h-4" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-xs font-black text-slate-100 truncate tracking-tight">{summary.title}</p>
          <p className="text-[10px] text-slate-400 mt-1 uppercase tracking-wider font-semibold">
            {getReportTypeLabel(summary.report_type)}
          </p>
          <div className="flex items-center gap-1.5 text-[9px] text-slate-500 mt-2 font-medium">
            <Calendar className="w-3 h-3" />
            {formatDate(summary.generated_at)}
          </div>
        </div>
      </div>
    </button>
  );
}
