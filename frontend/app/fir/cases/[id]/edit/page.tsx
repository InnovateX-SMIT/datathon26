"use client";

import React from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { FileText } from "lucide-react";
import PageHeader from "@/components/layout/page-header";
import FirCaseForm from "@/features/fir/components/FirCaseForm";

export default function FirCaseEditPage() {
  const params = useParams();
  const caseId = Number(params.id);

  if (isNaN(caseId) || caseId <= 0) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="glass-card rounded-2xl border border-red-500/20 bg-red-500/5 p-8 text-center max-w-sm">
          <h2 className="text-lg font-bold text-slate-200 mb-2">Invalid Case ID</h2>
          <p className="text-sm text-slate-400 mb-4">The case ID in the URL is not valid.</p>
          <Link
            href="/fir/cases"
            className="inline-flex px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs uppercase tracking-wider rounded-xl transition-colors"
          >
            Back to Cases
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
      <PageHeader
        icon={FileText}
        iconColor="text-indigo-400"
        iconBg="bg-indigo-500/10 border border-indigo-500/20"
        badge="Modify Details"
        badgeColor="text-indigo-400 bg-indigo-500/10 border border-indigo-500/20"
        title="Edit FIR Case"
        subtitle="Modify First Information Report Details"
        description="Update the sections below to modify the FIR case details. Original CrimeNo and CaseNo will be preserved."
      />

      <FirCaseForm caseId={caseId} />
    </div>
  );
}
