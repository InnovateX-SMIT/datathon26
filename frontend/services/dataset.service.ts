import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "https://crimenexus-backend.onrender.com";

function getAuthHeaders(isMultipart = false) {
  return isMultipart ? {} : { "Content-Type": "application/json" };
}

export interface DatasetInfo {
  id: number;
  name: string;
  display_name: string;
  description: string | null;
  original_filename: string;
  source_type: string;
  row_count: number;
  column_count?: number;
  file_size: number;
  status: string;
  upload_status?: string;
  storage_path?: string | null;
  is_active: boolean;
  import_summary: string | null;
  upload_time: string | null;
  created_at: string | null;
  updated_at: string | null;
  schema_type?: string;
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

export interface DatasetPreview {
  first_20_rows: Array<Record<string, any>>;
  total_rows: number;
  total_columns: number;
  columns: string[];
  data_types: Record<string, string>;
}

export interface DatasetStatistics {
  total_rows: number;
  total_columns: number;
  missing_values: Record<string, number>;
  duplicate_rows: number;
  numeric_columns: string[];
  categorical_columns: string[];
}

export interface DatasetConfig {
  max_active_datasets: string;
}

export async function fetchDatasets(): Promise<DatasetInfo[]> {
  const res = await axios.get<DatasetInfo[]>(`${API_BASE}/api/v1/datasets/`, {
    headers: getAuthHeaders(),
  });
  return res.data;
}

export async function uploadDatasets(
  displayName: string | null,
  description: string | null,
  files: File[],
  preview: boolean = false
): Promise<any> {
  const formData = new FormData();
  if (displayName) formData.append("display_name", displayName);
  if (description) formData.append("description", description);
  
  if (files.length === 1) {
    formData.append("file", files[0]);
  } else {
    files.forEach(f => {
      formData.append("files", f);
    });
  }

  const res = await axios.post<any>(
    `${API_BASE}/api/v1/datasets/upload`,
    formData,
    {
      headers: getAuthHeaders(true),
      params: { preview }
    }
  );
  return res.data;
}

export async function detectSchemaType(file: File): Promise<{ schema_type: string }> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await axios.post<{ schema_type: string }>(
    `${API_BASE}/api/v1/datasets/detect`,
    formData,
    {
      headers: getAuthHeaders(true)
    }
  );
  return res.data;
}

export async function importFIRDataset(
  displayName: string | null,
  description: string | null,
  file: File,
  preview: boolean = false
): Promise<any> {
  const formData = new FormData();
  if (displayName) formData.append("display_name", displayName);
  if (description) formData.append("description", description);
  formData.append("file", file);

  const res = await axios.post<any>(
    `${API_BASE}/api/v1/fir/import`,
    formData,
    {
      headers: getAuthHeaders(true),
      params: { preview }
    }
  );
  return res.data;
}

export async function activateDataset(datasetId: number): Promise<DatasetInfo> {
  const res = await axios.post<DatasetInfo>(
    `${API_BASE}/api/v1/datasets/activate`,
    { dataset_id: datasetId },
    {
      headers: getAuthHeaders(),
    }
  );
  return res.data;
}

export async function deactivateDataset(datasetId: number): Promise<DatasetInfo> {
  const res = await axios.post<DatasetInfo>(
    `${API_BASE}/api/v1/datasets/deactivate`,
    { dataset_id: datasetId },
    {
      headers: getAuthHeaders(),
    }
  );
  return res.data;
}

export async function deleteDataset(datasetId: number): Promise<void> {
  await axios.delete(`${API_BASE}/api/v1/datasets/${datasetId}`, {
    headers: getAuthHeaders(),
  });
}

export async function deleteDatasetPermanent(datasetId: number): Promise<any> {
  const res = await axios.delete(
    `${API_BASE}/api/v1/datasets/${datasetId}/permanent`,
    {
      headers: getAuthHeaders(),
    }
  );
  return res.data;
}

export async function fetchDatasetSummary(datasetId: number): Promise<DatasetSummary> {
  const res = await axios.get<DatasetSummary>(
    `${API_BASE}/api/v1/datasets/${datasetId}/summary`,
    {
      headers: getAuthHeaders(),
    }
  );
  return res.data;
}

export async function fetchDatasetPreview(datasetId: number): Promise<DatasetPreview> {
  const res = await axios.get<DatasetPreview>(
    `${API_BASE}/api/v1/datasets/${datasetId}/preview`,
    {
      headers: getAuthHeaders(),
    }
  );
  return res.data;
}

export async function fetchDatasetStatistics(datasetId: number): Promise<DatasetStatistics> {
  const res = await axios.get<DatasetStatistics>(
    `${API_BASE}/api/v1/datasets/${datasetId}/statistics`,
    {
      headers: getAuthHeaders(),
    }
  );
  return res.data;
}

export async function fetchDatasetConfig(): Promise<DatasetConfig> {
  const res = await axios.get<DatasetConfig>(
    `${API_BASE}/api/v1/datasets/config`,
    {
      headers: getAuthHeaders(),
    }
  );
  return res.data;
}

export async function updateDatasetConfig(maxActive: string): Promise<DatasetConfig> {
  const res = await axios.put<DatasetConfig>(
    `${API_BASE}/api/v1/datasets/config`,
    { max_active_datasets: maxActive },
    {
      headers: getAuthHeaders(),
    }
  );
  return res.data;
}

export async function fetchActiveDatasets(): Promise<DatasetInfo[]> {
  const res = await axios.get<DatasetInfo[]>(
    `${API_BASE}/api/v1/datasets/active`,
    {
      headers: getAuthHeaders(),
    }
  );
  return res.data;
}
