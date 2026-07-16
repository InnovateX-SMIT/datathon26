"use client";

import React from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import MapFullscreenPanel, { LeafletMapResizer } from "./MapFullscreenPanel";
import type { GeoMarker } from "../types/geo";

interface FirMarkerMapProps {
  data: GeoMarker[];
  loading?: boolean;
}

const createSingleIcon = (status: string) => {
  if (typeof window === "undefined") return null;
  const lower = status.toLowerCase();
  let color = "bg-indigo-500";
  let ring = "bg-indigo-500/40";
  if (lower.includes("closed")) {
    color = "bg-emerald-500";
    ring = "bg-emerald-500/40";
  } else if (lower.includes("investigation") || lower.includes("pending")) {
    color = "bg-amber-500";
    ring = "bg-amber-500/40";
  } else if (lower.includes("chargesheet") || lower.includes("filed")) {
    color = "bg-cyan-500";
    ring = "bg-cyan-500/40";
  }

  return L.divIcon({
    html: `
      <div class="flex items-center justify-center relative w-6 h-6">
        <span class="absolute inline-flex w-5 h-5 rounded-full ${ring} animate-ping"></span>
        <div class="w-3.5 h-3.5 rounded-full ${color} border-2 border-slate-950 shadow-md"></div>
      </div>
    `,
    className: "custom-fir-icon",
    iconSize: [24, 24],
    iconAnchor: [12, 12],
    popupAnchor: [0, -10]
  });
};

const createClusterIcon = (count: number) => {
  if (typeof window === "undefined") return null;
  const size = count < 10 ? 32 : count < 50 ? 40 : 48;
  return L.divIcon({
    html: `
      <div class="flex items-center justify-center rounded-full bg-indigo-650/45 border border-indigo-500/50 text-indigo-300 font-black text-xs shadow-xl font-sans" style="width: ${size}px; height: ${size}px;">
        ${count}
      </div>
    `,
    className: "custom-cluster-icon",
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
    popupAnchor: [0, -size / 2]
  });
};

