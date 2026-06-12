export interface Alert {
  id: number;
  crime_event_id: number | null;
  title: string;
  description: string;
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  source: "prediction" | "network" | "decision_support" | "geo";
  status: "NEW" | "ACKNOWLEDGED" | "IN_PROGRESS" | "RESOLVED" | "DISMISSED";
  assigned_user_id: number | null;
  metadata_payload: string | null;
  created_at: string;
  updated_at: string;
}

export interface AlertSourceStats {
  source: string;
  count: number;
}

export interface AlertSeverityStats {
  severity: string;
  count: number;
}

export interface AlertSummary {
  total_active: number;
  critical_count: number;
  resolved_count: number;
  today_count: number;
  by_source: AlertSourceStats[];
  by_severity: AlertSeverityStats[];
}
