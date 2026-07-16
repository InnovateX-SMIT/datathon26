import type { DistrictCrime, StationCrime, HeatmapPoint, HotspotCluster, GeoFiltersState, GeoIntelligenceResponse } from "../types/geo";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function getAuthHeaders(): HeadersInit {
  return { "Content-Type": "application/json" };
}

async function apiGet<T>(path: string, signal?: AbortSignal): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "GET",
    headers: getAuthHeaders(),
    signal,
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `API error ${res.status}: ${path}`);
  }
  return res.json() as Promise<T>;
}

function buildQueryString(filters: GeoFiltersState): string {
  const params = new URLSearchParams();
  if (filters.district) params.append("district", filters.district);
  if (filters.crime_type) params.append("crime_type", filters.crime_type);
  if (filters.start_date) params.append("start_date", filters.start_date);
  if (filters.end_date) params.append("end_date", filters.end_date);
  
  const query = params.toString();
  return query ? `?${query}` : "";
}

export async function fetchDistrictCrime(filters: GeoFiltersState): Promise<DistrictCrime[]> {
  return apiGet<DistrictCrime[]>(`/api/v1/geo/districts${buildQueryString(filters)}`);
}

export async function fetchStationCrime(filters: GeoFiltersState): Promise<StationCrime[]> {
  return apiGet<StationCrime[]>(`/api/v1/geo/stations${buildQueryString(filters)}`);
}

export async function fetchHeatmapPoints(filters: GeoFiltersState): Promise<HeatmapPoint[]> {
  return apiGet<HeatmapPoint[]>(`/api/v1/geo/heatmap${buildQueryString(filters)}`);
}

export async function fetchHotspotClusters(filters: GeoFiltersState): Promise<HotspotCluster[]> {
  return apiGet<HotspotCluster[]>(`/api/v1/geo/hotspots${buildQueryString(filters)}`);
}


export async function fetchGeoIntelligence(filters: GeoFiltersState, signal?: AbortSignal): Promise<GeoIntelligenceResponse> {
  return apiGet<GeoIntelligenceResponse>(`/api/v1/geo/intelligence${buildQueryString(filters)}`, signal);
}

export async function fetchGeoLookupOptions(): Promise<{ districts: string[]; categories: string[] }> {
  return apiGet<{ districts: string[]; categories: string[] }>("/api/v1/geo/lookup-options");
}
