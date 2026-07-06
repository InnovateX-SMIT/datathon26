export interface NetworkNodeMetadata {
  risk_score?: number;
  gender?: string;
  age?: number;
  status?: string;
  occupation?: string;
  caste?: string;
  crime_type?: string;
  crime_category?: string;
  crime_subcategory?: string;
  severity?: number;
  crime_date?: string;
  state?: string;
  district?: string;
  latitude?: number;
  longitude?: number;
  role?: string;
  [key: string]: unknown;
}

export interface NetworkNode {
  id: string;
  type: "criminal" | "crime" | "location" | string;
  label: string;
  metadata: NetworkNodeMetadata;
}

export interface NetworkEdge {
  source: string;
  target: string;
  relationship: string;
}

export interface NetworkGraphResponse {
  nodes: NetworkNode[];
  edges: NetworkEdge[];
  total_nodes: number;
  total_edges: number;
}


export interface NetworkCriminalSample {
  id: number;
  name: string;
  risk_score?: number | null;
  status?: string | null;
}

export interface NetworkCriminalSamplesResponse {
  dataset_id: number;
  criminals: NetworkCriminalSample[];
}
