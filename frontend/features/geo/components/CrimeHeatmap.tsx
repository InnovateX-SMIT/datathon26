"use client";

import React from "react";
import { MapContainer, TileLayer, Circle, Tooltip } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import type { HeatmapPoint } from "../types/geo";

interface CrimeHeatmapProps {
  data: HeatmapPoint[];
  loading?: boolean;
}

export default function CrimeHeatmap({ data, loading }: CrimeHeatmapProps) {
  const mapCenter: [number, number] = [15.0, 76.25];
  const defaultZoom = 10;

  const maxWeight = React.useMemo(() => {
    if (data.length === 0) return 1;
    return Math.max(...data.map((p) => p.weight), 1);
  }, [data]);

  const getHeatColor = (weight: number) => {
    const ratio = weight / maxWeight;
    if (ratio > 0.8) return "#f43f5e"; // Rose
    if (ratio > 0.5) return "#f97316"; // Orange
    if (ratio > 0.2) return "#eab308"; // Yellow
    return "#10b981"; // Emerald
  };

  const getRadiusMeters = (weight: number) => {
    const ratio = weight / maxWeight;
    // Base radius 800m, up to 4000m for extreme hotspots
    return 800 + ratio * 3200;
  };

  const renderHeader = () => (
    <div className="flex items-center gap-2 mb-4">
      <div className="w-1.5 h-5 bg-indigo-500 rounded" />
      <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
        Crime Density Heatmap (Intensity Density Grid)
      </h3>
    </div>
  );

  if (loading) {
    return (
      <div className="glass-card p-6 rounded-2xl border border-slate-800/60 h-[450px] flex flex-col mb-6 animate-pulse">
        {renderHeader()}
        <div className="flex-1 bg-slate-800/10 rounded-xl flex items-center justify-center text-slate-500 text-xs">
          Loading crime heatmap data...
        </div>
      </div>
    );
  }

  return (
    <div className="glass-card p-6 rounded-2xl border border-slate-800/60 h-[450px] flex flex-col mb-6 relative overflow-hidden bg-slate-950/40">
      {renderHeader()}
      <div className="flex-1 rounded-xl overflow-hidden border border-slate-800/80 z-0 relative h-full min-h-[300px]">
        <MapContainer
          center={mapCenter}
          zoom={defaultZoom}
          style={{ height: "100%", width: "100%", background: "#0c1020" }}
          zoomControl={true}
        >
          <TileLayer
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          />

          {data.map((point, idx) => {
            const fillColor = getHeatColor(point.weight);
            const radius = getRadiusMeters(point.weight);

            return (
              <React.Fragment key={`heat-${idx}`}>
                {/* Outer halo for soft glow */}
                <Circle
                  center={[point.latitude, point.longitude]}
                  radius={radius * 1.5}
                  pathOptions={{
                    fillColor: fillColor,
                    fillOpacity: 0.1,
                    stroke: false,
                  }}
                  interactive={false}
                />
                
                {/* Core density circle */}
                <Circle
                  center={[point.latitude, point.longitude]}
                  radius={radius}
                  pathOptions={{
                    fillColor: fillColor,
                    fillOpacity: 0.35,
                    color: fillColor,
                    weight: 1.5,
                    opacity: 0.6,
                  }}
                >
                  <Tooltip sticky>
                    <div className="p-1.5 text-slate-100 bg-[#0f172a]/95 rounded border border-[#1e293b] font-sans text-xs">
                      <p className="font-bold text-slate-300">Density Cluster</p>
                      <p className="mt-0.5">
                        Incidents: <span className="font-extrabold text-rose-400">{point.weight.toLocaleString()}</span>
                      </p>
                      <p className="text-[10px] text-slate-400">
                        Intensity: {Math.round((point.weight / maxWeight) * 100)}%
                      </p>
                    </div>
                  </Tooltip>
                </Circle>
              </React.Fragment>
            );
          })}
        </MapContainer>
      </div>
    </div>
  );
}
