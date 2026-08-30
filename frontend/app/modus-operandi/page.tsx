"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  Fingerprint,
  MapPin,
  Clock,
  ArrowRight,
  Search,
  Users,
  Scale,
  RefreshCw,
  FileText,
  Building,
  TrendingUp,
  User,
  AlertTriangle,
  Loader2,
  ExternalLink,
  ShieldAlert,
  ChevronRight,
} from "lucide-react";
import PageHeader from "@/components/layout/page-header";
import SectionHeader from "@/components/layout/section-header";
import { fetchDatasets, type DatasetInfo } from "@/services/dataset.service";
import {
  getCrossJurisdictionMO,
  listCases,
  getOffenderMOProfile,
} from "@/features/fir/services/firApi";
import type {
  CrossJurisdictionSummary,
  CrossJurisdictionLink,
  OffenderBehavioralProfileResponse,
} from "@/features/fir/types/mo";
import type { CaseMasterResponse } from "@/features/fir/types/fir";
import FirModusOperandi from "@/features/fir/components/FirModusOperandi";

export default function ModusOperandiPage() {
  const [activeDatasets, setActiveDatasets] = useState<DatasetInfo[]>([]);
  const [datasetsLoading, setDatasetsLoading] = useState(true);

  // Tabs: "cross-jurisdiction" | "case-analyzer" | "offender-profiles"
  const [activeTab, setActiveTab] = useState<"cross-jurisdiction" | "case-analyzer" | "offender-profiles">(
    "cross-jurisdiction"
  );

  // Cross-jurisdiction state
  const [crossMoData, setCrossMoData] = useState<CrossJurisdictionSummary | null>(null);
  const [crossLoading, setCrossLoading] = useState(false);
  const [crossError, setCrossError] = useState<string | null>(null);

  // Case similarity analyzer state
  const [selectedCaseId, setSelectedCaseId] = useState<number | null>(null);
  const [caseSearchQuery, setCaseSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<CaseMasterResponse[]>([]);
  const [searchLoading, setSearchLoading] = useState(false);

  // Offender profile state
  const [offenderIdInput, setOffenderIdInput] = useState("");
  const [offenderProfile, setOffenderProfile] = useState<OffenderBehavioralProfileResponse | null>(null);
  const [offenderLoading, setOffenderLoading] = useState(false);
  const [offenderError, setOffenderError] = useState<string | null>(null);
  
  // List of suspects from active dataset case search for quick selection
  const [discoveredSuspects, setDiscoveredSuspects] = useState<Array<{ id: number; name: string; caseNo?: string }>>([]);

  const loadActiveDatasets = async () => {
    setDatasetsLoading(true);
    try {
      const data = await fetchDatasets();
      setActiveDatasets(data.filter((d) => d.is_active));
    } catch (err) {
      console.error("Failed to load datasets", err);
    } finally {
      setDatasetsLoading(false);
    }
  };

  const loadCrossJurisdictionMO = async () => {
    setCrossLoading(true);
    setCrossError(null);
    try {
      const data = await getCrossJurisdictionMO(0.35, 30); // Use 0.35 threshold for wider discovery
      setCrossMoData(data);
    } catch (err) {
      console.error("Failed to load cross-jurisdiction MO patterns", err);
      setCrossError(err instanceof Error ? err.message : "Failed to load cross-jurisdiction patterns");
    } finally {
      setCrossLoading(false);
    }
  };

  useEffect(() => {
    loadActiveDatasets();
    const handler = () => loadActiveDatasets();
    window.addEventListener("activeDatasetChanged", handler);
    return () => window.removeEventListener("activeDatasetChanged", handler);
  }, []);

  useEffect(() => {
    const isFirDataset = activeDatasets.some((d) => d.schema_type === "fir_normalized");
    if (isFirDataset) {
      loadCrossJurisdictionMO();
      // Load quick suspect list from initial cases
      listCases({ page: 1, page_size: 30 })
        .then((res) => {
          const suspectsMap: Record<number, { id: number; name: string; caseNo?: string }> = {};
          res.records.forEach((c) => {
            if (c.accused && c.accused.length > 0) {
              c.accused.forEach((a) => {
                suspectsMap[a.id] = { id: a.id, name: a.AccusedName, caseNo: c.CrimeNo || undefined };
              });
            }
          });
          setDiscoveredSuspects(Object.values(suspectsMap));
        })
        .catch((e) => console.error("Failed to populate initial suspects", e));
    }
  }, [activeDatasets]);

  // Handle case search
  const handleCaseSearch = async (val: string) => {
    setCaseSearchQuery(val);
    if (!val.trim()) {
      setSearchResults([]);
      return;
    }
    setSearchLoading(true);
    try {
      const res = await listCases({ q: val, page_size: 8 });
      setSearchResults(res.records);
    } catch (e) {
      console.error("Search failed", e);
    } finally {
      setSearchLoading(false);
    }
  };

  // Handle Offender profile fetch
  const handleOffenderLookup = async (id: number) => {
    setOffenderLoading(true);
    setOffenderError(null);
    try {
      const data = await getOffenderMOProfile(id);
      setOffenderProfile(data);
    } catch (err) {
      setOffenderError(err instanceof Error ? err.message : "Accused profile not found.");
      setOffenderProfile(null);
    } finally {
      setOffenderLoading(false);
    }
  };

  const isFirDataset = activeDatasets.some((d) => d.schema_type === "fir_normalized");

  // No active dataset
  if (!datasetsLoading && activeDatasets.length === 0) {
    return (
      <div className="min-h-[80vh] flex flex-col items-center justify-center p-6 text-center text-slate-200">
        <div className="bg-slate-900/60 p-8 rounded-3xl border border-slate-800/80 max-w-md w-full backdrop-blur-md space-y-6">
          <ShieldAlert className="w-16 h-16 text-indigo-400 mx-auto animate-pulse" />
          <h2 className="text-xl font-bold uppercase tracking-tight">No Active Dataset</h2>
          <p className="text-sm text-slate-400 leading-relaxed">
            Modus Operandi analysis requires an active FIR-normalized dataset. Please activate one from the Dataset Manager.
          </p>
          <Link
            href="/dataset-manager"
            className="block w-full py-3 px-4 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs uppercase tracking-wider rounded-xl transition-all shadow-lg shadow-indigo-600/10"
          >
            Go to Dataset Manager
          </Link>
        </div>
      </div>
    );
  }

  // Legacy dataset active (not FIR normalized)
  if (!datasetsLoading && !isFirDataset) {
    return (
      <div className="min-h-[80vh] flex flex-col items-center justify-center p-6 text-center text-slate-200">
        <div className="bg-slate-900/60 p-8 rounded-3xl border border-amber-500/30 max-w-md w-full backdrop-blur-md space-y-6">
          <ShieldAlert className="w-16 h-16 text-amber-400 mx-auto" />
          <h2 className="text-xl font-bold uppercase tracking-tight">Legacy Dataset Active</h2>
          <p className="text-sm text-slate-400 leading-relaxed">
            The currently active dataset uses the legacy schema. Modus Operandi similarity analysis is only supported on FIR-normalized datasets.
            Switch to an FIR dataset in the Dataset Manager to use this feature.
          </p>
          <Link
            href="/dataset-manager"
            className="block w-full py-3 px-4 bg-amber-600 hover:bg-amber-500 text-white font-bold text-xs uppercase tracking-wider rounded-xl transition-all"
          >
            Switch Dataset
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
      {/* Page Header */}
      <PageHeader
        icon={Fingerprint}
        iconColor="text-violet-400"
        iconBg="bg-violet-500/10 border border-violet-500/20"
        badge="Behavioral Intelligence"
        title="Modus Operandi Similarity Analysis"
        subtitle="TF-IDF & Cosine Similarity Analytics Engine"
        description="Discover inter-district crime matches, analyze extracted case-level modus operandi profiles, and track recurring offender signatures using NLP similarity mapping."
      >
        <button
          onClick={() => {
            loadCrossJurisdictionMO();
            if (selectedCaseId) {
              // Trigger reload of component if needed
              setSelectedCaseId((prev) => prev);
            }
          }}
          disabled={crossLoading}
          className="flex items-center gap-2 px-5 py-2.5 bg-slate-900 hover:bg-slate-850 border border-slate-800 hover:border-slate-700 text-slate-300 hover:text-slate-100 font-bold text-xs uppercase tracking-wider rounded-xl transition-all shadow-lg cursor-pointer"
        >
          <RefreshCw className={`w-4 h-4 ${crossLoading ? "animate-spin" : ""}`} />
          Recalculate Intel
        </button>
      </PageHeader>

      {/* Tabs Menu */}
      <div className="flex border-b border-slate-900">
        <div className="flex gap-2">
          <button
            onClick={() => setActiveTab("cross-jurisdiction")}
            className={`pb-4 px-4 text-xs uppercase tracking-widest font-black transition-all relative cursor-pointer ${
              activeTab === "cross-jurisdiction"
                ? "text-indigo-400 border-b-2 border-indigo-500"
                : "text-slate-500 hover:text-slate-355"
            }`}
          >
            Cross-Jurisdiction Patterns
          </button>
          <button
            onClick={() => setActiveTab("case-analyzer")}
            className={`pb-4 px-4 text-xs uppercase tracking-widest font-black transition-all relative cursor-pointer ${
              activeTab === "case-analyzer"
                ? "text-indigo-400 border-b-2 border-indigo-500"
                : "text-slate-500 hover:text-slate-355"
            }`}
          >
            Case MO Analyzer
          </button>
          <button
            onClick={() => setActiveTab("offender-profiles")}
            className={`pb-4 px-4 text-xs uppercase tracking-widest font-black transition-all relative cursor-pointer ${
              activeTab === "offender-profiles"
                ? "text-indigo-400 border-b-2 border-indigo-500"
                : "text-slate-500 hover:text-slate-355"
            }`}
          >
            Offender Profiles
          </button>
        </div>
      </div>

      {/* Tab Panels */}
      <div className="space-y-6">
        
        {/* TAB 1: Cross-Jurisdiction Patterns */}
        {activeTab === "cross-jurisdiction" && (
          <div className="space-y-6">
            {/* Quick summary metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="glass-card rounded-2xl p-5 border border-slate-800/60 flex items-center justify-between">
                <div>
                  <span className="text-[9px] font-bold text-slate-500 uppercase tracking-wider block">
                    Inter-District Links
                  </span>
                  <span className="text-3xl font-black text-violet-400 font-mono block">
                    {crossMoData?.total_cross_jurisdiction_patterns ?? 0}
                  </span>
                </div>
                <div className="p-3 bg-slate-900 border border-slate-800 rounded-xl text-slate-400">
                  <TrendingUp className="w-5 h-5 text-violet-400" />
                </div>
              </div>

              <div className="glass-card rounded-2xl p-5 border border-slate-800/60 flex items-center justify-between">
                <div>
                  <span className="text-[9px] font-bold text-slate-500 uppercase tracking-wider block">
                    Active Jurisdiction Pairs
                  </span>
                  <span className="text-3xl font-black text-indigo-400 font-mono block">
                    {crossMoData?.jurisdiction_pairs.length ?? 0}
                  </span>
                </div>
                <div className="p-3 bg-slate-900 border border-slate-800 rounded-xl text-slate-400">
                  <Building className="w-5 h-5 text-indigo-400" />
                </div>
              </div>

              <div className="glass-card rounded-2xl p-5 border border-slate-800/60 flex items-center justify-between">
                <div>
                  <span className="text-[9px] font-bold text-slate-500 uppercase tracking-wider block">
                    Highest Similarity Link
                  </span>
                  <span className="text-3xl font-black text-emerald-400 font-mono block">
                    {crossMoData && crossMoData.sample_links.length > 0
                      ? `${crossMoData.sample_links[0].similarity_percentage}%`
                      : "—"}
                  </span>
                </div>
                <div className="p-3 bg-slate-900 border border-slate-800 rounded-xl text-slate-400">
                  <Fingerprint className="w-5 h-5 text-emerald-400" />
                </div>
              </div>
            </div>

            {/* Jurisdiction Matrix */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              
              {/* Left Column: District Pairs list */}
              <div className="glass-card rounded-2xl border border-slate-800/60 p-5 space-y-4 lg:col-span-1">
                <SectionHeader title="High-Risk District Interlinks" accentColor="bg-indigo-500" />
                <p className="text-xs text-slate-400 leading-relaxed font-medium">
                  The following borders contain highly overlapping Modus Operandi signatures, suggesting mobile criminal operations or shared networks.
                </p>

                {crossLoading ? (
                  <div className="py-12 flex justify-center text-slate-500">
                    <Loader2 className="w-6 h-6 animate-spin text-indigo-400" />
                  </div>
                ) : !crossMoData || crossMoData.jurisdiction_pairs.length === 0 ? (
                  <div className="py-8 text-center text-slate-500 italic text-xs">
                    No high-similarity cross-jurisdiction patterns found in active samples.
                  </div>
                ) : (
                  <div className="space-y-2.5 max-h-[500px] overflow-y-auto pr-1">
                    {crossMoData.jurisdiction_pairs.map((pair, idx) => (
                      <div
                        key={idx}
                        className="bg-slate-900/35 border border-slate-800/60 rounded-xl p-3 flex flex-col gap-1.5"
                      >
                        <div className="flex items-center justify-between text-xs font-bold text-slate-200">
                          <span className="truncate">{pair.district_a}</span>
                          <span className="text-slate-500 px-1.5">↔</span>
                          <span className="truncate">{pair.district_b}</span>
                        </div>
                        <div className="flex items-center justify-between text-[11px] text-slate-450 font-mono mt-0.5">
                          <span>Links: <strong className="text-indigo-400 font-bold">{pair.linked_cases_count}</strong></span>
                          <span>Avg Sim: <strong className="text-slate-300">{(pair.avg_similarity * 100).toFixed(0)}%</strong></span>
                          <span>Max Sim: <strong className="text-emerald-455 font-bold">{(pair.max_similarity * 100).toFixed(0)}%</strong></span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Right Column: Similar cases links list */}
              <div className="glass-card rounded-2xl border border-slate-800/60 p-5 space-y-4 lg:col-span-2">
                <SectionHeader title="Linked Cross-District Case Matches" accentColor="bg-violet-500" />

                {crossLoading ? (
                  <div className="py-24 flex flex-col items-center justify-center gap-3 text-slate-500">
                    <Loader2 className="w-7 h-7 animate-spin text-violet-400" />
                    <span className="text-xs uppercase font-bold tracking-wider">Loading Cross-Border Intel...</span>
                  </div>
                ) : crossError ? (
                  <div className="p-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl text-xs flex gap-2 items-center">
                    <AlertTriangle className="w-5 h-5" />
                    <span>Failed to fetch cross-district links: {crossError}</span>
                  </div>
                ) : !crossMoData || crossMoData.sample_links.length === 0 ? (
                  <div className="py-24 text-center text-slate-500 italic text-xs">
                    No similar cross-district case matches registered.
                  </div>
                ) : (
                  <div className="space-y-3.5 max-h-[580px] overflow-y-auto pr-1">
                    {crossMoData.sample_links.map((link, idx) => (
                      <div
                        key={idx}
                        className="bg-slate-900/40 hover:bg-slate-900/70 border border-slate-800/60 rounded-xl p-4 transition-all flex flex-col md:flex-row md:items-center justify-between gap-4"
                      >
                        <div className="flex-1 space-y-2 min-w-0">
                          {/* Case Headers */}
                          <div className="flex flex-wrap items-center gap-2 text-xs">
                            <Link
                              href={`/fir/cases/${link.source_case_id}`}
                              className="font-mono font-bold text-indigo-400 hover:underline"
                            >
                              {link.source_crime_no || `Case #${link.source_case_id}`}
                            </Link>
                            <span className="text-slate-500 text-[10px]">({link.source_district})</span>
                            <span className="text-slate-500 px-1">↔</span>
                            <Link
                              href={`/fir/cases/${link.target_case_id}`}
                              className="font-mono font-bold text-violet-400 hover:underline"
                            >
                              {link.target_crime_no || `Case #${link.target_case_id}`}
                            </Link>
                            <span className="text-slate-500 text-[10px]">({link.target_district})</span>
                          </div>

                          <div className="text-[11px] text-slate-400 font-semibold uppercase tracking-wide">
                            Crime Type: <span className="text-slate-350">{link.crime_type}</span>
                          </div>

                          {/* Common traits */}
                          {link.matching_attributes.length > 0 && (
                            <div className="flex flex-wrap items-center gap-1">
                              <span className="text-[9px] font-bold text-slate-500 uppercase tracking-widest mr-1">
                                Shared Traits:
                              </span>
                              {link.matching_attributes.map((trait, tIdx) => (
                                <span
                                  key={tIdx}
                                  className="px-2 py-0.2 bg-violet-500/10 text-violet-300 border border-violet-500/25 rounded text-[10px] font-medium"
                                >
                                  {trait}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>

                        {/* Similarity Score and Actions */}
                        <div className="flex items-center gap-3 shrink-0 self-end md:self-center">
                          <div className="text-right">
                            <div className="text-lg font-black text-violet-450 font-mono">
                              {link.similarity_percentage}%
                            </div>
                            <span className="text-[9px] font-bold text-slate-500 uppercase tracking-wider block">
                              TF-IDF Similarity
                            </span>
                          </div>
                          
                          <button
                            onClick={() => {
                              setSelectedCaseId(link.source_case_id);
                              setActiveTab("case-analyzer");
                            }}
                            className="p-2.5 bg-violet-600/30 hover:bg-violet-650 text-violet-250 hover:text-white rounded-xl border border-violet-500/20 transition-all cursor-pointer"
                            title="Analyze Similarity Details"
                          >
                            <ArrowRight className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: Case Similarity Viewer / Analyzer */}
        {activeTab === "case-analyzer" && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
            
            {/* Left selector sidebar */}
            <div className="glass-card rounded-2xl border border-slate-800/60 p-5 space-y-4 lg:col-span-1">
              <SectionHeader title="Target Case Selector" accentColor="bg-indigo-500" />
              
              {/* Case lookup search */}
              <div className="relative">
                <Search className="absolute left-3 top-3 w-4 h-4 text-slate-500" />
                <input
                  type="text"
                  placeholder="Search case by Crime / Case No or Title..."
                  value={caseSearchQuery}
                  onChange={(e) => handleCaseSearch(e.target.value)}
                  className="w-full bg-slate-900/60 border border-slate-700/60 text-slate-205 text-xs rounded-xl pl-9 pr-3 py-2.5 focus:border-indigo-500 focus:outline-none transition-colors placeholder:text-slate-600"
                />
              </div>

              {/* Search result dropdown box */}
              {caseSearchQuery && (
                <div className="bg-slate-950/80 border border-slate-800/80 rounded-xl overflow-hidden divide-y divide-slate-800/40 max-h-52 overflow-y-auto">
                  {searchLoading ? (
                    <div className="p-3 text-center text-xs text-slate-500 flex justify-center gap-2">
                      <Loader2 className="w-4 h-4 animate-spin text-indigo-400" /> Loading...
                    </div>
                  ) : searchResults.length === 0 ? (
                    <div className="p-3 text-center text-xs text-slate-500">No cases match search.</div>
                  ) : (
                    searchResults.map((c) => (
                      <button
                        key={c.id}
                        onClick={() => {
                          setSelectedCaseId(c.id);
                          setCaseSearchQuery("");
                          setSearchResults([]);
                        }}
                        className={`w-full text-left p-2.5 text-xs hover:bg-slate-900 transition-colors flex flex-col gap-0.5 ${
                          selectedCaseId === c.id ? "bg-indigo-650/15 border-l-2 border-indigo-500" : ""
                        }`}
                      >
                        <span className="font-mono font-bold text-indigo-400">{c.CrimeNo || `Case #${c.id}`}</span>
                        <span className="text-slate-400 font-medium truncate">{c.CaseNo || "—"} • {c.BriefFacts?.slice(0, 50)}...</span>
                      </button>
                    ))
                  )}
                </div>
              )}

              {/* Quick Select cases from cross jurisdiction if loaded */}
              <div>
                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-2">
                  Cases with Interlinks
                </span>
                {!crossMoData || crossMoData.sample_links.length === 0 ? (
                  <div className="text-xs text-slate-505 italic">No similar matches loaded.</div>
                ) : (
                  <div className="space-y-1.5 max-h-64 overflow-y-auto pr-1">
                    {Array.from(
                      new Map(
                        crossMoData.sample_links.flatMap((l) => [
                          [l.source_case_id, { id: l.source_case_id, crimeNo: l.source_crime_no }],
                          [l.target_case_id, { id: l.target_case_id, crimeNo: l.target_crime_no }],
                        ])
                      ).values()
                    ).slice(0, 12).map((item) => (
                      <button
                        key={item.id}
                        onClick={() => setSelectedCaseId(item.id)}
                        className={`w-full text-left p-2 bg-slate-900/30 hover:bg-slate-900 border border-slate-800/40 hover:border-slate-700/60 rounded-lg text-xs font-mono text-slate-300 font-bold transition-all flex items-center justify-between ${
                          selectedCaseId === item.id ? "border-indigo-500 bg-indigo-500/5 text-indigo-400" : ""
                        }`}
                      >
                        <span className="truncate">{item.crimeNo || `Case #${item.id}`}</span>
                        <ChevronRight className="w-3.5 h-3.5" />
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Right main panel: Show the MO analysis */}
            <div className="lg:col-span-2 space-y-6">
              {selectedCaseId ? (
                <div className="animate-fade-in space-y-4">
                  {/* Brief header showing active case */}
                  <div className="glass-card rounded-2xl border border-slate-800/65 p-4 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 rounded-xl">
                        <FileText className="w-5 h-5" />
                      </div>
                      <div>
                        <h4 className="text-sm font-bold text-slate-200">Analyzing Case Target #{selectedCaseId}</h4>
                        <p className="text-[11px] text-slate-550 font-mono mt-0.5">Loads TF-IDF cosine matching case patterns</p>
                      </div>
                    </div>
                    <button
                      onClick={() => setSelectedCaseId(null)}
                      className="px-2.5 py-1.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-slate-600 rounded-lg text-[10px] font-extrabold uppercase tracking-wide text-slate-400 transition-colors"
                    >
                      Clear Target
                    </button>
                  </div>
                  <FirModusOperandi caseId={selectedCaseId} />
                </div>
              ) : (
                <div className="glass-card rounded-2xl border border-slate-800/60 p-12 text-center text-slate-400 flex flex-col items-center justify-center gap-4 min-h-[400px]">
                  <Fingerprint className="w-16 h-16 text-indigo-505/40 animate-pulse" />
                  <div>
                    <h4 className="text-sm font-bold text-slate-200 uppercase tracking-wider">No Case Selected</h4>
                    <p className="text-xs text-slate-500 max-w-sm mt-1 mx-auto leading-relaxed">
                      Use the Target Case Selector on the left side to look up an FIR case, extract its behavioral footprint, and identify similar cases.
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 3: Offender Behavioral Profiles */}
        {activeTab === "offender-profiles" && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
            
            {/* Left list/search column */}
            <div className="glass-card rounded-2xl border border-slate-800/60 p-5 space-y-4 lg:col-span-1">
              <SectionHeader title="Offender Directory Lookup" accentColor="bg-violet-500" />
              
              <div className="space-y-3">
                <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-widest">
                  Search Accused by ID
                </label>
                <div className="flex gap-2">
                  <div className="relative flex-1">
                    <User className="absolute left-3 top-3 w-4 h-4 text-slate-500" />
                    <input
                      type="number"
                      placeholder="Enter Accused ID..."
                      value={offenderIdInput}
                      onChange={(e) => setOffenderIdInput(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && offenderIdInput && handleOffenderLookup(Number(offenderIdInput))}
                      className="w-full bg-slate-900/60 border border-slate-700/60 text-slate-200 text-xs rounded-xl pl-9 pr-3 py-2.5 focus:border-indigo-500 focus:outline-none transition-colors placeholder:text-slate-600"
                    />
                  </div>
                  <button
                    onClick={() => offenderIdInput && handleOffenderLookup(Number(offenderIdInput))}
                    disabled={!offenderIdInput}
                    className="px-4 py-2.5 bg-indigo-650 hover:bg-indigo-600 text-white text-xs font-bold uppercase tracking-wider rounded-xl transition-all disabled:opacity-50"
                  >
                    Lookup
                  </button>
                </div>
              </div>

              {/* Quick selectors for suspects featured in initial list */}
              <div className="pt-2 border-t border-slate-800/40">
                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-2">
                  Accused in Current Dataset
                </span>
                {discoveredSuspects.length === 0 ? (
                  <div className="text-xs text-slate-505 italic">No linked suspects indexed yet. Search cases in Case Tab first.</div>
                ) : (
                  <div className="space-y-1.5 max-h-[350px] overflow-y-auto pr-1">
                    {discoveredSuspects.map((suspect) => (
                      <button
                        key={suspect.id}
                        onClick={() => {
                          setOffenderIdInput(String(suspect.id));
                          handleOffenderLookup(suspect.id);
                        }}
                        className={`w-full text-left p-2.5 bg-slate-900/30 hover:bg-slate-900 border border-slate-800/40 hover:border-slate-700/60 rounded-xl text-xs transition-all flex flex-col gap-0.5 ${
                          offenderProfile && offenderProfile.accused_id === suspect.id
                            ? "border-violet-500 bg-violet-500/5 text-violet-400"
                            : "text-slate-350"
                        }`}
                      >
                        <span className="font-bold">{suspect.name}</span>
                        <span className="text-[10px] text-slate-500 font-mono">ID #{suspect.id} {suspect.caseNo ? `• Case: ${suspect.caseNo}` : ""}</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Right details column */}
            <div className="lg:col-span-2">
              {offenderLoading ? (
                <div className="glass-card rounded-2xl border border-slate-800/60 p-16 text-center text-slate-400 flex flex-col items-center justify-center gap-3 min-h-[400px]">
                  <Loader2 className="w-8 h-8 animate-spin text-violet-400" />
                  <span className="text-xs uppercase font-bold tracking-widest">Aggregating Offender Behavioral Signatures...</span>
                </div>
              ) : offenderError ? (
                <div className="glass-card rounded-2xl border border-red-500/20 bg-red-500/5 p-6 flex flex-col items-center justify-center gap-4 text-center min-h-[400px]">
                  <AlertTriangle className="w-12 h-12 text-red-500" />
                  <div>
                    <h4 className="text-sm font-bold text-slate-200">Accused Lookup Failed</h4>
                    <p className="text-xs text-slate-500 max-w-sm mt-1">{offenderError}</p>
                  </div>
                </div>
              ) : offenderProfile ? (
                <div className="glass-card rounded-2xl border border-slate-800/60 p-6 space-y-6 animate-fade-in">
                  
                  {/* Offender profile header */}
                  <div className="flex items-center justify-between border-b border-slate-800/60 pb-4">
                    <div className="flex items-center gap-3.5">
                      <div className="p-3 rounded-2xl bg-violet-500/10 border border-violet-500/20 text-violet-400">
                        <User className="w-6 h-6" />
                      </div>
                      <div>
                        <h3 className="text-lg font-black text-slate-100 tracking-tight">{offenderProfile.name}</h3>
                        <p className="text-xs text-slate-400 font-mono mt-0.5">
                          Accused ID: #{offenderProfile.accused_id} {offenderProfile.person_id ? `• Person ID: ${offenderProfile.person_id}` : ""}
                        </p>
                      </div>
                    </div>

                    <div className="text-right">
                      <span className="text-[9px] font-bold text-slate-500 uppercase tracking-wider block">
                        Linked Incidents
                      </span>
                      <span className="text-2xl font-black text-violet-455 font-mono">
                        {offenderProfile.total_associated_cases}
                      </span>
                    </div>
                  </div>

                  {/* Recurring signatures list */}
                  <div className="space-y-2">
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block">
                      Recurring MO Signatures
                    </span>
                    <div className="flex flex-wrap gap-2 pt-0.5">
                      {offenderProfile.recurring_mo_signatures.map((sig, idx) => (
                        <span
                          key={idx}
                          className="px-3 py-1 bg-violet-550/15 text-violet-350 border border-violet-500/25 rounded-xl text-xs font-semibold"
                        >
                          {sig}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Primary Crime Types & Districts */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                    <div className="p-4 bg-slate-900/40 rounded-xl border border-slate-800/50 space-y-2">
                      <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">
                        Primary Crime Groupings
                      </span>
                      <div className="flex flex-wrap gap-1.5">
                        {offenderProfile.primary_crime_types.map((t, idx) => (
                          <span key={idx} className="text-xs font-semibold text-slate-350 bg-slate-800/40 px-2 py-0.5 rounded border border-slate-700/30">
                            {t}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div className="p-4 bg-slate-900/40 rounded-xl border border-slate-800/50 space-y-2">
                      <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">
                        Operated Districts
                      </span>
                      <div className="flex flex-wrap gap-1.5">
                        {offenderProfile.primary_districts.map((d, idx) => (
                          <span key={idx} className="text-xs font-semibold text-slate-350 bg-slate-800/40 px-2 py-0.5 rounded border border-slate-700/30">
                            {d}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Case History Timeline */}
                  <div className="space-y-3">
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block">
                      Incident Association History
                    </span>
                    <div className="space-y-3 max-h-[300px] overflow-y-auto pr-1">
                      {offenderProfile.associated_cases.map((c) => (
                        <div
                          key={c.case_id}
                          className="bg-slate-900/35 hover:bg-slate-900/60 border border-slate-800/50 rounded-xl p-3.5 transition-colors flex items-center justify-between gap-4"
                        >
                          <div className="space-y-1 min-w-0">
                            <div className="flex items-center gap-2">
                              <span className="font-mono text-xs font-bold text-indigo-400">
                                {c.crime_no || `Case #${c.case_id}`}
                              </span>
                              <span className="text-slate-500 text-[10px]">({c.police_station}, {c.district})</span>
                            </div>
                            <div className="text-xs text-slate-400 font-semibold truncate">
                              Category: <span className="text-slate-355">{c.crime_type}</span>
                            </div>
                            <p className="text-[11px] text-slate-450 italic leading-relaxed truncate">
                              MO Summary: {c.mo_summary}
                            </p>
                          </div>
                          
                          <button
                            onClick={() => {
                              setSelectedCaseId(c.case_id);
                              setActiveTab("case-analyzer");
                            }}
                            className="text-xs font-bold text-indigo-400 hover:text-indigo-350 shrink-0 inline-flex items-center gap-0.5"
                          >
                            Analyze MO <ChevronRight className="w-4 h-4" />
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Disclaimers */}
                  <div className="p-3 bg-slate-900/30 border border-slate-800/50 rounded-xl flex items-start gap-2.5 mt-2">
                    <ShieldAlert className="w-4 h-4 text-violet-400 shrink-0 mt-0.5" />
                    <p className="text-[10px] text-slate-500 leading-relaxed italic">
                      {offenderProfile.interpretation_disclaimer}
                    </p>
                  </div>
                </div>
              ) : (
                <div className="glass-card rounded-2xl border border-slate-800/60 p-12 text-center text-slate-400 flex flex-col items-center justify-center gap-4 min-h-[400px]">
                  <Users className="w-16 h-16 text-violet-505/40 animate-pulse" />
                  <div>
                    <h4 className="text-sm font-bold text-slate-200 uppercase tracking-wider">No Offender Selected</h4>
                    <p className="text-xs text-slate-500 max-w-sm mt-1 mx-auto leading-relaxed">
                      Select an accused suspect from the quick-selection list on the left side, or type a known accused ID number to generate their aggregated behavioral signature.
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
        
      </div>
    </div>
  );
}
