import React, { useState } from "react";
import { Search, Info, Database } from "lucide-react";
import type { NetworkCriminalSample } from "@/types/network";

interface NetworkSearchProps {
  onSearch: (criminalId: number) => void;
  loading: boolean;
  samples: NetworkCriminalSample[];
  activeDatasetId: number | null;
}

export default function NetworkSearch({ onSearch, loading, samples, activeDatasetId }: NetworkSearchProps) {
  const [value, setValue] = useState("");

  const effectiveValue = value || (samples[0] ? String(samples[0].id) : "");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const parsedId = parseInt(effectiveValue.trim(), 10);
    if (!Number.isNaN(parsedId)) {
      onSearch(parsedId);
    }
  };

  const handleSampleClick = (id: number) => {
    setValue(String(id));
    onSearch(id);
  };

  return (
    <div className="glass-card bg-slate-950/40 border border-slate-900 rounded-2xl p-5 shadow-xl backdrop-blur-md">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between mb-4">
        <div className="flex items-center gap-2">
          <Search className="w-4 h-4 text-indigo-400" />
          <h3 className="text-sm font-black text-slate-200 uppercase tracking-wider">
            Criminal ID Link Finder
          </h3>
        </div>
        {activeDatasetId && (
          <div className="flex items-center gap-1.5 text-[10px] font-bold text-slate-500 uppercase tracking-wider">
            <Database className="w-3.5 h-3.5 text-indigo-400" />
            Active Dataset #{activeDatasetId}
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <input
            type="number"
            min="1"
            placeholder={samples[0] ? `Try ${samples[0].id}` : "Enter criminal ID..."}
            value={effectiveValue}
            onChange={(e) => setValue(e.target.value)}
            className="w-full bg-slate-950/80 border border-slate-800 text-slate-100 placeholder-slate-500 rounded-xl py-3 px-4 text-sm focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/20 transition-all font-mono"
            required
            disabled={loading}
          />
        </div>
        <button
          type="submit"
          disabled={loading || !effectiveValue.trim()}
          className="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-900 disabled:text-slate-600 disabled:border-slate-950 border border-indigo-500/30 text-white font-extrabold text-xs uppercase tracking-widest rounded-xl cursor-pointer hover:shadow-[0_0_15px_rgba(99,102,241,0.35)] disabled:shadow-none transition-all duration-300 shrink-0"
        >
          {loading ? "Loading Graph..." : "Load Graph"}
        </button>
      </form>

      {samples.length > 0 && (
        <div className="mt-4 flex flex-wrap gap-2">
          {samples.map((sample) => (
            <button
              key={sample.id}
              type="button"
              onClick={() => handleSampleClick(sample.id)}
              disabled={loading}
              className="px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-950/60 hover:border-indigo-500/40 hover:text-indigo-300 text-[10px] font-bold text-slate-400 transition-colors disabled:opacity-50"
              title={sample.name}
            >
              #{sample.id} {sample.name}
            </button>
          ))}
        </div>
      )}

      <div className="mt-3.5 flex gap-2 items-start text-[10px] text-slate-500 leading-normal">
        <Info className="w-3.5 h-3.5 shrink-0 mt-0.5 text-indigo-500/50" />
        <span>
          Suggested IDs are pulled from the currently active dataset, so graph lookups stay aligned after dataset switching.
        </span>
      </div>
    </div>
  );
}
