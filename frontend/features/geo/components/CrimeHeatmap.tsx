"use client";

import React from "react";
import { MapContainer, TileLayer, Circle, Tooltip } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import MapFullscreenPanel, { LeafletMapResizer } from "./MapFullscreenPanel";
import type { HeatmapPoint } from "../types/geo";

interface CrimeHeatmapProps {
  data: HeatmapPoint[];
  loading?: boolean;
}

export default function CrimeHeatmap({ data, loading }: CrimeHeatmapProps) {
  const defaultZoom = 10;

  const mapCenter = React.useMemo<[number, number]>(() => {
    const validPoints = data.filter((p) => p.latitude && p.longitude);
    if (validPoints.length === 0) return [15.0, 76.25];
    const latSum = validPoints.reduce((sum, p) => sum + p.latitude, 0);
    const lonSum = validPoints.reduce((sum, p) => sum + p.longitude, 0);
    return [latSum / validPoints.length, lonSum / validPoints.length];
  }, [data]);

  const maxWeight = React.useMemo(() => {
    if (data.length === 0) return 1;
    return Math.max(...data.map((p) => p.weight), 1);
  }, [data]);

  const getHeatColor = (weight: number) => {
    const ratio = weight / maxWeight;
    if (ratio > 0.8) return "#f43f5e";
    if (ratio > 0.5) return "#f97316";
    if (ratio > 0.2) return "#eab308";
    return "#10b981";
  };

  const getRadiusMeters = (weight: number) => 800 + (weight / maxWeight) * 3200;

  return (
    <MapFullscreenPanel title="Crime Density Heatmap (Intensity Density Grid)" loading={loading}>
      {(fullscreen) => {
        if (loading) {
          return <div className="flex-1 bg-slate-800/10 rounded-xl flex items-center justify-center text-slate-500 text-xs animate-pulse">Loading crime heatmap data...</div>;
        }

        if (data.length === 0) {
          return (
            <div className="flex-1 rounded-xl border border-dashed border-slate-800/80 bg-slate-950/40 flex flex-col items-center justify-center text-center px-6">
              <h4 className="text-sm font-bold text-slate-300 uppercase tracking-wider">No Heatmap Data</h4>
              <p className="text-xs text-slate-500 mt-2 max-w-xs leading-relaxed">No density points are available for the active filters.</p>
            </div>
          );
        }

        return (
          <div className="flex-1 rounded-xl overflow-hidden border border-slate-800/80 z-0 relative h-full min-h-[300px]">
            <MapContainer center={mapCenter} zoom={defaultZoom} style={{ height: "100%", width: "100%", background: "#0c1020" }} zoomControl>
              <LeafletMapResizer resizeKey={fullscreen ? "heatmap-full" : "heatmap-inline"} />
              <TileLayer url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>' />
              {data.map((point, idx) => {
                const fillColor = getHeatColor(point.weight);
                const radius = getRadiusMeters(point.weight);
                return (
                  <React.Fragment key={`heat-${idx}`}>
                    <Circle center={[point.latitude, point.longitude]} radius={radius * 1.5} pathOptions={{ fillColor, fillOpacity: 0.1, stroke: false }} interactive={false} />
                    <Circle center={[point.latitude, point.longitude]} radius={radius} pathOptions={{ fillColor, fillOpacity: 0.35, color: fillColor, weight: 1.5, opacity: 0.6 }}>
                      <Tooltip sticky>
                        <div className="p-1.5 text-slate-100 bg-[#0f172a]/95 rounded border border-[#1e293b] font-sans text-xs">
                          <p className="font-bold text-slate-300">Density Cluster</p>
                          <p className="mt-0.5">Incidents: <span className="font-extrabold text-rose-400">{point.weight.toLocaleString()}</span></p>
                          <p className="text-[10px] text-slate-400">Intensity: {Math.round((point.weight / maxWeight) * 100)}%</p>
                        </div>
                      </Tooltip>
                    </Circle>
                  </React.Fragment>
                );
              })}
            </MapContainer>
          </div>
        );
      }}
    </MapFullscreenPanel>
  );
}
