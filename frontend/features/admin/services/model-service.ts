const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function getAuthHeaders(): HeadersInit {
  return { "Content-Type": "application/json" };
}

export interface MLModelInfo {
  id: number;
  version: string;
  model_type: string;
  training_dataset_ids: string;
  algorithm: string;
  accuracy: number | null;
  precision: number | null;
  recall: number | null;
  f1_score: number | null;
  roc_auc: number | null;
  training_duration: number | null;
  status: string;
  model_path: string | null;
  is_production: boolean;
  training_logs: string | null;
  created_at: string;
}

export interface CompareResult {
  model_1: MLModelInfo;
  model_2: MLModelInfo;
  metrics_difference: Record<string, number | null>;
}

export async function fetchModelHistory(modelType?: string): Promise<MLModelInfo[]> {
  const query = modelType ? `?model_type=${modelType}` : "";
  const res = await fetch(`${API_BASE}/api/v1/admin/models/history${query}`, {
    method: "GET",
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to fetch model registry history.");
  }
  return res.json();
}

export async function trainModel(modelType: string): Promise<MLModelInfo> {
  const res = await fetch(`${API_BASE}/api/v1/admin/models/train`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({ model_type: modelType }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to trigger model retraining.");
  }
  return res.json();
}

export async function markProductionModel(modelId: number): Promise<MLModelInfo> {
  const res = await fetch(`${API_BASE}/api/v1/admin/models/production?model_id=${modelId}`, {
    method: "POST",
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to mark model version as production.");
  }
  return res.json();
}

export async function rollbackModel(modelId: number): Promise<MLModelInfo> {
  const res = await fetch(`${API_BASE}/api/v1/admin/models/rollback?model_id=${modelId}`, {
    method: "POST",
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to rollback model version.");
  }
  return res.json();
}

export async function deleteModel(modelId: number): Promise<void> {
  const res = await fetch(`${API_BASE}/api/v1/admin/models/${modelId}`, {
    method: "DELETE",
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to delete model registry entry.");
  }
}

export async function compareModels(modelId1: number, modelId2: number): Promise<CompareResult> {
  const res = await fetch(`${API_BASE}/api/v1/admin/models/compare`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({ model_id_1: modelId1, model_id_2: modelId2 }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to compare model versions.");
  }
  return res.json();
}

export async function fetchModelLogs(modelId: number): Promise<string> {
  const res = await fetch(`${API_BASE}/api/v1/admin/models/${modelId}/logs`, {
    method: "GET",
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to fetch model logs.");
  }
  return res.json();
}
