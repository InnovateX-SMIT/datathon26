"use client";

import React from "react";
import { MapContainer, TileLayer, Marker, Popup, Circle } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import type { HotspotCluster } from "../types/geo";

interface HotspotMapProps {
  data: HotspotCluster[];
  loading?: boolean;
}

// Custom pulsing neon warning icon for DBSCAN hotspots
const createHotspotIcon = (clusterId: number) => {
  if (typeof window === "undefined") return null;

  return L.divIcon({
    html: `
      <div class="flex items-center justify-center relative w-10 h-10">
        <span class="absolute inline-flex w-8 h-8 rounded-full bg-[#ef4444]/35 animate-ping"></span>
        <span class="absolute inline-flex w-10 h-10 rounded-full bg-[#ef4444]/15 animate-pulse"></span>
        <div class="w-6 h-6 rounded-full bg-[#ef4444] border border-slate-950 shadow-lg flex items-center justify-center text-[10px] text-white font-black">
          H${clusterId}
        </div>
      </div>
    `,
    className: "custom-hotspot-icon",
    iconSize: [40, 40],
    iconAnchor: [20, 20],
    popupAnchor: [0, -15]
  });
};

export default function HotspotMap({ data, loading }: HotspotMapProps) {
  const mapCenter: [number, number] = [15.0, 76.25];
  const defaultZoom = 10;

  const renderHeader = () => (
    <div className="flex items-center gap-2 mb-4">
      <div className="w-1.5 h-5 bg-indigo-500 rounded" />
      <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
        DBSCAN Crime Hotspots (Algorithmic Detections)
      </h3>
    </div>
  );

  if (loading) {
    return (
      <div className="glass-card p-6 rounded-2xl border border-slate-800/60 h-[450px] flex flex-col mb-6 animate-pulse">
        {renderHeader()}
        <div className="flex-1 bg-slate-800/10 rounded-xl flex items-center justify-center text-slate-500 text-xs">
          Loading algorithmic hotspots...
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

          {data.map((cluster) => {
            const icon = createHotspotIcon(cluster.cluster_id);
            
            return (
              <React.Fragment key={`hotspot-${cluster.cluster_id}`}>
                {/* Warning zone circle */}
                <Circle
                  center={[cluster.latitude, cluster.longitude]}
                  radius={2000} // 2km radius hotspot zone
                  pathOptions={{
                    fillColor: "#ef4444",
                    fillOpacity: 0.12,
                    color: "#ef4444",
                    weight: 1,
                    dashArray: "4 4",
                  }}
                />

                <Marker
                  position={[cluster.latitude, cluster.longitude]}
                  icon={icon || undefined}
                >
                  <Popup>
                    <div className="p-2 text-slate-200 font-sans text-xs min-w-[140px]">
                      <h4 className="font-bold text-[#ef4444] text-sm border-b border-slate-800 pb-1 mb-1">
                        Hotspot Zone H{cluster.cluster_id}
                      </h4>
                      <div className="space-y-1 mt-2">
                        <p>
                          Incident Density: <span className="font-bold text-slate-100">{cluster.crime_count.toLocaleString()}</span>
                        </p>
                        <p className="text-[10px] text-slate-400">
                          Centroid: {cluster.latitude.toFixed(4)}, {cluster.longitude.toFixed(4)}
                        </p>
                        <div className="py-1 px-2 bg-rose-500/10 border border-rose-500/20 text-[#ef4444] text-[9px] uppercase tracking-wider rounded font-bold mt-1 text-center">
                          High Density Risk Area
                        </div>
                      </div>
                    </div>
                  </Popup>
                </Marker>
              </React.Fragment>
            );
          })}
        </MapContainer>
      </div>
    </div>
  );
}
