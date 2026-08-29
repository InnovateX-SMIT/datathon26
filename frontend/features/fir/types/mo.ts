// ══════════════════════════════════════════════════════════════════════════════
// Modus Operandi & Behavioral Intelligence Types
// ══════════════════════════════════════════════════════════════════════════════

export interface MOAttributes {
  entry_method?: string | null;
  weapon_tool?: string | null;
  target_type?: string | null;
  time_pattern?: string | null;
  approach_method?: string | null;
  escape_method?: string | null;
  location_type?: string | null;
}

export interface AssociatedSuspect {
  accused_id: number;
  name: string;
  person_id?: string | null;
  age?: number | null;
  gender?: string | null;
}

export interface SimilarCaseMatch {
  case_id: number;
  crime_no?: string | null;
  case_no?: string | null;
  crime_type: string;
  district: string;
  police_station: string;
  registered_date?: string | null;
  similarity_score: number;
  similarity_percentage: number;
  is_cross_jurisdiction: boolean;
  matching_attributes: string[];
  associated_suspects: AssociatedSuspect[];
}

export interface MOProfileResponse {
  case_id: number;
  crime_no?: string | null;
  case_no?: string | null;
  crime_type: string;
  district?: string | null;
  police_station?: string | null;
  registered_date?: string | null;
  raw_narrative?: string | null;
  is_sufficient: boolean;
  mo_summary: string;
  attributes: MOAttributes;
  behavioral_tags: string[];
  associated_suspects: AssociatedSuspect[];
  similar_cases: SimilarCaseMatch[];
  interpretation_disclaimer: string;
}

export interface OffenderCaseSummary {
  case_id: number;
  crime_no?: string | null;
  crime_type: string;
  registered_date?: string | null;
  district?: string | null;
  police_station?: string | null;
  mo_summary: string;
  behavioral_tags: string[];
}

export interface OffenderBehavioralProfileResponse {
  accused_id: number;
  name: string;
  person_id?: string | null;
  total_associated_cases: number;
  has_sufficient_history: boolean;
  recurring_mo_signatures: string[];
  primary_crime_types: string[];
  primary_districts: string[];
  associated_cases: OffenderCaseSummary[];
  interpretation_disclaimer: string;
}

export interface CrossJurisdictionLink {
  source_case_id: number;
  source_crime_no?: string | null;
  source_district: string;
  target_case_id: number;
  target_crime_no?: string | null;
  target_district: string;
  crime_type: string;
  similarity_score: number;
  similarity_percentage: number;
  matching_attributes: string[];
}

export interface CrossJurisdictionSummary {
  total_cross_jurisdiction_patterns: number;
  jurisdiction_pairs: Array<{
    district_a: string;
    district_b: string;
    linked_cases_count: number;
    avg_similarity: number;
    max_similarity: number;
  }>;
  sample_links: CrossJurisdictionLink[];
}
