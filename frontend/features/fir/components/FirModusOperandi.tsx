"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  Fingerprint,
  Layers,
  ArrowRight,
  ShieldAlert,
  Clock,
  MapPin,
  Crosshair,
  UserCheck,
  Building,
  Key,
  Flame,
  AlertTriangle,
  Info,
  Loader2,
  ExternalLink,
  ChevronRight,
  X,
} from "lucide-react";
import SectionHeader from "@/components/layout/section-header";
import { getCaseMO, getOffenderMOProfile } from "../services/firApi";
import type {
  MOProfileResponse,
  SimilarCaseMatch,
  OffenderBehavioralProfileResponse,
} from "../types/mo";

interface FirModusOperandiProps {
  caseId: number;
}

export default function FirModusOperandi({ caseId }: FirModusOperandiProps) {
  const [moData, setMoData] = useState<MOProfileResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Selected offender modal state
  const [selectedOffenderId, setSelectedOffenderId] = useState<number | null>(null);
  const [offenderProfile, setOffenderProfile] = useState<OffenderBehavioralProfileResponse | null>(null);
  const [loadingOffender, setLoadingOffender] = useState(false);

  const [reloadTrigger, setReloadTrigger] = useState(0);

  useEffect(() => {
    let cancelled = false;
    async function loadMO() {
      setLoading(true);
      setError(null);
      try {
        const data = await getCaseMO(caseId);
        if (!cancelled) {
          setMoData(data);
        }
      } catch (err: unknown) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load MO profile");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    loadMO();
    return () => {
      cancelled = true;
    };
  }, [caseId, reloadTrigger]);

  const handleOpenOffenderProfile = async (accusedId: number) => {
    setSelectedOffenderId(accusedId);
    setLoadingOffender(true);
    try {
      const data = await getOffenderMOProfile(accusedId);
      setOffenderProfile(data);
    } catch {
      setOffenderProfile(null);
    } finally {
      setLoadingOffender(false);
    }
  };

  if (loading) {
    return (
      <div className="glass-card rounded-xl border border-slate-800/60 p-6 flex items-center justify-center min-h-[180px]">
        <div className="flex items-center gap-3 text-slate-400">
          <Loader2 className="w-5 h-5 animate-spin text-indigo-400" />
          <span className="text-sm font-medium">Extracting Modus Operandi & Behavioral Patterns...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass-card rounded-xl border border-red-500/20 p-5 bg-red-500/5">
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-3 text-red-400 text-xs font-semibold">
            <AlertTriangle className="w-5 h-5 shrink-0" />
            <span>Failed to load Modus Operandi profile: {error}</span>
          </div>
          <button
            onClick={() => setReloadTrigger((prev) => prev + 1)}
            className="px-3 py-1.5 bg-red-600/80 hover:bg-red-500 text-white rounded-lg text-xs font-bold uppercase tracking-wider transition-all"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!moData) {
    return (
      <div className="glass-card rounded-xl border border-slate-800/60 p-5 text-center text-slate-400 text-xs">
        No Modus Operandi data available for this case.
      </div>
    );
  }

  const attrs = moData.attributes;
  const hasExtractedAttrs = Object.values(attrs).some((v) => Boolean(v));

  return (
    <div className="space-y-6">
      {/* ── Section Header ──────────────────────────────────────────────────── */}
      <div className="glass-card rounded-xl border border-slate-800/60 p-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-violet-500/10 border border-violet-500/20 text-violet-400">
              <Fingerprint className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-extrabold text-slate-100 tracking-tight flex items-center gap-2">
                Modus Operandi & Behavioral Intelligence
              </h3>
              <p className="text-[11px] text-slate-400 font-medium">
                Structured behavioral extraction & cross-case similarity engine
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {moData.is_sufficient ? (
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                MO Profile Extracted
              </span>
            ) : (
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider bg-amber-500/10 text-amber-400 border border-amber-500/20">
                <AlertTriangle className="w-3 h-3" />
                Insufficient Facts Narrative
              </span>
            )}
          </div>
        </div>

        {/* Narrative Summary */}
        <div className="bg-slate-900/40 rounded-xl p-4 border border-slate-800/60 space-y-3">
          <div className="flex items-start gap-2.5">
            <Info className="w-4 h-4 text-violet-400 shrink-0 mt-0.5" />
            <div>
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block">
                Extracted Behavioral Summary
              </span>
              <p className="text-sm font-semibold text-slate-200 mt-0.5 leading-relaxed">
                {moData.mo_summary}
              </p>
            </div>
          </div>

          {/* Behavioral Tags */}
          {moData.behavioral_tags.length > 0 && (
            <div className="flex flex-wrap items-center gap-1.5 pt-2 border-t border-slate-800/40">
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mr-1">
                Behavioral Tags:
              </span>
              {moData.behavioral_tags.map((tag, idx) => (
                <span
                  key={idx}
                  className="px-2.5 py-0.5 bg-violet-500/10 text-violet-300 border border-violet-500/20 rounded-md text-[11px] font-medium"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* ── Extracted Behavioral Attributes Matrix ────────────────────────── */}
        {hasExtractedAttrs && (
          <div className="mt-4 pt-4 border-t border-slate-800/40">
            <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-3">
              Behavioral Dimensions Breakdown
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {attrs.entry_method && (
                <div className="p-3 bg-slate-900/30 rounded-lg border border-slate-800/50 flex items-start gap-2.5">
                  <Key className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                  <div>
                    <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">
                      Entry / Breach Method
                    </span>
                    <p className="text-xs font-semibold text-slate-200 mt-0.5">{attrs.entry_method}</p>
                  </div>
                </div>
              )}

              {attrs.weapon_tool && (
                <div className="p-3 bg-slate-900/30 rounded-lg border border-slate-800/50 flex items-start gap-2.5">
                  <ShieldAlert className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                  <div>
                    <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">
                      Weapon / Tool / Vector
                    </span>
                    <p className="text-xs font-semibold text-slate-200 mt-0.5">{attrs.weapon_tool}</p>
                  </div>
                </div>
              )}

              {attrs.target_type && (
                <div className="p-3 bg-slate-900/30 rounded-lg border border-slate-800/50 flex items-start gap-2.5">
                  <Crosshair className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
                  <div>
                    <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">
                      Target Classification
                    </span>
                    <p className="text-xs font-semibold text-slate-200 mt-0.5">{attrs.target_type}</p>
                  </div>
                </div>
              )}

              {attrs.time_pattern && (
                <div className="p-3 bg-slate-900/30 rounded-lg border border-slate-800/50 flex items-start gap-2.5">
                  <Clock className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
                  <div>
                    <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">
                      Temporal Pattern
                    </span>
                    <p className="text-xs font-semibold text-slate-200 mt-0.5">{attrs.time_pattern}</p>
                  </div>
                </div>
              )}

              {attrs.approach_method && (
                <div className="p-3 bg-slate-900/30 rounded-lg border border-slate-800/50 flex items-start gap-2.5">
                  <Layers className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
                  <div>
                    <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">
                      Modus / Approach
                    </span>
                    <p className="text-xs font-semibold text-slate-200 mt-0.5">{attrs.approach_method}</p>
                  </div>
                </div>
              )}

              {attrs.escape_method && (
                <div className="p-3 bg-slate-900/30 rounded-lg border border-slate-800/50 flex items-start gap-2.5">
                  <Flame className="w-4 h-4 text-orange-400 shrink-0 mt-0.5" />
                  <div>
                    <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">
                      Evasion / Getaway Method
                    </span>
                    <p className="text-xs font-semibold text-slate-200 mt-0.5">{attrs.escape_method}</p>
                  </div>
                </div>
              )}

              {attrs.location_type && (
                <div className="p-3 bg-slate-900/30 rounded-lg border border-slate-800/50 flex items-start gap-2.5">
                  <Building className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                  <div>
                    <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">
                      Location Context
                    </span>
                    <p className="text-xs font-semibold text-slate-200 mt-0.5">{attrs.location_type}</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* ── Behaviorally Similar Cases ───────────────────────────────────────── */}
      <div className="glass-card rounded-xl border border-slate-800/60 p-5">
        <SectionHeader
          title={`Behaviorally Similar Cases (${moData.similar_cases.length})`}
          accentColor="bg-indigo-500"
        />

        {moData.similar_cases.length === 0 ? (
          <div className="p-6 text-center text-slate-400 bg-slate-900/20 rounded-xl border border-slate-800/40">
            <p className="text-xs italic">No behaviorally similar cases above threshold found in current dataset.</p>
          </div>
        ) : (
          <div className="space-y-3 mt-2">
            {moData.similar_cases.map((sim) => (
              <div
                key={sim.case_id}
                className="bg-slate-900/40 hover:bg-slate-900/70 transition-all rounded-xl p-4 border border-slate-800/60 flex flex-col md:flex-row md:items-center justify-between gap-4"
              >
                <div className="space-y-1.5 min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="font-mono text-sm font-bold text-indigo-300">
                      {sim.crime_no || `Case #${sim.case_id}`}
                    </span>
                    <span className="px-2 py-0.5 bg-slate-800 text-slate-300 text-[10px] font-bold uppercase rounded">
                      {sim.crime_type}
                    </span>
                    {sim.is_cross_jurisdiction ? (
                      <span className="px-2 py-0.5 bg-amber-500/10 text-amber-300 border border-amber-500/20 text-[10px] font-extrabold uppercase tracking-wide rounded">
                        Cross-Jurisdiction ({sim.district})
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 bg-cyan-500/10 text-cyan-300 border border-cyan-500/20 text-[10px] font-extrabold uppercase tracking-wide rounded">
                        Local Jurisdiction
                      </span>
                    )}
                  </div>

                  <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-400">
                    <span className="inline-flex items-center gap-1">
                      <MapPin className="w-3 h-3 text-slate-500" />
                      {sim.police_station}, {sim.district}
                    </span>
                    {sim.registered_date && (
                      <span className="inline-flex items-center gap-1">
                        <Clock className="w-3 h-3 text-slate-500" />
                        {sim.registered_date}
                      </span>
                    )}
                  </div>

                  {/* Matching traits */}
                  {sim.matching_attributes.length > 0 && (
                    <div className="flex flex-wrap items-center gap-1 pt-1">
                      <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider">
                        Matching Traits:
                      </span>
                      {sim.matching_attributes.map((trait, tIdx) => (
                        <span
                          key={tIdx}
                          className="px-2 py-0.2 bg-indigo-500/10 text-indigo-300 rounded text-[10px] font-medium border border-indigo-500/20"
                        >
                          {trait}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Associated suspects */}
                  {sim.associated_suspects.length > 0 && (
                    <div className="flex flex-wrap items-center gap-1.5 pt-1">
                      <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">
                        Linked Suspects:
                      </span>
                      {sim.associated_suspects.map((s) => (
                        <button
                          key={s.accused_id}
                          onClick={() => handleOpenOffenderProfile(s.accused_id)}
                          className="inline-flex items-center gap-1 px-2 py-0.5 bg-violet-500/10 hover:bg-violet-500/20 text-violet-300 rounded text-[10px] font-medium border border-violet-500/20 transition-colors cursor-pointer"
                        >
                          <UserCheck className="w-2.5 h-2.5" />
                          {s.name}
                        </button>
                      ))}
                    </div>
                  )}
                </div>

                {/* Similarity Score & View Action */}
                <div className="flex items-center gap-3 shrink-0 self-end md:self-center">
                  <div className="text-right">
                    <div className="text-lg font-black text-indigo-400 font-mono">
                      {sim.similarity_percentage}%
                    </div>
                    <span className="text-[9px] font-bold text-slate-500 uppercase tracking-wider block">
                      TF-IDF Cosine Match
                    </span>
                  </div>

                  <Link
                    href={`/fir/cases/${sim.case_id}`}
                    className="p-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl transition-all shadow-md hover:shadow-indigo-500/20"
                    title="Inspect Similar Case"
                  >
                    <ArrowRight className="w-4 h-4" />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Investigative Interpretation Disclaimer */}
        <div className="mt-4 p-3 rounded-lg bg-slate-900/40 border border-slate-800/50 flex items-start gap-2.5">
          <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
          <p className="text-[11px] text-slate-400 leading-relaxed font-medium">
            <strong className="text-slate-300">Investigative Intelligence Disclaimer: </strong>
            {moData.interpretation_disclaimer}
          </p>
        </div>
      </div>

      {/* ── Offender Behavioral Profile Modal ───────────────────────────────── */}
      {selectedOffenderId && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-card rounded-2xl border border-indigo-500/20 p-6 max-w-xl w-full max-h-[85vh] overflow-y-auto space-y-4 relative shadow-2xl">
            <button
              onClick={() => setSelectedOffenderId(null)}
              className="absolute top-4 right-4 text-slate-400 hover:text-slate-200 p-1"
            >
              <X className="w-5 h-5" />
            </button>

            {loadingOffender ? (
              <div className="py-12 flex flex-col items-center justify-center gap-3 text-slate-400">
                <Loader2 className="w-6 h-6 animate-spin text-indigo-400" />
                <span className="text-xs font-bold uppercase tracking-wider">
                  Analyzing Offender Behavioral Patterns...
                </span>
              </div>
            ) : offenderProfile ? (
              <div className="space-y-4">
                <div className="flex items-center gap-3 border-b border-slate-800/60 pb-3">
                  <div className="p-2.5 rounded-xl bg-violet-500/10 border border-violet-500/20 text-violet-400">
                    <UserCheck className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-slate-100">{offenderProfile.name}</h3>
                    <p className="text-xs text-slate-400 font-mono">
                      Associated with {offenderProfile.total_associated_cases} Case(s) on record
                    </p>
                  </div>
                </div>

                {/* Recurring MO Signatures */}
                <div>
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block mb-1.5">
                    Recurring Behavioral Signatures
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {offenderProfile.recurring_mo_signatures.map((sig, sIdx) => (
                      <span
                        key={sIdx}
                        className="px-2.5 py-1 bg-violet-500/15 text-violet-300 border border-violet-500/30 rounded-lg text-xs font-semibold"
                      >
                        {sig}
                      </span>
                    ))}
                  </div>
                </div>

                {/* History list */}
                <div>
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block mb-1.5">
                    Associated Cases History
                  </span>
                  <div className="space-y-2 max-h-48 overflow-y-auto">
                    {offenderProfile.associated_cases.map((c) => (
                      <div
                        key={c.case_id}
                        className="p-2.5 bg-slate-900/60 rounded-lg border border-slate-800/40 text-xs flex justify-between items-center"
                      >
                        <div>
                          <span className="font-mono font-bold text-indigo-400">{c.crime_no || `#${c.case_id}`}</span>
                          <span className="text-slate-400 ml-2">({c.crime_type})</span>
                          <p className="text-[10px] text-slate-500">{c.police_station}, {c.district}</p>
                        </div>
                        <Link
                          href={`/fir/cases/${c.case_id}`}
                          className="text-xs text-indigo-400 hover:text-indigo-300 font-semibold inline-flex items-center gap-1"
                        >
                          View <ChevronRight className="w-3.5 h-3.5" />
                        </Link>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-800/40 text-[10px] text-slate-500 font-medium italic">
                  {offenderProfile.interpretation_disclaimer}
                </div>
              </div>
            ) : (
              <p className="text-xs text-slate-400 py-6 text-center">Failed to load profile details.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
