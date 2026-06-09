"use client";

import React from "react";
import { ShieldCheck } from "lucide-react";
import Placeholder from "@/components/placeholder";

export default function AdminPage() {
  return (
    <Placeholder
      title="Admin Portal"
      badge="Identity Access Management"
      icon={ShieldCheck}
      description="The Admin Portal oversees role configurations, API connection parameters, database seed initializations, and audit logs."
    />
  );
}
