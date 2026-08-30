export interface OverviewResponse {
  total_crimes: number;
  total_victims: number;
  total_accused: number;
}

export interface TrendResponse {
  period: string;
  count: number;
}

export interface CategoryItem {
  name: string;
  count: number;
}

export interface CategoryResponse {
  categories: CategoryItem[];
  subcategories: CategoryItem[];
}

export interface ComparisonResponse {
  current_month: number;
  previous_month: number;
  month_change_percent: number;
  current_year: number;
  previous_year: number;
  year_change_percent: number;
}

// Phase 7: Sociological Intelligence
export interface DemographicItem {
  category: string;
  count: number;
}

export interface AgeVsCrimeItem {
  age_group: string;
  crime_category: string;
  count: number;
}

export interface GenderVsCrimeItem {
  gender: string;
  crime_category: string;
  count: number;
}

export interface DistrictDemographicItem {
  district: string;
  average_offender_age: number;
  predominant_gender: string;
  predominant_crime_category: string;
  count: number;
}

export interface DemographicsResponse {
  offender_age_distribution: DemographicItem[];
  offender_gender_distribution: DemographicItem[];
  victim_age_distribution: DemographicItem[];
  victim_gender_distribution: DemographicItem[];
  age_vs_crime: AgeVsCrimeItem[];
  gender_vs_crime: GenderVsCrimeItem[];
  district_demographics: DistrictDemographicItem[];
  data_limitations: string[];
}

export interface RiskCorrelationItem {
  group: string;
  average_risk: number;
}

export interface CorrelationMetric {
  variables: string;
  correlation_type: string;
  correlation_coefficient: number;
  sample_size: number;
  geographic_level: string;
  time_period: string;
  interpretation: string;
}

export interface SociologicalRiskResponse {
  age_group_risk: RiskCorrelationItem[];
  gender_risk: RiskCorrelationItem[];
  district_risk: RiskCorrelationItem[];
  repeat_involvement_risk: RiskCorrelationItem[];
  correlations: CorrelationMetric[];
}

export interface SocioEconomicCorrelationResponse {
  data_available: boolean;
  error_message: string;
}

