"use client";

import React from "react";
import { FileText } from "lucide-react";
import PageHeader from "@/components/layout/page-header";
import FirCaseForm from "@/features/fir/components/FirCaseForm";

interface FirCaseEditClientProps {
  caseId: number;
}

export default function FirCaseEditClient({ caseId }: FirCaseEditClientProps) {
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
