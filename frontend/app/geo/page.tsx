"use client";

import React from "react";
import { Map } from "lucide-react";
import Placeholder from "@/components/placeholder";

export default function GeoIntelligencePage() {
  return (
    <Placeholder
      title="Geo Intelligence"
      badge="Geospatial Mapping Suite"
      icon={Map}
      description="The Geo Intelligence module integrates geospatial overlays, heatmaps, and DBSCAN clustering density markers to track hotspot patterns geographically."
    />
  );
}
