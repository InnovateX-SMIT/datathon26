import React from "react";
import { Filter, Calendar, MapPin, ShieldAlert } from "lucide-react";
import type { GeoFiltersState } from "../types/geo";

interface GeoFiltersProps {
  filters: GeoFiltersState;
  onFiltersChange: (filters: GeoFiltersState) => void;
}

const DISTRICTS = [
  "Ballari",
  "Shivamogga",
  "Mysuru",
  "Kalaburagi",
  "Tumakuru",
  "Mangaluru",
  "Bengaluru Urban",
  "Bengaluru Rural",
  "Belagavi",
  "Hubballi"
];

const CRIME_TYPES = [
  "Theft",
  "Assault",
  "Burglary",
  "Robbery",
  "Murder",
  "Kidnapping",
  "Fraud",
  "Riot",
  "Cybercrime"
];

export default function GeoFilters({ filters, onFiltersChange }: GeoFiltersProps) {
  const handleDistrictChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onFiltersChange({ ...filters, district: e.target.value || undefined });
  };

  const handleCrimeTypeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onFiltersChange({ ...filters, crime_type: e.target.value || undefined });
  };

  const handleStartDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onFiltersChange({ ...filters, start_date: e.target.value || undefined });
  };

  const handleEndDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onFiltersChange({ ...filters, end_date: e.target.value || undefined });
  };

  const resetFilters = () => {
    onFiltersChange({});
  };

  return (
    <div className="glass-card p-6 rounded-2xl border border-slate-800/60 mb-6 bg-slate-900/20 backdrop-blur-md">
      <div className="flex items-center justify-between mb-4 border-b border-slate-800/40 pb-3">
        <div className="flex items-center gap-2 text-indigo-400 font-semibold text-sm uppercase tracking-wider">
          <Filter className="w-4 h-4" />
          <span>Geo Intelligence Query Filters</span>
        </div>
        <button
          onClick={resetFilters}
          className="text-xs font-bold text-slate-400 hover:text-indigo-400 transition-colors cursor-pointer"
        >
          Reset Filters
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* District Dropdown */}
        <div className="flex flex-col gap-1.5">
          <label className="text-[10px] uppercase font-bold text-slate-400 tracking-wider flex items-center gap-1">
            <MapPin className="w-3 h-3 text-slate-500" />
            <span>District / Region</span>
          </label>
          <div className="relative">
            <select
              value={filters.district ?? ""}
              onChange={handleDistrictChange}
              className="w-full bg-[#0a0f1d] border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 outline-none focus:border-indigo-500 hover:border-slate-700 transition-all appearance-none cursor-pointer"
            >
              <option value="">All Districts</option>
              {DISTRICTS.map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Crime Category Dropdown */}
        <div className="flex flex-col gap-1.5">
          <label className="text-[10px] uppercase font-bold text-slate-400 tracking-wider flex items-center gap-1">
            <ShieldAlert className="w-3 h-3 text-slate-500" />
            <span>Crime Category</span>
          </label>
          <div className="relative">
            <select
              value={filters.crime_type ?? ""}
              onChange={handleCrimeTypeChange}
              className="w-full bg-[#0a0f1d] border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 outline-none focus:border-indigo-500 hover:border-slate-700 transition-all appearance-none cursor-pointer"
            >
              <option value="">All Categories</option>
              {CRIME_TYPES.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Start Date Picker */}
        <div className="flex flex-col gap-1.5">
          <label className="text-[10px] uppercase font-bold text-slate-400 tracking-wider flex items-center gap-1">
            <Calendar className="w-3 h-3 text-slate-500" />
            <span>Start Date</span>
          </label>
          <input
            type="date"
            value={filters.start_date ?? ""}
            onChange={handleStartDateChange}
            className="w-full bg-[#0a0f1d] border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-slate-200 outline-none focus:border-indigo-500 hover:border-slate-700 transition-all cursor-pointer"
          />
        </div>

        {/* End Date Picker */}
        <div className="flex flex-col gap-1.5">
          <label className="text-[10px] uppercase font-bold text-slate-400 tracking-wider flex items-center gap-1">
            <Calendar className="w-3 h-3 text-slate-500" />
            <span>End Date</span>
          </label>
          <input
            type="date"
            value={filters.end_date ?? ""}
            onChange={handleEndDateChange}
            className="w-full bg-[#0a0f1d] border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-slate-200 outline-none focus:border-indigo-500 hover:border-slate-700 transition-all cursor-pointer"
          />
        </div>
      </div>
    </div>
  );
}
