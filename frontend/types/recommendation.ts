export interface Recommendation {
  id: number;
  crime_event_id: number | null;
  priority: "high" | "medium" | "low";
  recommendation_text: string;
  reason: string | null;
  status: "pending" | "resolved" | "dismissed";
  created_at: string;
}

export interface BeatAllocation {
  beat_name: string;
  asi_allocated: number;
  chc_allocated: number;
  cpc_allocated: number;
  normalized_severity: number;
}

export interface AllocationPayload {
  district: string;
  sanctioned_asi: number;
  sanctioned_chc: number;
  sanctioned_cpc: number;
}

export interface AllocationResponse {
  status: string;
  district: string;
  solved_allocation: BeatAllocation[];
}

export interface ResourceAllocation {
  id: number;
  district: string;
  allocated_asi: number;
  allocated_chc: number;
  allocated_cpc: number;
  solved_allocation: BeatAllocation[];
  created_at: string;
}

export interface DecisionSupportMetrics {
  totalCount: number;
  pendingCount: number;
  resolvedCount: number;
  dismissedCount: number;
}
