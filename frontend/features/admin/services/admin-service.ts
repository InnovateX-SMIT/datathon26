import axios from "axios";
import type {
  AdminUser,
  CreateUserPayload,
  UpdateUserPayload,
  AuditLogListResponse,
  SystemHealth,
  ModelStatusResponse,
  DatasetStatusResponse,
} from "@/features/admin/types/admin";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function getAuthHeaders() {
  const token =
    typeof window !== "undefined"
      ? localStorage.getItem("datathon_auth_token")
      : null;
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

export async function fetchAdminUsers(): Promise<AdminUser[]> {
  const res = await axios.get<AdminUser[]>(`${API_BASE}/api/v1/admin/users`, {
    headers: getAuthHeaders(),
  });
  return res.data;
}

export async function createAdminUser(
  payload: CreateUserPayload
): Promise<AdminUser> {
  const res = await axios.post<AdminUser>(
    `${API_BASE}/api/v1/admin/users`,
    payload,
    { headers: getAuthHeaders() }
  );
  return res.data;
}

export async function getAdminUser(id: number): Promise<AdminUser> {
  const res = await axios.get<AdminUser>(
    `${API_BASE}/api/v1/admin/users/${id}`,
    { headers: getAuthHeaders() }
  );
  return res.data;
}

export async function updateAdminUser(
  id: number,
  payload: UpdateUserPayload
): Promise<AdminUser> {
  const res = await axios.put<AdminUser>(
    `${API_BASE}/api/v1/admin/users/${id}`,
    payload,
    { headers: getAuthHeaders() }
  );
  return res.data;
}

export async function deactivateAdminUser(id: number): Promise<AdminUser> {
  const res = await axios.put<AdminUser>(
    `${API_BASE}/api/v1/admin/users/${id}/deactivate`,
    {},
    { headers: getAuthHeaders() }
  );
  return res.data;
}

export async function activateAdminUser(id: number): Promise<AdminUser> {
  const res = await axios.put<AdminUser>(
    `${API_BASE}/api/v1/admin/users/${id}/activate`,
    {},
    { headers: getAuthHeaders() }
  );
  return res.data;
}

export async function fetchSystemHealth(): Promise<SystemHealth> {
  const res = await axios.get<SystemHealth>(
    `${API_BASE}/api/v1/admin/system/health`,
    { headers: getAuthHeaders() }
  );
  return res.data;
}

export async function fetchModelStatus(): Promise<ModelStatusResponse> {
  const res = await axios.get<ModelStatusResponse>(
    `${API_BASE}/api/v1/admin/system/models`,
    { headers: getAuthHeaders() }
  );
  return res.data;
}

export async function fetchAuditLogs(
  page: number = 1,
  pageSize: number = 50,
  action?: string
): Promise<AuditLogListResponse> {
  const params: Record<string, string | number> = {
    page,
    page_size: pageSize,
  };
  if (action && action !== "ALL") params.action = action;

  const res = await axios.get<AuditLogListResponse>(
    `${API_BASE}/api/v1/admin/audit-logs`,
    { headers: getAuthHeaders(), params }
  );
  return res.data;
}

export async function fetchDatasetStatus(): Promise<DatasetStatusResponse> {
  const res = await axios.get<DatasetStatusResponse>(
    `${API_BASE}/api/v1/admin/dataset/status`,
    { headers: getAuthHeaders() }
  );
  return res.data;
}

export async function refreshModels(): Promise<{ status: string; message: string }> {
  const res = await axios.post<{ status: string; message: string }>(
    `${API_BASE}/api/v1/admin/dataset/refresh-models`,
    {},
    { headers: getAuthHeaders() }
  );
  return res.data;
}

export async function triggerReimport(): Promise<{ status: string; message: string }> {
  const res = await axios.post<{ status: string; message: string }>(
    `${API_BASE}/api/v1/admin/dataset/reimport`,
    {},
    { headers: getAuthHeaders() }
  );
  return res.data;
}
