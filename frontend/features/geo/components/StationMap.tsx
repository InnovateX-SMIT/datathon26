"use client";

import React from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import MapFullscreenPanel, { LeafletMapResizer } from "./MapFullscreenPanel";
import type { StationCrime } from "../types/geo";

interface StationMapProps {
  data: StationCrime[];
  loading?: boolean;
}

const createStationIcon = () => {
  if (typeof window === "undefined") return null;
  return L.divIcon({
    html: `
      <div class="flex items-center justify-center relative w-6 h-6">
        <span class="absolute inline-flex w-5 h-5 rounded-full bg-blue-500/40 animate-ping"></span>
        <div class="w-3.5 h-3.5 rounded-full bg-blue-500 border-2 border-slate-950 shadow-md"></div>
      </div>
    `,
    className: "custom-station-icon",
    iconSize: [24, 24],
    iconAnchor: [12, 12],
    popupAnchor: [0, -10]
  });
};

export default function StationMap({ data, loading }: StationMapProps) {
  const mapCenter: [number, number] = [15.0, 76.25];
  const defaultZoom = 10;
  const stationIcon = React.useMemo(() => createStationIcon(), []);

  return (
    <MapFullscreenPanel title="Police Station Map (Precinct Distributions)" loading={loading}>
      {(fullscreen) => {
        if (loading) {
          return <div className="flex-1 bg-slate-800/10 rounded-xl flex items-center justify-center text-slate-500 text-xs animate-pulse">Loading police stations distribution...</div>;
        }

        if (data.length === 0) {
          return (
            <div className="flex-1 rounded-xl border border-dashed border-slate-800/80 bg-slate-950/40 flex flex-col items-center justify-center text-center px-6">
              <h4 className="text-sm font-bold text-slate-300 uppercase tracking-wider">No Station Data</h4>
              <p className="text-xs text-slate-500 mt-2 max-w-xs leading-relaxed">No police station activity matches the active filters.</p>
            </div>
          );
        }

        return (
          <div className="flex-1 rounded-xl overflow-hidden border border-slate-800/80 z-0 relative h-full min-h-[300px]">
            <MapContainer center={mapCenter} zoom={defaultZoom} style={{ height: "100%", width: "100%", background: "#0c1020" }} zoomControl>
              <LeafletMapResizer resizeKey={fullscreen ? "station-full" : "station-inline"} />
              <TileLayer url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>' />
              {data.map((station, idx) => {
                if (!station.latitude || !station.longitude) return null;
                return (
                  <Marker key={`${station.station}-${idx}`} position={[station.latitude, station.longitude]} icon={stationIcon || undefined}>
                    <Popup>
                      <div className="p-2 text-slate-200 font-sans text-xs min-w-[120px]">
                        <h4 className="font-bold text-blue-400 text-sm border-b border-slate-800 pb-1 mb-1">{station.station}</h4>
                        <div className="space-y-0.5 mt-1.5">
                          <p>Total Crimes: <span className="font-bold text-slate-100">{station.crime_count.toLocaleString()}</span></p>
                          <p className="text-[10px] text-slate-400">Coord: {station.latitude.toFixed(4)}, {station.longitude.toFixed(4)}</p>
                        </div>
                      </div>
                    </Popup>
                  </Marker>
                );
              })}
            </MapContainer>
          </div>
        );
      }}
    </MapFullscreenPanel>
  );
}
