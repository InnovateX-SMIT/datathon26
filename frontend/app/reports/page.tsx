"use client";

import React from "react";
import { FileText, Download, Clock, CheckCircle } from "lucide-react";

export default function ExecutiveReports() {
  const reportsList = [
    { id: 1, title: "District Crime Summary - Bengaluru Urban (May 2026)", size: "2.4 MB", date: "June 01, 2026", format: "PDF" },
    { id: 2, title: "Predictive Recidivism Auditing Report", size: "1.8 MB", date: "May 15, 2026", format: "PDF" },
    { id: 3, title: "Simplex Optimization Allocation Matrix", size: "450 KB", date: "May 10, 2026", format: "CSV" },
  ];

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div>
        <span className="text-xs font-bold text-indigo-400 uppercase tracking-widest px-2.5 py-1 bg-indigo-500/10 border border-indigo-500/20 rounded-full">
          Report Dispatcher
        </span>
        <h1 className="text-3xl font-extrabold tracking-tight mt-2 text-slate-100">
          Executive Operations & Briefings
        </h1>
        <p className="text-slate-400 mt-1 max-w-2xl">
          Export strategic summaries, police station distributions, and predictive statistics.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {reportsList.map((report) => (
          <div key={report.id} className="glass-card p-6 rounded-2xl flex flex-col justify-between min-h-[185px]">
            <div>
              <div className="flex justify-between items-start">
                <span className="text-[10px] font-extrabold text-slate-500 uppercase tracking-wider">{report.format} Document</span>
                <span className="text-[10px] text-emerald-400 font-bold bg-emerald-500/5 px-2 py-0.5 border border-emerald-500/10 rounded-full flex items-center gap-1">
                  Ready <CheckCircle className="w-2.5 h-2.5 fill-emerald-500/15" />
                </span>
              </div>
              <h3 className="text-sm font-bold text-slate-200 mt-3.5 leading-snug">{report.title}</h3>
            </div>
            
            <div className="flex justify-between items-center border-t border-[#1e293b]/50 pt-4 mt-6">
              <div className="flex items-center gap-1.5 text-[10px] text-slate-500 font-semibold">
                <Clock className="w-3.5 h-3.5" />
                <span>{report.date}</span>
              </div>
              <button className="text-[10px] text-indigo-400 font-bold hover:text-indigo-300 transition-colors px-2.5 py-1.5 bg-indigo-500/5 border border-indigo-500/15 rounded-lg flex items-center gap-1 cursor-pointer">
                <Download className="w-3.5 h-3.5" /> Download ({report.size})
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
