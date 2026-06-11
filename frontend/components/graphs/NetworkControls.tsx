import React from "react";
import { useReactFlow } from "@xyflow/react";
import { Maximize, RefreshCw, Crosshair } from "lucide-react";

export default function NetworkControls() {
  const { fitView, zoomTo, setCenter } = useReactFlow();

  const handleFit = () => {
    fitView({ padding: 0.2, duration: 800 });
  };

  const handleResetZoom = () => {
    zoomTo(1, { duration: 800 });
  };

  const handleCenter = () => {
    // Centers the view back to the middle of the nodes layout (approx. x=400, y=280)
    setCenter(400, 280, { zoom: 1.0, duration: 800 });
  };

  return (
    <div className="absolute bottom-4 left-4 z-10 flex flex-col gap-2 bg-slate-950/80 border border-slate-900 rounded-xl p-2 shadow-xl backdrop-blur-md">
      {/* Fit Graph */}
      <button
        onClick={handleFit}
        title="Fit Graph"
        className="p-2 bg-slate-900 hover:bg-indigo-500/20 hover:text-indigo-400 border border-slate-800 rounded-lg text-slate-400 hover:border-indigo-500/30 transition-all duration-200 cursor-pointer flex items-center justify-center"
      >
        <Maximize className="w-4 h-4" />
      </button>

      {/* Reset Zoom */}
      <button
        onClick={handleResetZoom}
        title="Reset Zoom"
        className="p-2 bg-slate-900 hover:bg-indigo-500/20 hover:text-indigo-400 border border-slate-800 rounded-lg text-slate-400 hover:border-indigo-500/30 transition-all duration-200 cursor-pointer flex items-center justify-center"
      >
        <RefreshCw className="w-4 h-4" />
      </button>

      {/* Center Graph */}
      <button
        onClick={handleCenter}
        title="Center Graph"
        className="p-2 bg-slate-900 hover:bg-indigo-500/20 hover:text-indigo-400 border border-slate-800 rounded-lg text-slate-400 hover:border-indigo-500/30 transition-all duration-200 cursor-pointer flex items-center justify-center"
      >
        <Crosshair className="w-4 h-4" />
      </button>
    </div>
  );
}
