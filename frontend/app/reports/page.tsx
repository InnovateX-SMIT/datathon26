"use client";

import React from "react";
import { FileSpreadsheet } from "lucide-react";
import Placeholder from "@/components/placeholder";

export default function ReportsPage() {
  return (
    <Placeholder
      title="Executive Reports"
      badge="Report Ingestion & Generation"
      icon={FileSpreadsheet}
      description="The Executive Reports module allows users to generate PDF report dossiers detailing patrol logs, crime density summaries, and optimized station performance logs."
    />
  );
}
