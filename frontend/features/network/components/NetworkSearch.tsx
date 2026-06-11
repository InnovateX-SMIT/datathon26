import React, { useState } from "react";
import { Search, Info } from "lucide-react";

interface NetworkSearchProps {
  onSearch: (criminalId: number) => void;
  loading: boolean;
}

export default function NetworkSearch({ onSearch, loading }: NetworkSearchProps) {
  const [value, setValue] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const parsedId = parseInt(value.trim(), 10);
    if (!isNaN(parsedId)) {
      onSearch(parsedId);
    }
  };

  return (
    <div className="glass-card bg-slate-950/40 border border-slate-900 rounded-3xl p-6 shadow-xl backdrop-blur-md">
      <div className="flex items-center gap-2 mb-4">
        <Search className="w-4 h-4 text-indigo-400" />
        <h3 className="text-sm font-black text-slate-200 uppercase tracking-wider">
          Criminal ID Link Finder
        </h3>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <input
            type="number"
            min="1"
            placeholder="Enter Criminal ID (e.g., 1)..."
            value={value}
            onChange={(e) => setValue(e.target.value)}
            className="w-full bg-slate-950/80 border border-slate-800 text-slate-100 placeholder-slate-500 rounded-2xl py-3 px-4 text-sm focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/20 transition-all font-mono"
            required
            disabled={loading}
          />
        </div>
        <button
          type="submit"
          disabled={loading || !value.trim()}
          className="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-900 disabled:text-slate-600 disabled:border-slate-950 border border-indigo-500/30 text-white font-extrabold text-xs uppercase tracking-widest rounded-2xl cursor-pointer hover:shadow-[0_0_15px_rgba(99,102,241,0.4)] disabled:shadow-none transition-all duration-300 shrink-0"
        >
          {loading ? "Loading Graph..." : "Load Graph"}
        </button>
      </form>

      <div className="mt-3.5 flex gap-2 items-start text-[10px] text-slate-500 leading-normal">
        <Info className="w-3.5 h-3.5 shrink-0 mt-0.5 text-indigo-500/50" />
        <span>
          Enter a numerical database identifier to search and render coordinate link visualizations. Visual nodes are layered by hierarchy: Criminals, related Crimes, and occurrence Locations.
        </span>
      </div>
    </div>
  );
}
