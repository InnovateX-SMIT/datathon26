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

export interface GeoFiltersState {
  district?: string;
  crime_type?: string;
  start_date?: string;
  end_date?: string;
}

export interface GeoIntelligenceResponse {
  districts: DistrictCrime[];
  stations: StationCrime[];
  heatmap: HeatmapPoint[];
  hotspots: HotspotCluster[];
  markers: GeoMarker[];
}
