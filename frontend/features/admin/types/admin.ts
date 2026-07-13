export type UserRole = "ADMIN" | "SUPERINTENDENT" | "OFFICER" | "ANALYST" | "SUPERVISOR";
export type UserStatus = "active" | "inactive";

export interface AdminUser {
  id: number;
  name: string;
  email: string;
  role: UserRole;
  status: UserStatus;
  created_at: string;
  updated_at: string;
}

export interface AuditLogResponse {
  id: number;
  user_id: number | null;
  user_name: string | null;
  user_role: string | null;
  module: string | null;
  action: string;
  action_type: string | null;
  entity_type: string | null;
  entity_id: number | null;
  details: string | null;
  previous_value: string | null;
  new_value: string | null;
  ip_address: string | null;
  user_agent: string | null;
  request_method: string | null;
  api_endpoint: string | null;
  response_status: number | null;
  created_at: string;
}

export interface AuditLogListResponse {
  logs: AuditLogResponse[];
  total: number;
  page: number;
  page_size: number;
}

export interface DatabaseHealthInfo {
  status: string;
  dialect: string;
  url_masked: string;
}

export interface SystemHealth {
  database: DatabaseHealthInfo;
  tables: Record<string, number>;
  api: {
    status: string;
    version: string;
    environment: string;
  };
  server: {
    python_version: string;
    fastapi_version: string;
  };
}

export interface ModelStatusItem {
  name: string;
  path: string;
  status: "loaded" | "missing";
  size_kb: number | null;
}

export interface ModelStatusResponse {
  models: ModelStatusItem[];
  checked_at: string;
}

export interface DatasetTableInfo {
  table: string;
  record_count: number;
}

export interface DatasetStatusResponse {
  tables: DatasetTableInfo[];
  total_records: number;
  checked_at: string;
}
