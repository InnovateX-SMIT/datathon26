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

export interface CreateUserPayload {
  name: string;
  email: string;
  password: string;
  role: UserRole;
}

export interface UpdateUserPayload {
  name?: string;
  role?: UserRole;
}

export interface AuditLogEntry {
  id: number;
  user_id: number | null;
  action: string;
  entity_type: string | null;
  entity_id: number | null;
  details: string | null;
  created_at: string;
}

export interface AuditLogListResponse {
  logs: AuditLogEntry[];
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
