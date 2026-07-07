"use client";

import React from "react";
import { FilePlus } from "lucide-react";
import PageHeader from "@/components/layout/page-header";
import FirCaseForm from "@/features/fir/components/FirCaseForm";

export default function FirCaseNewPage() {
  return (
    <div className="space-y-6 max-w-5xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
      <PageHeader
        icon={FilePlus}
        iconColor="text-emerald-400"
        iconBg="bg-emerald-500/10 border border-emerald-500/20"
        badge="New Registration"
        badgeColor="text-emerald-400 bg-emerald-500/10 border border-emerald-500/20"
        title="Register FIR Case"
        subtitle="First Information Report Registration"
        description="Fill out the sections below to register a new FIR case. CrimeNo and CaseNo are automatically generated upon successful submission."
      />

      <FirCaseForm />
    </div>
  );
}
