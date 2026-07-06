import axios from "axios";
import type { NetworkCriminalSamplesResponse, NetworkGraphResponse } from "@/types/network";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function getAuthHeaders() {
  const token = typeof window !== "undefined" ? localStorage.getItem("datathon_auth_token") : null;
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

/**
 * Fetch the network graph for a given criminal ID.
 * Calls the Phase 6A backend API: GET /api/v1/network/criminal/{criminal_id}
 */
export async function fetchNetworkGraph(criminalId: number): Promise<NetworkGraphResponse> {
  const res = await axios.get<NetworkGraphResponse>(
    `${API_BASE}/api/v1/network/criminal/${criminalId}`,
    { headers: getAuthHeaders() }
  );
  return res.data;
}


export async function fetchSampleCriminals(limit = 10): Promise<NetworkCriminalSamplesResponse> {
  const res = await axios.get<NetworkCriminalSamplesResponse>(
    `${API_BASE}/api/v1/network/criminals/sample`,
    { headers: getAuthHeaders(), params: { limit } }
  );
  return res.data;
}
