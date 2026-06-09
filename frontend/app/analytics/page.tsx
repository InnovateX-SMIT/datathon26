"use client";

import React from "react";
import { BarChart3 } from "lucide-react";
import Placeholder from "@/components/placeholder";

export default function AnalyticsPage() {
  return (
    <Placeholder
      title="Crime Analytics"
      badge="Statistical Analysis Engine"
      icon={BarChart3}
      description="The Crime Analytics module provides temporal analytics, category breakdown metrics, and district crime aggregation tools, awaiting live database ingestion."
    />
  );
}
