import type {
  OverviewResponse,
  TrendResponse,
  CategoryResponse,
  ComparisonResponse,
} from "../types/analytics";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "https://crimenexus-backend.onrender.com";

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

export async function fetchOverview(): Promise<OverviewResponse> {
  return apiGet<OverviewResponse>("/api/v1/analytics/overview");
}

export async function fetchTrends(granularity: string): Promise<TrendResponse[]> {
  return apiGet<TrendResponse[]>(`/api/v1/analytics/trends?granularity=${granularity}`);
}

export async function fetchCategories(): Promise<CategoryResponse> {
  return apiGet<CategoryResponse>("/api/v1/analytics/categories");
}

export async function fetchComparison(): Promise<ComparisonResponse> {
  return apiGet<ComparisonResponse>("/api/v1/analytics/comparison");
}
