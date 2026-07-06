import type {
  DashboardSummary,
  TrendDataPoint,
  CategoryDataPoint,
  DistrictDataPoint,
  RecentCrimeItem,
  SystemStatus,
} from "@/types/dashboard";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function getAuthHeaders(): HeadersInit {
  return { "Content-Type": "application/json" };
}

async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "GET",
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `API error ${res.status}: ${path}`);
  }
  return res.json() as Promise<T>;
}

export async function fetchDashboardSummary(): Promise<DashboardSummary> {
  return apiGet<DashboardSummary>("/api/v1/analytics/dashboard/summary");
}

export async function fetchCrimeTrend(days = 30): Promise<TrendDataPoint[]> {
  return apiGet<TrendDataPoint[]>(`/api/v1/analytics/dashboard/trend?days=${days}`);
}

export async function fetchCategoryBreakdown(): Promise<CategoryDataPoint[]> {
  return apiGet<CategoryDataPoint[]>("/api/v1/analytics/dashboard/categories");
}

export async function fetchDistrictRanking(): Promise<DistrictDataPoint[]> {
  return apiGet<DistrictDataPoint[]>("/api/v1/analytics/dashboard/districts");
}

export async function fetchRecentCrimes(): Promise<RecentCrimeItem[]> {
  return apiGet<RecentCrimeItem[]>("/api/v1/analytics/dashboard/recent-crimes");
}

export async function fetchSystemStatus(): Promise<SystemStatus> {
  return apiGet<SystemStatus>("/api/v1/analytics/dashboard/system-status");
}
