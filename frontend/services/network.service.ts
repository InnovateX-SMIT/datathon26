import axios from "axios";
import type { NetworkCriminalSamplesResponse, NetworkGraphResponse } from "@/types/network";
import { API_BASE } from "@/services/api";

/**
 * Fetch the network graph for a given criminal ID.
 * Calls the Phase 6A backend API: GET /api/v1/network/criminal/{criminal_id}
 */
export async function fetchNetworkGraph(criminalId: number): Promise<NetworkGraphResponse> {
  const res = await axios.get<NetworkGraphResponse>(
    `${API_BASE}/api/v1/network/criminal/${criminalId}`,
    {}
  );
  return res.data;
}


export async function fetchSampleCriminals(limit = 10): Promise<NetworkCriminalSamplesResponse> {
  const res = await axios.get<NetworkCriminalSamplesResponse>(
    `${API_BASE}/api/v1/network/criminals/sample`,
    { params: { limit } }
  );
  return res.data;
}
