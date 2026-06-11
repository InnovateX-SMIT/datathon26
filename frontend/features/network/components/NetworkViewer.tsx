import React from "react";
import { Network, Activity, HelpCircle } from "lucide-react";
import NetworkSearch from "./NetworkSearch";
import NetworkStatistics from "./NetworkStatistics";
import NetworkLegend from "@/components/graphs/NetworkLegend";
import CriminalNetworkGraph from "@/components/graphs/CriminalNetworkGraph";
import { useNetworkGraph } from "../hooks/useNetworkGraph";

export default function NetworkViewer() {
  const {
    nodes,
    edges,
    onNodesChange,
    onEdgesChange,
    loading,
    error,
    loadNetwork,
    statistics,
  } = useNetworkGraph();

  const handleSearch = (criminalId: number) => {
    loadNetwork(criminalId);
  };

  const hasGraphData = nodes.length > 0;

  return (
    <div className="min-h-screen py-8 px-4 sm:px-6 lg:px-8 space-y-8 animate-fade-in relative">
      {/* Background ambient lighting glows */}
      <div className="absolute top-[20%] right-[10%] w-[400px] h-[400px] rounded-full bg-blue-500/5 blur-[100px] pointer-events-none" />
      <div className="absolute bottom-[20%] left-[5%] w-[350px] h-[350px] rounded-full bg-emerald-500/5 blur-[90px] pointer-events-none" />

      {/* 1. Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-900 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-blue-500/10 border border-blue-500/20 rounded-2xl">
              <Network className="w-6 h-6 text-blue-400" />
            </div>
            <div>
              <h1 className="text-3xl font-black text-slate-100 uppercase tracking-tight">
                Network Intelligence
              </h1>
              <p className="text-slate-400 text-xs font-semibold uppercase tracking-widest mt-1">
                Criminal Link & Association Analyzer
              </p>
            </div>
          </div>
          <p className="text-slate-400 text-sm mt-3 max-w-2xl leading-relaxed">
            Analyze linkages between suspects, incident files, and coordinate zones. Map organizational structure visually and trace connections dynamically using graph mapping algorithms.
          </p>
        </div>

        {/* Engine status indicator */}
        <div className="flex items-center gap-2.5 px-4.5 py-2.5 bg-slate-950/60 border border-slate-800 rounded-2xl w-fit">
          <Activity className={`w-4 h-4 text-blue-400 ${loading ? "animate-spin" : "animate-pulse"}`} />
          <div className="text-left">
            <span className="text-[9px] font-bold text-slate-500 block uppercase tracking-wider">Network Engine Status</span>
            <span className="text-xs font-extrabold text-slate-300 block uppercase tracking-wide">
              {loading ? "Analyzing Links..." : "Operational"}
            </span>
          </div>
        </div>
      </div>

      {/* 2. Search Panel */}
      <NetworkSearch onSearch={handleSearch} loading={loading} />

      {/* Error Message Banner */}
      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-2xl text-red-400 text-xs font-semibold flex items-center gap-3 max-w-4xl mx-auto shadow-md">
          <span className="w-2 h-2 rounded-full bg-red-500 animate-ping shrink-0" />
          <span>{error} Please check the ID and try again.</span>
        </div>
      )}

      {/* Graph Area / Initial State */}
      {hasGraphData ? (
        <div className="space-y-8 animate-fade-in">
          {/* 3. Statistics Panel */}
          <NetworkStatistics statistics={statistics} />

          {/* 4. Legend */}
          <NetworkLegend />

          {/* 5. React Flow Visualization */}
          <div className="relative">
            <CriminalNetworkGraph
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
            />
            {loading && (
              <div className="absolute inset-0 bg-slate-950/60 backdrop-blur-xs flex items-center justify-center z-20 rounded-3xl">
                <div className="flex flex-col items-center gap-3">
                  <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
                  <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">
                    Updating network graph...
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>
      ) : (
        !loading && (
          <div className="border border-dashed border-slate-900 bg-slate-950/20 rounded-3xl p-16 flex flex-col items-center justify-center text-center max-w-2xl mx-auto shadow-inner space-y-4">
            <div className="p-4 bg-slate-950/60 border border-slate-905 rounded-2xl">
              <HelpCircle className="w-8 h-8 text-slate-600" />
            </div>
            <div className="space-y-1">
              <h4 className="font-bold text-slate-300 text-sm uppercase tracking-wider">No Network Loaded</h4>
              <p className="text-xs text-slate-500 max-w-xs leading-relaxed">
                Provide a valid criminal identifier in the search bar above to fetch and map links.
              </p>
            </div>
          </div>
        )
      )}

      {/* Loading placeholder when graph is loading for the first time */}
      {loading && !hasGraphData && (
        <div className="border border-slate-900 bg-slate-950/40 rounded-3xl p-24 flex flex-col items-center justify-center text-center max-w-2xl mx-auto shadow-md">
          <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-4" />
          <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">
            Tracing associations & location links...
          </span>
        </div>
      )}

      {/* Footer logs */}
      <div className="pt-8 border-t border-slate-900 flex justify-between items-center text-[10px] font-mono text-slate-600 tracking-wider">
        <span>SECURE CRIMINAL LINK ASSOCIATION ENGINE</span>
        <span>PHASE 6B NETWORK VISUALIZATION</span>
      </div>
    </div>
  );
}
