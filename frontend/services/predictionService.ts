import { apiClient } from "./api";

export interface CrimeRiskPredictionRequest {
  case_master_id?: number;
  district_id?: number;
  police_station_id?: number;
  crime_major_head_id?: number;
  crime_minor_head_id?: number;
  gravity_offence_id?: number;
  latitude?: number;
  longitude?: number;
  hour_of_day?: number;
  day_of_week?: number;
  month?: number;
  is_weekend?: number;
  is_night_time?: number;
  hist_station_crime_count_30d?: number;
  hist_district_crime_count_30d?: number;
}

export interface ContributingFactor {
  factor: string;
  value?: any;
  weight: number;
}

export interface CrimeRiskPredictionResponse {
  source: string;
  risk_tier_id?: number;
  risk_tier: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  confidence?: number;
  risk_score?: number;
  top_contributing_factors: ContributingFactor[];
}

export interface HotspotPredictionRequest {
  grid_lat?: number;
  grid_lon?: number;
  district_id?: number;
  police_station_id?: number;
  prior_7d_crime_count?: number;
  prior_30d_crime_count?: number;
  prior_90d_crime_count?: number;
  prior_180d_crime_count?: number;
  spatial_density_ratio?: number;
  peak_hour_window_id?: number;
}

export interface HotspotPredictionResponse {
  source: string;
  hotspot_flag_id?: number;
  hotspot_flag: "NON_HOTSPOT" | "FUTURE_HOTSPOT";
  confidence?: number;
  top_contributing_factors?: ContributingFactor[];
}

/**
 * Calls backend FastAPI /api/v1/predictions/crime-risk endpoint (Pipeline 1: QuickML).
 */
export async function predictCrimeRisk(
  payload: CrimeRiskPredictionRequest,
  signal?: AbortSignal
): Promise<CrimeRiskPredictionResponse> {
  const response = await apiClient.post<CrimeRiskPredictionResponse>(
    "/api/v1/predictions/crime-risk",
    payload,
    { signal }
  );
  return response.data;
}

/**
 * Calls backend FastAPI /api/v1/predictions/hotspots endpoint (Pipeline 2: QuickML).
 */
export async function predictFutureHotspot(
  payload: HotspotPredictionRequest,
  signal?: AbortSignal
): Promise<HotspotPredictionResponse> {
  const response = await apiClient.post<HotspotPredictionResponse>(
    "/api/v1/predictions/hotspots",
    payload,
    { signal }
  );
  return response.data;
}
