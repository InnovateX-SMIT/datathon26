"use client";

import React from "react";
import { Scale } from "lucide-react";
import Placeholder from "@/components/placeholder";

export default function DecisionSupportPage() {
  return (
    <Placeholder
      title="Decision Support"
      badge="Resource Allocation Optimizer"
      icon={Scale}
      description="The Decision Support engine solves resource allocation linear programs (LP Simplex) to automatically distribute personnel to the highest severity beats."
    />
  );
}
