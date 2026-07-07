"use client";

import React from "react";
import { useParams } from "next/navigation";
import FirCaseDetail from "@/features/fir/components/FirCaseDetail";

export default function FirCaseDetailPage() {
  const params = useParams();
  const caseId = Number(params.id);

  if (isNaN(caseId) || caseId <= 0) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="glass-card rounded-2xl border border-red-500/20 bg-red-500/5 p-8 text-center max-w-sm">
          <h2 className="text-lg font-bold text-slate-200 mb-2">Invalid Case ID</h2>
          <p className="text-sm text-slate-400 mb-4">The case ID in the URL is not valid.</p>
          <a
            href="/fir/cases"
            className="inline-flex px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs uppercase tracking-wider rounded-xl transition-colors"
          >
            Back to Cases
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
      <FirCaseDetail caseId={caseId} />
    </div>
  );
}
