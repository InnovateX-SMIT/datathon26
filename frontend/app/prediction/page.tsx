"use client";

import React from "react";
import { BrainCircuit } from "lucide-react";
import Placeholder from "@/components/placeholder";

export default function PredictionPage() {
  return (
    <Placeholder
      title="Predictive Intelligence"
      badge="Risk & Recidivism Forecaster"
      icon={BrainCircuit}
      description="The Predictive Intelligence module employs machine learning classifiers to predict recidivism risks and historical incident probability indexes."
    />
  );
}
