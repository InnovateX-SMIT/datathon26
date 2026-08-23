import axios from "axios";
import type { Alert, AlertSummary } from "@/types/alert";
import { API_BASE, getAuthHeaders } from "@/services/api";

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
    params,
    timeout: 20000,
  });
  return res.data;
}

export async function fetchAlertSummary(): Promise<AlertSummary> {
  const res = await axios.get<AlertSummary>(`${API_BASE}/api/v1/alerts/summary`, {
    timeout: 20000,
  });
  return res.data;
}

export async function fetchAlertById(id: number): Promise<Alert> {
  const res = await axios.get<Alert>(`${API_BASE}/api/v1/alerts/${id}`, {
    timeout: 20000,
  });
  return res.data;
}

export async function generateAlerts(): Promise<Alert[]> {
  const res = await axios.post<Alert[]>(
    `${API_BASE}/api/v1/alerts/generate`,
    {},
    { headers: getAuthHeaders(), timeout: 30000 }
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
    { headers: getAuthHeaders(), timeout: 15000 }
  );
  return res.data;
}
