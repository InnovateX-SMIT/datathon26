export interface DashboardSummary {
  total_crimes: number;
  total_victims: number;
  total_accused: number;
  active_cases: number;
  high_risk_criminals: number;
  total_criminals: number;
}

export interface TrendDataPoint {
  date: string;
  count: number;
}

export interface CategoryDataPoint {
  category: string;
  count: number;
}

export interface DistrictDataPoint {
  district: string;
  count: number;
}

export interface RecentCrimeItem {
  id: number;
  crime_type: string;
  crime_category: string;
  district: string;
  severity: number;
  status: string;
  crime_date: string;
  victim_count: number;
  accused_count: number;
}

export interface SystemStatus {
  database_status: string;
  total_records: number;
  last_updated: string;
  data_coverage_days: number;
}
