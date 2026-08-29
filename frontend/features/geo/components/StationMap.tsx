"use client";

import React, { useMemo } from "react";
import { MapContainer, TileLayer, Marker, Popup, Tooltip } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import MapFullscreenPanel, { LeafletMapResizer } from "./MapFullscreenPanel";
import type { StationCrime } from "../types/geo";

interface StationMapProps {
  data: StationCrime[];
  loading?: boolean;
  selectedStation?: string;
  onSelectStation?: (station: string) => void;
}

const createStationIcon = (isSelected: boolean) => {
  if (typeof window === "undefined") return null;
  const color = isSelected ? "bg-cyan-400" : "bg-blue-500";
  const pingColor = isSelected ? "bg-cyan-400/60" : "bg-blue-500/40";
  const border = isSelected ? "border-cyan-200 border-2" : "border-slate-950 border-2";

  return L.divIcon({
    html: `
      <div class="flex items-center justify-center relative w-7 h-7">
        <span class="absolute inline-flex w-6 h-6 rounded-full ${pingColor} animate-ping"></span>
        <div class="w-4 h-4 rounded-full ${color} ${border} shadow-lg"></div>
      </div>
    `,
    className: "custom-station-icon",
    iconSize: [28, 28],
    iconAnchor: [14, 14],
    popupAnchor: [0, -12]
  });
};

export default function StationMap({ data, loading, selectedStation, onSelectStation }: StationMapProps) {
  const defaultZoom = 9;

  const mapCenter = useMemo<[number, number]>(() => {
    const valid = data.filter((d) => d.latitude && d.longitude);
    if (valid.length === 0) return [15.0, 76.25];
    const latSum = valid.reduce((sum, p) => sum + p.latitude, 0);
    const lonSum = valid.reduce((sum, p) => sum + p.longitude, 0);
    return [latSum / valid.length, lonSum / valid.length];
  }, [data]);

  return (
    <MapFullscreenPanel
      title={`Police Station Map (Precinct Distribution${selectedStation ? ` — Selected: ${selectedStation}` : ""})`}
      loading={loading}
    >
      {(fullscreen) => {
        if (loading) {
          return (
            <div className="flex-1 bg-slate-800/10 rounded-xl flex items-center justify-center text-slate-500 text-xs animate-pulse font-sans">
              Loading police stations distribution...
            </div>
          );
        }

        if (data.length === 0) {
          return (
            <div className="flex-1 rounded-xl border border-dashed border-slate-800/80 bg-slate-950/40 flex flex-col items-center justify-center text-center px-6">
              <h4 className="text-sm font-bold text-slate-300 uppercase tracking-wider font-sans">No Station Data</h4>
              <p className="text-xs text-slate-500 mt-2 max-w-xs leading-relaxed font-sans">
                No police station activity matches the active filters.
              </p>
            </div>
          );
        }

        return (
          <div className="flex-1 flex flex-col h-full min-h-[340px]">
            {selectedStation && (
              <div className="mb-2 px-3 py-1.5 bg-blue-950/40 border border-blue-500/30 rounded-lg flex items-center justify-between text-xs text-blue-300 font-sans">
                <span>
                  Drill-down active on Station: <strong className="text-blue-200 uppercase">{selectedStation}</strong>
                </span>
                {onSelectStation && (
                  <button
                    onClick={() => onSelectStation("")}
                    className="text-[10px] uppercase font-bold text-blue-400 hover:text-blue-200 underline cursor-pointer"
                  >
                    View All Stations
                  </button>
                )}
              </div>
            )}

            <div className="flex-1 rounded-xl overflow-hidden border border-slate-800/80 z-0 relative h-full">
              <MapContainer
                center={mapCenter}
                zoom={defaultZoom}
                style={{ height: "100%", width: "100%", background: "#0c1020" }}
                zoomControl
              >
                <LeafletMapResizer resizeKey={fullscreen ? "station-full" : "station-inline"} />
                <TileLayer
                  url="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}"
                  attribution='&copy; <a href="https://www.esri.com/" target="_blank">Esri</a>, HERE, Garmin, NGA, EPA'
                  maxZoom={16}
                />
                <TileLayer
                  url="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}"
                  maxZoom={16}
                />
                {data.map((station, idx) => {
                  if (!station.latitude || !station.longitude) return null;
                  const isSelected = selectedStation && selectedStation.toLowerCase() === station.station.toLowerCase();
                  const icon = createStationIcon(Boolean(isSelected));

                  return (
                    <Marker
                      key={`${station.station}-${idx}`}
                      position={[station.latitude, station.longitude]}
                      icon={icon || undefined}
                      eventHandlers={{
                        click: () => {
                          if (onSelectStation) {
                            onSelectStation(isSelected ? "" : station.station);
                          }
                        },
                      }}
                    >
                      <Tooltip sticky>
                        <div className="p-1 text-slate-100 bg-[#0f172a]/95 rounded border border-[#1e293b] font-sans text-xs">
                          <p className="font-bold text-blue-400 uppercase tracking-wide">{station.station}</p>
                          <p className="mt-0.5">
                            Station Crimes: <span className="font-extrabold text-white">{station.crime_count.toLocaleString()}</span>
                          </p>
                        </div>
                      </Tooltip>
                      <Popup>
                        <div className="p-2 text-slate-200 font-sans text-xs min-w-[150px]">
                          <h4 className="font-bold text-blue-400 text-sm border-b border-slate-800 pb-1 mb-1 uppercase">
                            {station.station}
                          </h4>
                          <div className="space-y-1 mt-1.5">
                            <p>
                              Station Crimes:{" "}
                              <span className="font-bold text-slate-100">{station.crime_count.toLocaleString()}</span>
                            </p>
                            <p className="text-[10px] text-slate-400">
                              Lat: {station.latitude.toFixed(4)}, Lon: {station.longitude.toFixed(4)}
                            </p>
                            {onSelectStation && (
                              <button
                                onClick={() => onSelectStation(isSelected ? "" : station.station)}
                                className="w-full mt-2 py-1 px-2 bg-blue-600 hover:bg-blue-500 text-white font-bold text-[10px] uppercase rounded transition-all cursor-pointer text-center"
                              >
                                {isSelected ? "Reset Station Filter" : "Filter by this Station"}
                              </button>
                            )}
                          </div>
                        </div>
                      </Popup>
                    </Marker>
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
