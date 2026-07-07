import axios from "axios";
import type {
  Recommendation,
  AllocationPayload,
  AllocationResponse,
  ResourceAllocation,
} from "@/types/recommendation";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function getAuthHeaders() {
  return { "Content-Type": "application/json" };
}

export async function fetchRecommendations(status?: string, priority?: string): Promise<Recommendation[]> {
  const params: Record<string, string> = {};
  if (status) params.status = status;
  if (priority) params.priority = priority;

  const res = await axios.get<Recommendation[]>(
    `${API_BASE}/api/v1/recommendations/`,
    {
      headers: getAuthHeaders(),
      params,
    }
  );
  return res.data;
}

export async function updateRecommendationStatus(id: number, status: string): Promise<Recommendation> {
  const res = await axios.put<Recommendation>(
    `${API_BASE}/api/v1/recommendations/${id}`,
    { status },
    { headers: getAuthHeaders() }
  );
  return res.data;
}

export async function generateRecommendations(): Promise<Recommendation[]> {
  const res = await axios.post<Recommendation[]>(
    `${API_BASE}/api/v1/recommendations/generate`,
    {},
    { headers: getAuthHeaders() }
  );
  return res.data;
}

export async function solveResourceAllocation(payload: AllocationPayload): Promise<AllocationResponse> {
  const res = await axios.post<AllocationResponse>(
    `${API_BASE}/api/v1/recommendations/solve`,
    payload,
    { headers: getAuthHeaders() }
  );
  return res.data;
}

export async function fetchResourceAllocationHistory(): Promise<ResourceAllocation[]> {
  const res = await axios.get<ResourceAllocation[]>(
    `${API_BASE}/api/v1/recommendations/resource-allocation`,
    { headers: getAuthHeaders() }
  );
  return res.data;
}

export interface RecommendationHistoryItem {
  id: number;
  dataset_ids: string;
  model_version: string;
  alert_count: number;
  generated_recommendations_count: number;
  status: string;
  created_at: string;
}

export async function fetchRecommendationHistory(): Promise<RecommendationHistoryItem[]> {
  const res = await axios.get<RecommendationHistoryItem[]>(
    `${API_BASE}/api/v1/recommendations/history`,
    { headers: getAuthHeaders() }
  );
  return res.data;
}

export async function triggerPipelineSync(): Promise<{
  status: string;
  active_dataset_ids: number[];
  model_version: string;
  recommendations_count: number;
  alerts_count: number;
  history_id: number;
}> {
  const res = await axios.post(
    `${API_BASE}/api/v1/recommendations/sync`,
    {},
    { headers: getAuthHeaders() }
  );
  return res.data;
}
