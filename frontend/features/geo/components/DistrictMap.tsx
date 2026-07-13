"use client";

import React from "react";
import { MapContainer, TileLayer, Polygon, Tooltip } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import MapFullscreenPanel, { LeafletMapResizer } from "./MapFullscreenPanel";
import type { DistrictCrime } from "../types/geo";

interface DistrictMapProps {
  data: DistrictCrime[];
  loading?: boolean;
}

const generateDistrictPolygon = (lat: number, lon: number, r: number = 0.012) => {
  const points = [];
  const seed = Math.sin(lat) * Math.cos(lon);
  for (let i = 0; i < 8; i++) {
    const angle = (i * Math.PI) / 4;
    const noise = 0.85 + 0.3 * Math.sin(i * 3 + seed * 10) * Math.cos(i * 2 + seed * 5);
    const radius = r * noise;
    points.push([lat + radius * Math.sin(angle), lon + radius * Math.cos(angle)] as [number, number]);
  }
  return points;
};

export default function DistrictMap({ data, loading }: DistrictMapProps) {
  const defaultZoom = 10;

  const mapCenter = React.useMemo<[number, number]>(() => {
    const validPoints = data.filter((d) => d.latitude && d.longitude);
    if (validPoints.length === 0) return [15.0, 76.25];
    const latSum = validPoints.reduce((sum, p) => sum + p.latitude, 0);
    const lonSum = validPoints.reduce((sum, p) => sum + p.longitude, 0);
    return [latSum / validPoints.length, lonSum / validPoints.length];
  }, [data]);

  const maxCrime = React.useMemo(() => {
    if (data.length === 0) return 1;
    return Math.max(...data.map((d) => d.crime_count), 1);
  }, [data]);

  const getDistrictColor = (crimeCount: number) => {
    if (crimeCount === 0) return "#1e293b";
    const ratio = crimeCount / maxCrime;
    if (ratio < 0.1) return "#1e1b4b";
    if (ratio < 0.3) return "#312e81";
    if (ratio < 0.5) return "#4338ca";
    if (ratio < 0.75) return "#4f46e5";
    if (ratio < 0.95) return "#6366f1";
    return "#818cf8";
  };

  return (
    <MapFullscreenPanel title="District Crime Map (Choropleth Overlay)" loading={loading}>
      {(fullscreen) => {
        if (loading) {
          return <div className="flex-1 bg-slate-800/10 rounded-xl flex items-center justify-center text-slate-500 text-xs animate-pulse">Loading district crime distribution...</div>;
        }

        if (data.length === 0) {
          return (
            <div className="flex-1 rounded-xl border border-dashed border-slate-800/80 bg-slate-950/40 flex flex-col items-center justify-center text-center px-6">
              <h4 className="text-sm font-bold text-slate-300 uppercase tracking-wider">No District Data</h4>
              <p className="text-xs text-slate-500 mt-2 max-w-xs leading-relaxed">No district-level crime counts match the active filters.</p>
            </div>
          );
        }

        return (
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
                  >
                    <Tooltip sticky>
                      <div className="p-1 text-slate-100 bg-[#0f172a]/95 rounded border border-[#1e293b] font-sans text-xs">
                        <p className="font-bold text-indigo-400">{item.district}</p>
                        <p className="mt-0.5">Crime Count: <span className="font-extrabold">{item.crime_count.toLocaleString()}</span></p>
                      </div>
                    </Tooltip>
                  </Polygon>
                );
              })}
            </MapContainer>
          </div>
        );
      }}
    </MapFullscreenPanel>
  );
}
