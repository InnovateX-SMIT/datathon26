"use client";

import React, { useEffect, useState, useMemo } from "react";
import { MapContainer, TileLayer, GeoJSON, CircleMarker, Tooltip, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import MapFullscreenPanel, { LeafletMapResizer } from "./MapFullscreenPanel";
import type { DistrictCrime } from "../types/geo";
import { fetchKarnatakaBoundaryGeoJson } from "../services/geoApi";

interface DistrictMapProps {
  data: DistrictCrime[];
  loading?: boolean;
  selectedDistrict?: string;
  onSelectDistrict?: (district: string) => void;
}

export default function DistrictMap({
  data,
  loading,
  selectedDistrict,
  onSelectDistrict,
}: DistrictMapProps) {
  const [geoJsonData, setGeoJsonData] = useState<any>(null);

  useEffect(() => {
    let active = true;
    fetchKarnatakaBoundaryGeoJson()
      .then((json) => {
        if (active && json && json.features) {
          setGeoJsonData(json);
        }
      })
      .catch((err) => {
        console.error("Failed to load Karnataka GeoJSON boundary:", err);
      });
    return () => {
      active = false;
    };
  }, []);

  const defaultZoom = 7;
  const defaultCenter: [number, number] = [15.3173, 75.7139]; // Centered on Karnataka State

  const maxCrime = useMemo(() => {
    if (!data || data.length === 0) return 1;
    return Math.max(...data.map((d) => d.crime_count), 1);
  }, [data]);

  const districtMapLookup = useMemo(() => {
    const map = new Map<string, DistrictCrime>();
    data.forEach((d) => {
      if (d.district) {
        map.set(d.district.toLowerCase().trim(), d);
      }
    });
    return map;
  }, [data]);

  const getDistrictColor = (crimeCount: number) => {
    if (crimeCount === 0) return "#1e293b";
    const ratio = crimeCount / maxCrime;
    if (ratio < 0.1) return "#312e81";
    if (ratio < 0.3) return "#4338ca";
    if (ratio < 0.5) return "#4f46e5";
    if (ratio < 0.75) return "#6366f1";
    if (ratio < 0.95) return "#818cf8";
    return "#a5b4fc";
  };

  const getMarkerRadius = (crimeCount: number) => {
    const ratio = crimeCount / maxCrime;
    return Math.max(8, Math.min(26, Math.round(10 + ratio * 16)));
  };

  return (
    <MapFullscreenPanel
      title={`District Crime Map (Real Boundary Overlay${selectedDistrict ? ` — Filtered: ${selectedDistrict}` : ""})`}
      loading={loading}
    >
      {(fullscreen) => {
        if (loading) {
          return (
            <div className="flex-1 bg-slate-800/10 rounded-xl flex items-center justify-center text-slate-500 text-xs animate-pulse font-sans">
              Loading Karnataka district geospatial intelligence...
            </div>
          );
        }

        if (data.length === 0 && !geoJsonData) {
          return (
            <div className="flex-1 rounded-xl border border-dashed border-slate-800/80 bg-slate-950/40 flex flex-col items-center justify-center text-center px-6">
              <h4 className="text-sm font-bold text-slate-300 uppercase tracking-wider font-sans">No District Data</h4>
              <p className="text-xs text-slate-500 mt-2 max-w-xs leading-relaxed font-sans">
                No district-level crime counts match the active filters.
              </p>
            </div>
          );
        }

        return (
<<<<<<< Updated upstream
          <div className="flex-1 rounded-xl overflow-hidden border border-slate-800/80 z-0 relative h-full min-h-[300px]">
            <MapContainer center={mapCenter} zoom={defaultZoom} style={{ height: "100%", width: "100%", background: "#0c1020" }} zoomControl>
              <LeafletMapResizer resizeKey={fullscreen ? "district-full" : "district-inline"} />
              <TileLayer url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>' />
              {data.map((item) => {
                if (!item.latitude || !item.longitude) return null;
                const boundary = generateDistrictPolygon(item.latitude, item.longitude);
                return (
                  <Polygon
                    key={item.district}
                    positions={boundary}
                    pathOptions={{ fillColor: getDistrictColor(item.crime_count), fillOpacity: 0.65, color: "#1e1b4b", weight: 1.5, dashArray: "3" }}
                    eventHandlers={{
                      mouseover: (e) => e.target.setStyle({ fillOpacity: 0.85, weight: 2, color: "#6366f1" }),
                      mouseout: (e) => e.target.setStyle({ fillOpacity: 0.65, weight: 1.5, color: "#1e1b4b" }),
                    }}
=======
          <div className="flex-1 flex flex-col h-full min-h-[340px]">
            {/* Quick Drill-down Action Toolbar */}
            {selectedDistrict && (
              <div className="mb-2 px-3 py-1.5 bg-indigo-950/40 border border-indigo-500/30 rounded-lg flex items-center justify-between text-xs text-indigo-300 font-sans">
                <span>
                  Drill-down active on: <strong className="text-indigo-200 uppercase">{selectedDistrict}</strong>
                </span>
                {onSelectDistrict && (
                  <button
                    onClick={() => onSelectDistrict("")}
                    className="text-[10px] uppercase font-bold text-indigo-400 hover:text-indigo-200 underline cursor-pointer"
>>>>>>> Stashed changes
                  >
                    View All Districts
                  </button>
                )}
              </div>
            )}

            <div className="flex-1 rounded-xl overflow-hidden border border-slate-800/80 z-0 relative h-full">
              <MapContainer
                center={defaultCenter}
                zoom={defaultZoom}
                style={{ height: "100%", width: "100%", background: "#0c1020" }}
                zoomControl
              >
                <LeafletMapResizer resizeKey={fullscreen ? "district-full" : "district-inline"} />
                <TileLayer
                  url="https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png"
                  attribution='&copy; <a href="https://stadiamaps.com/" target="_blank">Stadia Maps</a> &copy; <a href="https://www.stamen.com/" target="_blank">Stamen Design</a> &copy; <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> contributors'
                  maxZoom={18}
                />

                {/* Real Karnataka State & District Boundary GeoJSON */}
                {geoJsonData && (
                  <GeoJSON
                    data={geoJsonData}
                    style={() => ({
                      fillColor: "#4f46e5",
                      fillOpacity: 0.12,
                      color: "#6366f1",
                      weight: 1.8,
                      dashArray: "4 2",
                    })}
                  />
                )}

                {/* District Data Centroid Overlays & Interaction Points */}
                {data.map((item) => {
                  if (!item.latitude || !item.longitude) return null;
                  const isSelected = selectedDistrict && selectedDistrict.toLowerCase() === item.district.toLowerCase();
                  const radius = getMarkerRadius(item.crime_count);
                  const fillColor = getDistrictColor(item.crime_count);

                  return (
                    <CircleMarker
                      key={`district-marker-${item.district}`}
                      center={[item.latitude, item.longitude]}
                      radius={radius}
                      pathOptions={{
                        fillColor: fillColor,
                        fillOpacity: isSelected ? 0.95 : 0.75,
                        color: isSelected ? "#38bdf8" : "#818cf8",
                        weight: isSelected ? 3 : 1.5,
                      }}
                      eventHandlers={{
                        click: () => {
                          if (onSelectDistrict) {
                            onSelectDistrict(isSelected ? "" : item.district);
                          }
                        },
                      }}
                    >
                      <Tooltip sticky>
                        <div className="p-1 text-slate-100 bg-[#0f172a]/95 rounded border border-[#1e293b] font-sans text-xs">
                          <p className="font-bold text-indigo-400 uppercase tracking-wide">{item.district}</p>
                          <p className="mt-0.5">
                            Total Crimes: <span className="font-extrabold text-white">{item.crime_count.toLocaleString()}</span>
                          </p>
                          <p className="text-[9px] text-indigo-300 mt-1 italic">Click to drill down into this district</p>
                        </div>
                      </Tooltip>
                      <Popup>
                        <div className="p-2 text-slate-200 font-sans text-xs min-w-[150px]">
                          <h4 className="font-bold text-indigo-400 text-sm border-b border-slate-800 pb-1 mb-1 uppercase">
                            {item.district}
                          </h4>
                          <div className="space-y-1 mt-1.5">
                            <p>
                              Incident Volume:{" "}
                              <span className="font-bold text-slate-100">{item.crime_count.toLocaleString()}</span>
                            </p>
                            <p className="text-[10px] text-slate-400">
                              Lat: {item.latitude.toFixed(4)}, Lon: {item.longitude.toFixed(4)}
                            </p>
                            {onSelectDistrict && (
                              <button
                                onClick={() => onSelectDistrict(isSelected ? "" : item.district)}
                                className="w-full mt-2 py-1 px-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-[10px] uppercase rounded transition-all cursor-pointer text-center"
                              >
                                {isSelected ? "Reset District Filter" : "Drill Down to District"}
                              </button>
                            )}
                          </div>
                        </div>
                      </Popup>
                    </CircleMarker>
                  );
                })}
              </MapContainer>
            </div>
          </div>
        );
      }}
    </MapFullscreenPanel>
  );
}
