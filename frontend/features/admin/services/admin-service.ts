import axios from "axios";
import type {
  AuditLogListResponse,
  SystemHealth,
  ModelStatusResponse,
  DatasetStatusResponse,
} from "@/features/admin/types/admin";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function getAuthHeaders() {
  return { "Content-Type": "application/json" };
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
  const params: Record<string, string | number> = { page, page_size: pageSize };
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

export async function optimizeIndexes(): Promise<{ status: string; message: string }> {
  const res = await axios.post<{ status: string; message: string }>(
    `${API_BASE}/api/v1/admin/dataset/optimize`,
    {},
    { headers: getAuthHeaders() }
  );
  return res.data;
}

export async function backupDatabase(): Promise<{ status: string; message: string }> {
  const res = await axios.post<{ status: string; message: string }>(
    `${API_BASE}/api/v1/admin/dataset/backup`,
    {},
    { headers: getAuthHeaders() }
  );
  return res.data;
}
