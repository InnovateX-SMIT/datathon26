import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function getAuthHeaders(isMultipart = false) {
  return isMultipart ? {} : { "Content-Type": "application/json" };
}

export interface DatabaseStats {
  health: string;
  counts: Record<string, number>;
  last_updated: Record<string, string | null>;
  timestamp: string;
}

export interface BulkUploadSummary {
  total_rows: number;
  valid_count: number;
  invalid_count: number;
  errors: Array<{
    row: number;
    errors: Record<string, string>;
    raw_data: Record<string, any>;
  }>;
  preview: Array<Record<string, any>>;
}

export async function fetchDatabaseStats(): Promise<DatabaseStats> {
  const res = await axios.get<DatabaseStats>(`${API_BASE}/api/v1/admin/database/stats`, {
    headers: getAuthHeaders(),
  });
  return res.data;
}

export async function fetchTableRecords(
  table: string,
  page: number = 1,
  pageSize: number = 10,
  q?: string,
  sortBy?: string,
  sortOrder?: string,
  filters?: Record<string, any>
): Promise<{ records: any[]; total: number; page: number; page_size: number }> {
  const params: Record<string, any> = {
    page,
    page_size: pageSize,
  };
  if (q && q.trim() !== "") params.q = q;
  if (sortBy) params.sort_by = sortBy;
  if (sortOrder) params.sort_order = sortOrder;
  if (filters && Object.keys(filters).length > 0) {
    params.filters = JSON.stringify(filters);
  }

  const res = await axios.get(`${API_BASE}/api/v1/admin/database/${table}`, {
    headers: getAuthHeaders(),
    params,
  });
  return res.data;
}

export async function fetchRecordById(table: string, id: number): Promise<any> {
  const res = await axios.get(`${API_BASE}/api/v1/admin/database/${table}/${id}`, {
    headers: getAuthHeaders(),
  });
  return res.data;
}

export async function createRecord(table: string, data: any): Promise<any> {
  const res = await axios.post(`${API_BASE}/api/v1/admin/database/${table}`, data, {
    headers: getAuthHeaders(),
  });
  return res.data;
}

export async function updateRecord(table: string, id: number, data: any): Promise<any> {
  const res = await axios.put(`${API_BASE}/api/v1/admin/database/${table}/${id}`, data, {
    headers: getAuthHeaders(),
  });
  return res.data;
}

export async function deleteRecord(table: string, id: number): Promise<any> {
  const res = await axios.delete(`${API_BASE}/api/v1/admin/database/${table}/${id}`, {
    headers: getAuthHeaders(),
  });
  return res.data;
}

export async function bulkUpload(
  table: string,
  file: File,
  preview: boolean = false
): Promise<BulkUploadSummary> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await axios.post<BulkUploadSummary>(
    `${API_BASE}/api/v1/admin/database/${table}/bulk-upload`,
    formData,
    {
      headers: getAuthHeaders(true),
      params: { preview },
    }
  );
  return res.data;
}

export async function exportTable(
  table: string,
  format: "csv" | "excel" = "csv",
  filters?: Record<string, any>
): Promise<Blob> {
  const params: Record<string, any> = {
    export_format: format,
  };
  if (filters && Object.keys(filters).length > 0) {
    params.filters = JSON.stringify(filters);
  }

  const res = await axios.get(`${API_BASE}/api/v1/admin/database/${table}/export`, {
    headers: getAuthHeaders(),
    params,
    responseType: "blob",
  });
  return res.data;
}

export interface DatasetInfo {
  id: number;
  name: string;
  display_name: string;
  description: string | null;
  original_filename: string;
  source_type: string;
  row_count: number;
  file_size: number;
  status: string;
  is_active: boolean;
  import_summary: string | null;
  upload_time: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface DatasetSummary {
  total_crimes: number;
  criminals: number;
  victims: number;
  date_range: {
    min: string | null;
    max: string | null;
  };
  districts: string[];
  upload_time: string | null;
  file_size: number;
}

export async function fetchDatasets(): Promise<DatasetInfo[]> {
  const res = await axios.get<DatasetInfo[]>(`${API_BASE}/api/v1/admin/datasets/`, {
    headers: getAuthHeaders(),
  });
  return res.data;
}

export async function uploadDataset(
  displayName: string,
  description: string | null,
  file: File
): Promise<DatasetInfo> {
  const formData = new FormData();
  formData.append("display_name", displayName);
  if (description) formData.append("description", description);
  formData.append("file", file);

  const res = await axios.post<DatasetInfo>(
    `${API_BASE}/api/v1/admin/datasets/upload`,
    formData,
    {
      headers: getAuthHeaders(true),
    }
  );
  return res.data;
}

export async function activateDataset(datasetId: number): Promise<DatasetInfo> {
  const res = await axios.post<DatasetInfo>(
    `${API_BASE}/api/v1/admin/datasets/activate`,
    { dataset_id: datasetId },
    {
      headers: getAuthHeaders(),
    }
  );
  return res.data;
}

export async function deleteDataset(datasetId: number): Promise<void> {
  await axios.delete(`${API_BASE}/api/v1/admin/datasets/${datasetId}`, {
    headers: getAuthHeaders(),
  });
}

export async function fetchDatasetSummary(datasetId: number): Promise<DatasetSummary> {
  const res = await axios.get<DatasetSummary>(
    `${API_BASE}/api/v1/admin/datasets/${datasetId}/summary`,
    {
      headers: getAuthHeaders(),
    }
  );
  return res.data;
}
