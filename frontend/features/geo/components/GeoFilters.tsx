import React, { useEffect, useState } from "react";
import { Filter, Calendar, MapPin, ShieldAlert, Crosshair } from "lucide-react";
import type { GeoFiltersState } from "../types/geo";
import { fetchGeoLookupOptions } from "../services/geoApi";

interface GeoFiltersProps {
  filters: GeoFiltersState;
  onFiltersChange: (filters: GeoFiltersState) => void;
}

const DEFAULT_MIN_CRIME_COUNT = 3;

export default function GeoFilters({ filters, onFiltersChange }: GeoFiltersProps) {
  const [districts, setDistricts] = useState<string[]>([]);
  const [crimeTypes, setCrimeTypes] = useState<string[]>([]);

  useEffect(() => {
    let active = true;
    fetchGeoLookupOptions()
      .then((res) => {
        if (active) {
          setDistricts(res.districts);
          setCrimeTypes(res.categories);
        }
      })
      .catch((err) => {
        console.error("Failed to load backend geo lookups:", err);
      });
    return () => {
      active = false;
    };
  }, []);

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

  const handleMinCrimeCountChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = parseInt(e.target.value, 10);
    if (!isNaN(val) && val >= 1) {
      onFiltersChange({ ...filters, min_crime_count: val });
    } else if (e.target.value === "") {
      // Reset to default (backend will use its own default)
      const { min_crime_count: _removed, ...rest } = filters;
      onFiltersChange(rest);
    }
  };

  const resetFilters = () => {
    onFiltersChange({});
  };

  const activeFilterCount = [
    filters.district,
    filters.crime_type,
    filters.start_date,
    filters.end_date,
    filters.min_crime_count !== undefined ? String(filters.min_crime_count) : undefined,
  ].filter(Boolean).length;

  return (
    <div className="glass-card p-6 rounded-2xl border border-slate-800/60 mb-6 bg-slate-900/20 backdrop-blur-md">
      <div className="flex items-center justify-between mb-4 border-b border-slate-800/40 pb-3">
        <div className="flex items-center gap-2 text-indigo-400 font-semibold text-sm uppercase tracking-wider">
          <Filter className="w-4 h-4" />
          <span>Geo Intelligence Query Filters</span>
          {activeFilterCount > 0 && (
            <span className="ml-1 inline-flex items-center justify-center w-4 h-4 rounded-full bg-indigo-500 text-white text-[9px] font-black">
              {activeFilterCount}
            </span>
          )}
        </div>
        <button
          onClick={resetFilters}
          className="text-xs font-bold text-slate-400 hover:text-indigo-400 transition-colors cursor-pointer"
        >
          Reset Filters
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
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
              className="w-full bg-[#0a0f1d] border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 outline-none focus:border-indigo-500 hover:border-slate-700 transition-all appearance-none cursor-pointer font-sans"
            >
              <option value="">All Districts</option>
              {districts.map((d) => (
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
              className="w-full bg-[#0a0f1d] border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 outline-none focus:border-indigo-500 hover:border-slate-700 transition-all appearance-none cursor-pointer font-sans"
            >
              <option value="">All Categories</option>
              {crimeTypes.map((t) => (
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
            className="w-full bg-[#0a0f1d] border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-slate-200 outline-none focus:border-indigo-500 hover:border-slate-700 transition-all cursor-pointer font-sans"
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
            className="w-full bg-[#0a0f1d] border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-slate-200 outline-none focus:border-indigo-500 hover:border-slate-700 transition-all cursor-pointer font-sans"
          />
        </div>

        {/* Hotspot Sensitivity — Min. Crimes per Cluster */}
        <div className="flex flex-col gap-1.5">
          <label className="text-[10px] uppercase font-bold text-slate-400 tracking-wider flex items-center gap-1">
            <Crosshair className="w-3 h-3 text-rose-500" />
            <span className="text-rose-400/80">Hotspot Min. Crimes</span>
          </label>
          <div className="relative flex items-center gap-2">
            <input
              type="number"
              min={1}
              max={500}
              step={1}
              placeholder={String(DEFAULT_MIN_CRIME_COUNT)}
              value={filters.min_crime_count ?? ""}
              onChange={handleMinCrimeCountChange}
              className="w-full bg-[#0a0f1d] border border-rose-900/40 rounded-xl px-3.5 py-2 text-xs text-slate-200 outline-none focus:border-rose-500/60 hover:border-rose-800/60 transition-all cursor-pointer font-sans placeholder:text-slate-600"
            />
          </div>
          <p className="text-[9px] text-slate-600 leading-tight font-sans">
            Lower = more hotspots detected. Raise when filtering to a specific area.
          </p>
        </div>
      </div>
    </div>
  );
}

