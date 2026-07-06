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
