export interface ReportType {
  key: string;
  name: string;
  description: string;
}

export interface ReportSummary {
  id: number;
  report_id: number;
  title: string;
  report_type: string;
  generated_at: string;
  executive_summary?: string;
}

export interface CrimeCategoryBreakdown {
  category: string;
  count: number;
}

export interface CrimeOverview {
  total_crimes: number;
  top_categories: CrimeCategoryBreakdown[];
  trend_direction: string;
}

export interface HighRiskLocation {
  district: string;
  crime_count: number;
  risk_level: string;
}

export interface PredictiveInsights {
  high_risk_locations: HighRiskLocation[];
  hotspot_count: number;
  risk_score_summary: {
    average_criminal_risk: number;
    high_risk_criminals_count: number;
    total_criminals_tracked: number;
  };
}

export interface NetworkKeyEntity {
  id: string;
  type: string;
  label: string;
  score: number;
}

export interface NetworkInsights {
  total_networks: number;
  largest_network_size: number;
  key_entities: NetworkKeyEntity[];
}

export interface Recommendation {
  id: number;
  priority: string;
  recommendation_text: string;
  reason: string;
  status: string;
}

export interface Alert {
  id: number;
  title: string;
  description: string;
  severity: string;
  source: string;
  status: string;
}

export interface Report {
  report_id: number;
  report_type: string;
  title: string;
  generated_at: string;
  executive_summary: string;
  crime_overview: CrimeOverview;
  predictive_insights: PredictiveInsights;
  network_insights: NetworkInsights;
  recommendations: Recommendation[];
  alerts: Alert[];
  dataset_name?: string;
  model_version?: string;
  prediction_accuracy?: number;
}