export default function FirMarkerMap({ data, loading }: FirMarkerMapProps) {
  const defaultZoom = 10;

  const mapCenter = React.useMemo<[number, number]>(() => {
    const validPoints = data.filter((m) => m.latitude && m.longitude);
    if (validPoints.length === 0) return [15.0, 76.25];
    const latSum = validPoints.reduce((sum, p) => sum + p.latitude, 0);
    const lonSum = validPoints.reduce((sum, p) => sum + p.longitude, 0);
    return [latSum / validPoints.length, lonSum / validPoints.length];
  }, [data]);

  // Client-side grid clustering (epsilon = 0.04 degrees) to avoid performance lag
  const clusters = React.useMemo(() => {
    const results: Array<{
      id: string;
      latitude: number;
      longitude: number;
      markers: GeoMarker[];
    }> = [];
    const eps = 0.04;

    data.forEach((marker) => {
      if (!marker.latitude || !marker.longitude) return;
      let matched = false;
      for (const cluster of results) {
        const dist = Math.sqrt(
          Math.pow(cluster.latitude - marker.latitude, 2) +
          Math.pow(cluster.longitude - marker.longitude, 2)
        );
        if (dist < eps) {
          cluster.markers.push(marker);
          // Re-calculate cluster centroid
          cluster.latitude = (cluster.latitude * (cluster.markers.length - 1) + marker.latitude) / cluster.markers.length;
          cluster.longitude = (cluster.longitude * (cluster.markers.length - 1) + marker.longitude) / cluster.markers.length;
          matched = true;
          break;
        }
      }
      if (!matched) {
        results.push({
          id: `cluster-${marker.id}`,
          latitude: marker.latitude,
          longitude: marker.longitude,
          markers: [marker]
        });
      }
    });

    return results;
  }, [data]);

  const formatDate = (dateStr: string) => {
    if (!dateStr) return "N/A";
    try {
      return new Date(dateStr).toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric"
      });
    } catch {
      return dateStr;
    }
  };

  const getStatusBadgeClass = (status: string) => {
    const lower = status.toLowerCase();
    if (lower.includes("closed")) return "bg-green-500/20 text-green-400 border border-green-500/30";
    if (lower.includes("investigation") || lower.includes("pending")) return "bg-amber-500/20 text-amber-400 border border-amber-500/30";
    if (lower.includes("chargesheet") || lower.includes("filed")) return "bg-cyan-500/20 text-cyan-400 border border-cyan-500/30";
    return "bg-slate-555/20 text-slate-400 border border-slate-500/30";
  };

  return (
    <MapFullscreenPanel title="Incident Marker Map (Operational GIS)" loading={loading}>
      {(fullscreen) => {
        if (loading) {
          return <div className="flex-1 bg-slate-800/10 rounded-xl flex items-center justify-center text-slate-500 text-xs animate-pulse">Loading incident markers...</div>;
        }

        if (data.length === 0) {
          return (
            <div className="flex-1 rounded-xl border border-dashed border-slate-800/80 bg-slate-950/40 flex flex-col items-center justify-center text-center px-6">
              <h4 className="text-sm font-bold text-slate-300 uppercase tracking-wider">No Incident Markers</h4>
              <p className="text-xs text-slate-500 mt-2 max-w-xs leading-relaxed">No incidents match the active filters or contain coordinates.</p>
            </div>
          );
        }

        return (
          <div className="flex-1 rounded-xl overflow-hidden border border-slate-800/80 z-0 relative h-full min-h-[300px]">
            <MapContainer center={mapCenter} zoom={defaultZoom} style={{ height: "100%", width: "100%", background: "#0c1020" }} zoomControl>
              <LeafletMapResizer resizeKey={fullscreen ? "marker-full" : "marker-inline"} />
              <TileLayer url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>' />
              {clusters.map((cluster) => {
                if (cluster.markers.length === 1) {
                  const m = cluster.markers[0];
                  const singleIcon = createSingleIcon(m.status);
                  return (
                    <Marker key={m.id} position={[m.latitude, m.longitude]} icon={singleIcon || undefined}>
                      <Popup>
                        <div className="p-2 text-slate-200 font-sans text-xs min-w-[200px] max-w-[240px]">
                          <h4 className="font-extrabold text-indigo-400 text-xs border-b border-slate-800 pb-1 mb-2 tracking-tight">FIR: {m.crime_no}</h4>
                          <table className="w-full text-left border-collapse space-y-1">
                            <tbody>
                              <tr>
                                <td className="text-slate-500 text-[10px] uppercase font-bold py-0.5">Crime Type</td>
                                <td className="font-semibold text-slate-200 py-0.5 uppercase text-[10px] tracking-tight">{m.crime_type}</td>
                              </tr>
                              <tr>
                                <td className="text-slate-500 text-[10px] uppercase font-bold py-0.5">Station</td>
                                <td className="text-slate-300 py-0.5">{m.police_station}</td>
                              </tr>
                              <tr>
                                <td className="text-slate-500 text-[10px] uppercase font-bold py-0.5">District</td>
                                <td className="text-slate-300 py-0.5">{m.district}</td>
                              </tr>
                              <tr>
                                <td className="text-slate-500 text-[10px] uppercase font-bold py-0.5">Date</td>
                                <td className="text-slate-300 font-mono py-0.5">{formatDate(m.crime_date)}</td>
                              </tr>
                              <tr>
                                <td className="text-slate-500 text-[10px] uppercase font-bold py-0.5">Status</td>
                                <td className="py-0.5">
                                  <span className={`inline-flex px-1.5 py-0.5 rounded-full text-[9px] font-black uppercase tracking-wider ${getStatusBadgeClass(m.status)}`}>
                                    {m.status}
                                  </span>
                                </td>
                              </tr>
                            </tbody>
                          </table>
                        </div>
                      </Popup>
                    </Marker>
                  );
                } else {
                  const icon = createClusterIcon(cluster.markers.length);
                  return (
                    <Marker key={cluster.id} position={[cluster.latitude, cluster.longitude]} icon={icon || undefined}>
                      <Popup>
                        <div className="p-2 text-slate-200 font-sans text-xs min-w-[220px] max-w-[260px]">
                          <h4 className="font-extrabold text-indigo-400 text-xs border-b border-slate-800 pb-1.5 mb-1.5">
                            Cluster: {cluster.markers.length} Incidents
                          </h4>
                          <div className="max-h-[160px] overflow-y-auto space-y-1.5 pr-1 divide-y divide-slate-800/60">
                            {cluster.markers.map((m) => (
                              <div key={m.id} className="pt-1.5 first:pt-0">
                                <p className="font-bold text-[10px] text-slate-100">{m.crime_no}</p>
                                <p className="text-[9px] text-slate-400 uppercase tracking-tight">{m.crime_type} | {m.police_station}</p>
                                <span className={`inline-flex px-1 py-0.5 rounded text-[8px] font-bold uppercase mt-1 ${getStatusBadgeClass(m.status)}`}>
                                  {m.status}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      </Popup>
                    </Marker>
                  );
                }
              })}
            </MapContainer>
          </div>
        );
      }}
    </MapFullscreenPanel>
  );
}
