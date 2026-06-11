export interface PredictionResponse<T> {
  success: boolean;
  data: T;
}

export interface PredictionHealth {
  status: string;
  models_loaded: {
    repeat_offender: boolean;
    crime_type: boolean;
    crime_risk: boolean;
    hotspot: boolean;
  };
}

export interface RepeatOffenderRequest {
  age: number;
  occupation: string;
  caste: string;
  district: string;
}

export interface RepeatOffenderResult {
  probability: number;
  risk_level: "LOW" | "MEDIUM" | "HIGH";
}

export interface CrimeRiskRequest {
  district: string;
  crime_category: string;
  historical_crime_count: number;
}

export interface CrimeRiskResult {
  risk_score: number;
  risk_level: "LOW" | "MEDIUM" | "HIGH";
}

export interface CrimeTypeRequest {
  district: string;
  month: number;
  hour: number;
  day_of_week: number;
  historical_crime_count: number;
}

export interface CrimeTypeResult {
  crime_type: string;
  confidence: number;
}

export interface HotspotRequest {
  district: string;
  trend_metrics: number;
  historical_crime_growth: number;
}

export interface HotspotResult {
  hotspot_probability: number;
  trend: "RISING" | "STABLE" | "FALLING";
}

export interface SHAPImpact {
  feature: string;
  impact: number;
}

export interface ExplainRequest {
  prediction_type: "repeat-offender" | "crime-risk" | "crime-type" | "hotspot";
  features: Record<string, unknown>;
}
