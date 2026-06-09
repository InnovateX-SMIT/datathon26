"use client";

import React from "react";
import { Bell } from "lucide-react";
import Placeholder from "@/components/placeholder";

export default function AlertsPage() {
  return (
    <Placeholder
      title="Alerts Panel"
      badge="Real-time Dispatch Alerts"
      icon={Bell}
      description="The Alerts Panel displays active patrols, security alerts, and system warnings triggered by geospatial statistical anomalies."
    />
  );
}
