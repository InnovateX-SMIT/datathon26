import type {
  OverviewResponse,
  TrendResponse,
  CategoryResponse,
  ComparisonResponse,
} from "../types/analytics";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function getAuthHeaders(): HeadersInit {
  const token = typeof window !== "undefined" ? localStorage.getItem("datathon_auth_token") : null;
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "GET",
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error(`API error ${res.status}: ${path}`);
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
