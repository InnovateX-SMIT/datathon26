import axios from "axios";
import type {
  PredictionResponse,
  PredictionHealth,
  RepeatOffenderRequest,
  RepeatOffenderResult,
  CrimeRiskRequest,
  CrimeRiskResult,
  CrimeTypeRequest,
  CrimeTypeResult,
  HotspotRequest,
  HotspotResult,
  SHAPImpact,
} from "@/types/prediction";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function getAuthHeaders() {
  return { "Content-Type": "application/json" };
}

export async function fetchPredictionHealth(): Promise<PredictionHealth> {
  const res = await axios.get<PredictionResponse<PredictionHealth>>(
    `${API_BASE}/api/v1/predictions/health`,
    { headers: getAuthHeaders() }
  );
  return res.data.data;
}

export async function predictRepeatOffender(data: RepeatOffenderRequest): Promise<RepeatOffenderResult> {
  const res = await axios.post<PredictionResponse<RepeatOffenderResult>>(
    `${API_BASE}/api/v1/predictions/repeat-offender`,
    data,
    { headers: getAuthHeaders() }
  );
  return res.data.data;
}

export async function predictCrimeRisk(data: CrimeRiskRequest): Promise<CrimeRiskResult> {
  const res = await axios.post<PredictionResponse<CrimeRiskResult>>(
    `${API_BASE}/api/v1/predictions/crime-risk`,
    data,
    { headers: getAuthHeaders() }
  );
  return res.data.data;
}

export async function predictCrimeType(data: CrimeTypeRequest): Promise<CrimeTypeResult> {
  const res = await axios.post<PredictionResponse<CrimeTypeResult>>(
    `${API_BASE}/api/v1/predictions/crime-type`,
    data,
    { headers: getAuthHeaders() }
  );
  return res.data.data;
}

export async function predictHotspot(data: HotspotRequest): Promise<HotspotResult> {
  const res = await axios.post<PredictionResponse<HotspotResult>>(
    `${API_BASE}/api/v1/predictions/hotspot`,
    data,
    { headers: getAuthHeaders() }
  );
  return res.data.data;
}

export async function fetchShapExplanation(
  predictionType: "repeat-offender" | "crime-risk" | "crime-type" | "hotspot",
  features: Record<string, unknown>
): Promise<SHAPImpact[]> {
  const res = await axios.post<PredictionResponse<SHAPImpact[]>>(
    `${API_BASE}/api/v1/predictions/explain`,
    {
      prediction_type: predictionType,
      features,
    },
    { headers: getAuthHeaders() }
  );
  return res.data.data;
}
