"use client";

import React, { useEffect, useState, useMemo } from "react";
import { Filter, Calendar, MapPin, Building2, ShieldAlert, Clock } from "lucide-react";
import type { GeoFiltersState, GeoLookupOptions } from "../types/geo";
import { fetchGeoLookupOptions } from "../services/geoApi";

interface GeoFiltersProps {
  filters: GeoFiltersState;
  onFiltersChange: (filters: GeoFiltersState) => void;
}

export default function GeoFilters({ filters, onFiltersChange }: GeoFiltersProps) {
  const [lookups, setLookups] = useState<GeoLookupOptions>({
    districts: [],
    categories: [],
    stations: [],
    stations_by_district: {},
  });

  useEffect(() => {
    let active = true;
    fetchGeoLookupOptions()
      .then((res) => {
        if (active) {
          setLookups(res);
        }
      })
      .catch((err) => {
        console.error("Failed to load backend geo lookups:", err);
      });
    return () => {
      active = false;
    };
  }, []);

  // Filter available police stations based on selected district
  const availableStations = useMemo(() => {
    if (filters.district && lookups.stations_by_district && lookups.stations_by_district[filters.district]) {
      return lookups.stations_by_district[filters.district];
    }
    return lookups.stations || [];
  }, [filters.district, lookups]);

  const handleDistrictChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selected = e.target.value || undefined;
    // If changing district, reset police station if it doesn't belong to the new district
    let newStation = filters.police_station;
    if (selected && lookups.stations_by_district[selected]) {
      if (newStation && !lookups.stations_by_district[selected].includes(newStation)) {
        newStation = undefined;
      }
    }
    onFiltersChange({ ...filters, district: selected, police_station: newStation });
  };

  const handleStationChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onFiltersChange({ ...filters, police_station: e.target.value || undefined });
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

  const handleTimePeriodChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onFiltersChange({ ...filters, time_period: e.target.value || undefined });
  };

  const resetFilters = () => {
    onFiltersChange({});
  };

  const activeFilterCount = [
    filters.district,
    filters.police_station,
    filters.crime_type,
    filters.start_date,
    filters.end_date,
    filters.time_period,
  ].filter(Boolean).length;

  return (
    <div className="glass-card p-6 rounded-2xl border border-slate-800/60 mb-6 bg-slate-900/20 backdrop-blur-md">
      <div className="flex items-center justify-between mb-4 border-b border-slate-800/40 pb-3">
        <div className="flex items-center gap-2 text-indigo-400 font-semibold text-sm uppercase tracking-wider font-sans">
          <Filter className="w-4 h-4" />
          <span>Geo Intelligence Query Filters</span>
          {activeFilterCount > 0 && (
            <span className="ml-1 inline-flex items-center justify-center px-2 py-0.5 rounded-full bg-indigo-500 text-white text-[9px] font-black font-mono">
              {activeFilterCount} Active
            </span>
          )}
        </div>
        <button
          onClick={resetFilters}
          className="text-xs font-bold text-slate-400 hover:text-indigo-400 transition-colors cursor-pointer font-sans"
        >
          Reset Filters
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {/* District Dropdown */}
        <div className="flex flex-col gap-1.5">
          <label className="text-[10px] uppercase font-bold text-slate-400 tracking-wider flex items-center gap-1 font-sans">
            <MapPin className="w-3 h-3 text-slate-500" />
            <span>District</span>
          </label>
          <select
            value={filters.district ?? ""}
            onChange={handleDistrictChange}
            className="w-full bg-[#0a0f1d] border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 outline-none focus:border-indigo-500 hover:border-slate-700 transition-all appearance-none cursor-pointer font-sans"
          >
            <option value="">All Districts</option>
            {lookups.districts.map((d) => (
              <option key={d} value={d}>
                {d}
              </option>
            ))}
          </select>
        </div>

        {/* Police Station Dropdown */}
        <div className="flex flex-col gap-1.5">
          <label className="text-[10px] uppercase font-bold text-slate-400 tracking-wider flex items-center gap-1 font-sans">
            <Building2 className="w-3 h-3 text-slate-500" />
            <span>Police Station</span>
          </label>
          <select
            value={filters.police_station ?? ""}
            onChange={handleStationChange}
            className="w-full bg-[#0a0f1d] border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 outline-none focus:border-indigo-500 hover:border-slate-700 transition-all appearance-none cursor-pointer font-sans"
          >
            <option value="">All Police Stations</option>
            {availableStations.map((st) => (
              <option key={st} value={st}>
                {st}
              </option>
            ))}
          </select>
        </div>

        {/* Crime Category Dropdown */}
        <div className="flex flex-col gap-1.5">
          <label className="text-[10px] uppercase font-bold text-slate-400 tracking-wider flex items-center gap-1 font-sans">
            <ShieldAlert className="w-3 h-3 text-slate-500" />
            <span>Crime Category</span>
          </label>
          <select
            value={filters.crime_type ?? ""}
            onChange={handleCrimeTypeChange}
            className="w-full bg-[#0a0f1d] border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 outline-none focus:border-indigo-500 hover:border-slate-700 transition-all appearance-none cursor-pointer font-sans"
          >
            <option value="">All Categories</option>
            {lookups.categories.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </div>

        {/* Time-of-Day Filter */}
        <div className="flex flex-col gap-1.5">
          <label className="text-[10px] uppercase font-bold text-slate-400 tracking-wider flex items-center gap-1 font-sans">
            <Clock className="w-3 h-3 text-slate-500" />
            <span>Time of Day</span>
          </label>
          <select
            value={filters.time_period ?? ""}
            onChange={handleTimePeriodChange}
            className="w-full bg-[#0a0f1d] border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 outline-none focus:border-indigo-500 hover:border-slate-700 transition-all appearance-none cursor-pointer font-sans"
          >
            <option value="">All Hours (24h)</option>
            <option value="morning">Morning (06:00 – 12:00)</option>
            <option value="afternoon">Afternoon (12:00 – 18:00)</option>
            <option value="evening">Evening (18:00 – 24:00)</option>
            <option value="night">Night (00:00 – 06:00)</option>
          </select>
        </div>

        {/* Start Date Picker */}
        <div className="flex flex-col gap-1.5">
          <label className="text-[10px] uppercase font-bold text-slate-400 tracking-wider flex items-center gap-1 font-sans">
            <Calendar className="w-3 h-3 text-slate-500" />
            <span>Start Date</span>
          </label>
          <input
            type="date"
            value={filters.start_date ?? ""}
            onChange={handleStartDateChange}
            className="w-full bg-[#0a0f1d] border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-slate-200 outline-none focus:border-indigo-500 hover:border-slate-700 transition-all cursor-pointer font-sans"
          />
        </div>

        {/* End Date Picker */}
        <div className="flex flex-col gap-1.5">
          <label className="text-[10px] uppercase font-bold text-slate-400 tracking-wider flex items-center gap-1 font-sans">
            <Calendar className="w-3 h-3 text-slate-500" />
            <span>End Date</span>
          </label>
          <input
            type="date"
            value={filters.end_date ?? ""}
            onChange={handleEndDateChange}
            className="w-full bg-[#0a0f1d] border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-slate-200 outline-none focus:border-indigo-500 hover:border-slate-700 transition-all cursor-pointer font-sans"
          />
        </div>
      </div>

      {activeFilterCount > 0 && (
        <div className="mt-4 pt-3 border-t border-slate-800/40 flex flex-wrap items-center gap-1.5 text-[10px] font-mono">
          <span className="text-slate-500">Active Filters:</span>
          {filters.district && (
            <span className="bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 px-2 py-0.5 rounded">
              Dist: {filters.district}
            </span>
          )}
          {filters.police_station && (
            <span className="bg-blue-500/10 border border-blue-500/20 text-blue-300 px-2 py-0.5 rounded">
              PS: {filters.police_station}
            </span>
          )}
          {filters.crime_type && (
            <span className="bg-amber-500/10 border border-amber-500/20 text-amber-300 px-2 py-0.5 rounded">
              Cat: {filters.crime_type}
            </span>
          )}
          {filters.time_period && (
            <span className="bg-sky-500/10 border border-sky-500/20 text-sky-300 px-2 py-0.5 rounded">
              Time: {filters.time_period}
            </span>
          )}
        </div>
      )}
    </div>
  );
}

