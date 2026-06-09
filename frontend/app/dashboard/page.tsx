"use client";

import React from "react";
import { LayoutDashboard } from "lucide-react";
import Placeholder from "@/components/placeholder";

export default function DashboardPage() {
  return (
    <Placeholder
      title="Executive Dashboard"
      badge="Core Command Center"
      icon={LayoutDashboard}
      description="The Executive Dashboard provides an overview of threat alerts, criminal networks, and geospatial hot spots. This layout will connect live intelligence panels in future development phases."
    />
  );
}
