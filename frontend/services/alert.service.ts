import axios from "axios";
import type { Alert, AlertSummary } from "@/types/alert";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function getAuthHeaders() {
  const token = typeof window !== "undefined" ? localStorage.getItem("datathon_auth_token") : null;
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

export async function fetchAlerts(
  status?: string,
  severity?: string,
  source?: string
): Promise<Alert[]> {
  const params: Record<string, string> = {};
  if (status) params.status = status;
  if (severity) params.severity = severity;
  if (source) params.source = source;

  const res = await axios.get<Alert[]>(`${API_BASE}/api/v1/alerts/`, {
    headers: getAuthHeaders(),
    params,
  });
  return res.data;
}

export async function fetchAlertSummary(): Promise<AlertSummary> {
  const res = await axios.get<AlertSummary>(`${API_BASE}/api/v1/alerts/summary`, {
    headers: getAuthHeaders(),
  });
  return res.data;
}

export async function fetchAlertById(id: number): Promise<Alert> {
  const res = await axios.get<Alert>(`${API_BASE}/api/v1/alerts/${id}`, {
    headers: getAuthHeaders(),
  });
  return res.data;
}

export async function generateAlerts(): Promise<Alert[]> {
  const res = await axios.post<Alert[]>(
    `${API_BASE}/api/v1/alerts/generate`,
    {},
    { headers: getAuthHeaders() }
  );
  return res.data;
}

export async function updateAlertStatus(
  id: number,
  status: string,
  assignedUserId?: number | null
): Promise<Alert> {
  const res = await axios.put<Alert>(
    `${API_BASE}/api/v1/alerts/${id}/status`,
    {
      status,
      assigned_user_id: assignedUserId,
    },
    { headers: getAuthHeaders() }
  );
  return res.data;
}
