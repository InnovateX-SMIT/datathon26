import React from "react";
import Link from "next/link";
import FirCaseEditClient from "./edit-client";

export async function generateStaticParams() {
  return [{ id: "1" }];
}

interface PageProps {
  params: Promise<{ id: string }>;
}

export default async function FirCaseEditPage({ params }: PageProps) {
  const { id } = await params;
  const caseId = Number(id);

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

  return <FirCaseEditClient caseId={caseId} />;
}
