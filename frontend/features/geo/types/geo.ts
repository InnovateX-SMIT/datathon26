export interface DistrictCrime {
  district: string;
  crime_count: number;
  latitude: number;
  longitude: number;
}

export interface StationCrime {
  station: string;
  crime_count: number;
  latitude: number;
  longitude: number;
}

export interface HeatmapPoint {
  latitude: number;
  longitude: number;
  weight: number;
}

export interface HotspotCluster {
  cluster_id: number;
  crime_count: number;
  latitude: number;
  longitude: number;
  first_incident_date?: string;
  last_incident_date?: string;
  peak_hour_window?: string;
  temporal_category?: string;
  hotspot_type?: string;
}

export interface GeoMarker {
  id: number;
  crime_no: string;
  crime_type: string;
  police_station: string;
  district: string;
  crime_date: string;
  status: string;
  latitude: number;
  longitude: number;
}

export interface HourlyDataPoint {
  hour: number;
  label: string;
  count: number;
}

export interface TimePeriodDistribution {
  morning: number;
  afternoon: number;
  evening: number;
  night: number;
}

export interface TimeOfDayCategoryBreakdown {
  period: string;
  top_categories: { category: string; count: number }[];
}

export interface TimeOfDayResponse {
  hourly: HourlyDataPoint[];
  periods: TimePeriodDistribution;
  category_by_time: TimeOfDayCategoryBreakdown[];
  peak_hour?: string;
  peak_period?: string;
  total_analyzed: number;
}

export interface GeoFiltersState {
  district?: string;
  police_station?: string;
  crime_type?: string;
  start_date?: string;
  end_date?: string;
<<<<<<< Updated upstream
=======
  time_period?: string;
  /** Minimum crime count per hotspot cluster (controls DBSCAN min_samples sensitivity) */
  min_crime_count?: number;
>>>>>>> Stashed changes
}

export interface GeoLookupOptions {
  districts: string[];
  categories: string[];
  stations: string[];
  stations_by_district: Record<string, string[]>;
}

export interface GeoIntelligenceResponse {
  districts: DistrictCrime[];
  stations: StationCrime[];
  heatmap: HeatmapPoint[];
  hotspots: HotspotCluster[];
  markers: GeoMarker[];
  time_of_day?: TimeOfDayResponse;
}
