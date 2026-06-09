"use client";

import React from "react";
import { Network } from "lucide-react";
import Placeholder from "@/components/placeholder";

export default function NetworkIntelligencePage() {
  return (
    <Placeholder
      title="Network Intelligence"
      badge="Criminal Network Linker"
      icon={Network}
      description="The Network Intelligence module charts organizational link analysis using centrality indicators to trace coordinate links and mastermind relationships."
    />
  );
}
