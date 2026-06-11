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
