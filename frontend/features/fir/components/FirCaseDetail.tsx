"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  AlertCircle,
  Loader2,
  FileText,
  MapPin,
  Users,
  UserX,
  Scale,
  ShieldAlert,
  Gavel,
  Clock,
  RefreshCw,
} from "lucide-react";
import SectionHeader from "@/components/layout/section-header";
import { getCase, deleteCase } from "../services/firApi";
import { useFirLookups } from "../hooks/useFirLookups";
import type { CaseMasterResponse } from "../types/fir";

// ── Shared styling ──────────────────────────────────────────────────────────
const labelCls = "text-[10px] font-bold text-slate-500 uppercase tracking-wider";
const valueCls = "text-sm text-slate-200 font-medium mt-0.5";
const cardCls = "glass-card rounded-xl border border-slate-800/60 p-5";

function FieldPair({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div>
      <span className={labelCls}>{label}</span>
      <p className={valueCls}>{value || "—"}</p>
    </div>
  );
}

interface FirCaseDetailProps {
  caseId: number;
}

export default function FirCaseDetail({ caseId }: FirCaseDetailProps) {
  const [caseData, setCaseData] = useState<CaseMasterResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);
  const { lookups } = useFirLookups();

  const handleDelete = async () => {
    if (!window.confirm("Are you sure you want to permanently delete this case?")) return;
    setDeleting(true);
    try {
      await deleteCase(caseId);
      alert("Case deleted successfully.");
      window.location.href = "/fir/cases";
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "Failed to delete case");
      setDeleting(false);
    }
  };

  const loadCase = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getCase(caseId);
      setCaseData(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load case");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCase();
  }, [caseId]);

  // ── Lookup resolver helpers ─────────────────────────────────────────────
  const resolveLookup = (list: { id: number; name: string }[] | undefined, id: number | null | undefined) =>
    list?.find((x) => x.id === id)?.name ?? (id != null ? `#${id}` : "—");

  const formatDatetime = (dt: string | null | undefined) => {
    if (!dt) return "—";
    try {
      return new Date(dt).toLocaleString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return dt;
    }
  };

  const formatDate = (dt: string | null | undefined) => {
    if (!dt) return "—";
    try {
      return new Date(dt).toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric",
      });
    } catch {
      return dt;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[500px]">
        <div className="flex items-center gap-3 text-slate-400">
          <Loader2 className="w-5 h-5 animate-spin" />
          <span className="text-sm font-medium">Loading case details...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[500px] text-center space-y-4">
        <AlertCircle className="w-12 h-12 text-red-500 animate-pulse" />
        <p className="text-sm text-slate-300">{error}</p>
        <button
          onClick={loadCase}
          className="flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs uppercase tracking-wider rounded-xl transition-colors cursor-pointer"
        >
          <RefreshCw className="w-3.5 h-3.5" /> Retry
        </button>
      </div>
    );
  }

  if (!caseData) return null;

  const c = caseData;
  const occ = c.occurrence_time;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Back button */}
      <Link
        href="/fir/cases"
        className="inline-flex items-center gap-2 text-xs font-bold text-slate-400 hover:text-indigo-400 transition-colors uppercase tracking-wider"
      >
        <ArrowLeft className="w-4 h-4" /> Back to Case List
      </Link>

      {/* ── Header Banner ──────────────────────────────────────────────────── */}
      <div className="glass-card rounded-2xl border border-indigo-500/20 p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-xl bg-indigo-500/10 border border-indigo-500/20">
              <FileText className="w-6 h-6 text-indigo-400" />
            </div>
            <div>
              <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">
                FIR Case #{c.id}
              </p>
              <h2 className="text-xl font-black text-slate-100 tracking-tight mt-0.5">
                {c.CrimeNo || "Crime No Pending"}
              </h2>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right">
              <span className={labelCls}>Case No</span>
              <p className="text-sm font-mono text-indigo-400 font-bold mt-0.5">
                {c.CaseNo || "—"}
              </p>
            </div>
            <div className="text-right">
              <span className={labelCls}>Registered</span>
              <p className="text-sm font-mono text-slate-300 mt-0.5">
                {formatDate(c.CrimeRegisteredDate)}
              </p>
            </div>
            <div className="flex items-center gap-2 border-l border-slate-800/80 pl-4 ml-2">
              <a
                href={`/fir/cases/${c.id}/edit`}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs uppercase tracking-wider rounded-xl transition-all shadow-lg hover:shadow-indigo-500/20"
              >
                Edit
              </a>
              <button
                onClick={handleDelete}
                disabled={deleting}
                className="px-4 py-2 bg-rose-600/80 hover:bg-rose-500 hover:text-white text-rose-100 font-bold text-xs uppercase tracking-wider rounded-xl transition-all border border-rose-500/30 disabled:opacity-50 cursor-pointer shadow-lg hover:shadow-rose-500/20"
              >
                {deleting ? "Deleting..." : "Delete"}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* ── Case Registration Details ──────────────────────────────────────── */}
      <div className={cardCls}>
        <SectionHeader title="Case Registration" accentColor="bg-indigo-500" />
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          <FieldPair label="Case Category" value={resolveLookup(lookups?.caseCategories, c.CaseCategoryID)} />
          <FieldPair label="Gravity of Offence" value={resolveLookup(lookups?.gravityOffences, c.GravityOffenceID)} />
          <FieldPair
            label="Crime Major Head"
            value={lookups?.crimeHeads.find((h) => h.id === c.CrimeMajorHeadID)?.CrimeGroupName ?? `#${c.CrimeMajorHeadID}`}
          />
          <FieldPair label="Crime Minor Head" value={`#${c.CrimeMinorHeadID}`} />
          <FieldPair label="Case Status" value={resolveLookup(lookups?.caseStatuses, c.CaseStatusID)} />
          <FieldPair label="Police Station (Unit)" value={`#${c.PoliceStationID}`} />
          <FieldPair label="Investigating Officer" value={`#${c.PolicePersonID}`} />
          <FieldPair label="Court" value={`#${c.CourtID}`} />
        </div>
        {c.BriefFacts && (
          <div className="mt-4 pt-4 border-t border-slate-800/40">
            <span className={labelCls}>Brief Facts</span>
            <p className="text-sm text-slate-300 leading-relaxed mt-1">{c.BriefFacts}</p>
          </div>
        )}
      </div>

      {/* ── Occurrence Details ──────────────────────────────────────────────── */}
      {occ && (
        <div className={cardCls}>
          <SectionHeader title="Occurrence Details" accentColor="bg-cyan-500" />
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            <FieldPair label="Incident From" value={formatDatetime(occ.IncidentFromDate)} />
            <FieldPair label="Incident To" value={formatDatetime(occ.IncidentToDate)} />
            <FieldPair label="Info Received at PS" value={formatDatetime(occ.InfoReceivedPSDate)} />
            <FieldPair
              label="Coordinates"
              value={
                occ.latitude && occ.longitude ? (
                  <span className="inline-flex items-center gap-1">
                    <MapPin className="w-3 h-3 text-cyan-400" />
                    {occ.latitude.toFixed(4)}, {occ.longitude.toFixed(4)}
                  </span>
                ) : (
                  "—"
                )
              }
            />
          </div>
          {occ.BriefFacts && (
            <div className="mt-4 pt-4 border-t border-slate-800/40">
              <span className={labelCls}>Occurrence Details</span>
              <p className="text-sm text-slate-300 leading-relaxed mt-1">{occ.BriefFacts}</p>
            </div>
          )}
        </div>
      )}

      {/* ── Complainants ───────────────────────────────────────────────────── */}
      <div className={cardCls}>
        <SectionHeader title={`Complainant(s) — ${c.complainants.length}`} accentColor="bg-amber-500" />
        {c.complainants.length === 0 ? (
          <p className="text-xs text-slate-500 italic">No complainants recorded.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {c.complainants.map((comp) => (
              <div key={comp.id} className="bg-slate-900/30 rounded-lg p-3 border border-slate-800/40 flex items-start gap-3">
                <div className="p-2 rounded-lg bg-amber-500/10 border border-amber-500/20 shrink-0">
                  <Users className="w-4 h-4 text-amber-400" />
                </div>
                <div className="min-w-0 flex-1 grid grid-cols-2 gap-x-4 gap-y-1">
                  <FieldPair label="Name" value={comp.ComplainantName} />
                  <FieldPair label="Age" value={comp.AgeYear != null ? `${comp.AgeYear} yrs` : "—"} />
                  <FieldPair label="Gender" value={resolveLookup(lookups?.genders, comp.GenderID)} />
                  <FieldPair label="Caste" value={resolveLookup(lookups?.castes, comp.CasteID)} />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ── Victims ────────────────────────────────────────────────────────── */}
      <div className={cardCls}>
        <SectionHeader title={`Victim(s) — ${c.victims.length}`} accentColor="bg-red-500" />
        {c.victims.length === 0 ? (
          <p className="text-xs text-slate-500 italic">No victims recorded.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {c.victims.map((vic) => (
              <div key={vic.id} className="bg-slate-900/30 rounded-lg p-3 border border-slate-800/40 flex items-start gap-3">
                <div className="p-2 rounded-lg bg-red-500/10 border border-red-500/20 shrink-0">
                  <ShieldAlert className="w-4 h-4 text-red-400" />
                </div>
                <div className="min-w-0 flex-1 grid grid-cols-2 gap-x-4 gap-y-1">
                  <FieldPair label="Name" value={vic.VictimName} />
                  <FieldPair label="Age" value={vic.AgeYear != null ? `${vic.AgeYear} yrs` : "—"} />
                  <FieldPair label="Gender" value={resolveLookup(lookups?.genders, vic.GenderID)} />
                  <FieldPair label="Victim is Police" value={vic.VictimPolice === "1" ? "Yes" : "No"} />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ── Accused ────────────────────────────────────────────────────────── */}
      <div className={cardCls}>
        <SectionHeader title={`Accused Person(s) — ${c.accused.length}`} accentColor="bg-violet-500" />
        {c.accused.length === 0 ? (
          <p className="text-xs text-slate-500 italic">No accused persons recorded.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {c.accused.map((acc) => (
              <div key={acc.id} className="bg-slate-900/30 rounded-lg p-3 border border-slate-800/40 flex items-start gap-3">
                <div className="p-2 rounded-lg bg-violet-500/10 border border-violet-500/20 shrink-0">
                  <UserX className="w-4 h-4 text-violet-400" />
                </div>
                <div className="min-w-0 flex-1 grid grid-cols-2 gap-x-4 gap-y-1">
                  <FieldPair label="Name" value={acc.AccusedName} />
                  <FieldPair label="Person ID" value={acc.PersonID || "—"} />
                  <FieldPair label="Age" value={acc.AgeYear != null ? `${acc.AgeYear} yrs` : "—"} />
                  <FieldPair label="Gender" value={resolveLookup(lookups?.genders, acc.GenderID)} />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ── Act/Section Associations ───────────────────────────────────────── */}
      <div className={cardCls}>
        <SectionHeader title={`Act & Section — ${c.act_sections.length}`} accentColor="bg-emerald-500" />
        {c.act_sections.length === 0 ? (
          <p className="text-xs text-slate-500 italic">No act/section associations recorded.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-800">
                  <th className="px-3 py-2 text-[10px] font-bold text-slate-500 uppercase tracking-wider">#</th>
                  <th className="px-3 py-2 text-[10px] font-bold text-slate-500 uppercase tracking-wider">Act Code</th>
                  <th className="px-3 py-2 text-[10px] font-bold text-slate-500 uppercase tracking-wider">Section Code</th>
                  <th className="px-3 py-2 text-[10px] font-bold text-slate-500 uppercase tracking-wider">Order</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/30">
                {c.act_sections.map((as, idx) => (
                  <tr key={idx} className="hover:bg-slate-800/20 transition-colors">
                    <td className="px-3 py-2 text-xs text-slate-500 font-mono">{idx + 1}</td>
                    <td className="px-3 py-2 text-xs text-emerald-400 font-mono font-bold">{as.ActCode}</td>
                    <td className="px-3 py-2 text-xs text-slate-300 font-mono">{as.SectionCode}</td>
                    <td className="px-3 py-2 text-xs text-slate-500 font-mono">{as.ActOrderID ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* ── Arrest/Surrender ───────────────────────────────────────────────── */}
      <div className={cardCls}>
        <SectionHeader title={`Arrest / Surrender — ${c.arrest_surrenders.length}`} accentColor="bg-orange-500" />
        {c.arrest_surrenders.length === 0 ? (
          <p className="text-xs text-slate-500 italic">No arrest/surrender records.</p>
        ) : (
          <div className="grid grid-cols-1 gap-3">
            {c.arrest_surrenders.map((ar) => (
              <div key={ar.id} className="bg-slate-900/30 rounded-lg p-3 border border-slate-800/40 flex items-start gap-3">
                <div className="p-2 rounded-lg bg-orange-500/10 border border-orange-500/20 shrink-0">
                  <Gavel className="w-4 h-4 text-orange-400" />
                </div>
                <div className="min-w-0 flex-1 grid grid-cols-2 md:grid-cols-4 gap-x-4 gap-y-1">
                  <FieldPair label="Date" value={formatDate(ar.ArrestSurrenderDate)} />
                  <FieldPair label="Accused" value={`#${ar.AccusedMasterID}`} />
                  <FieldPair label="Is Accused" value={ar.IsAccused ? "Yes" : "No"} />
                  <FieldPair label="Court" value={`#${ar.CourtID}`} />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ── Chargesheet ────────────────────────────────────────────────────── */}
      <div className={cardCls}>
        <SectionHeader title={`Chargesheet — ${c.chargesheets.length}`} accentColor="bg-sky-500" />
        {c.chargesheets.length === 0 ? (
          <p className="text-xs text-slate-500 italic">No chargesheet filed yet.</p>
        ) : (
          <div className="grid grid-cols-1 gap-3">
            {c.chargesheets.map((cs) => (
              <div key={cs.id} className="bg-slate-900/30 rounded-lg p-3 border border-slate-800/40 flex items-start gap-3">
                <div className="p-2 rounded-lg bg-sky-500/10 border border-sky-500/20 shrink-0">
                  <Scale className="w-4 h-4 text-sky-400" />
                </div>
                <div className="min-w-0 flex-1 grid grid-cols-2 md:grid-cols-3 gap-x-4 gap-y-1">
                  <FieldPair label="Date" value={formatDatetime(cs.csdate)} />
                  <FieldPair label="Type" value={cs.cstype} />
                  <FieldPair label="Officer" value={`#${cs.PolicePersonID}`} />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ── Metadata ───────────────────────────────────────────────────────── */}
      <div className="flex items-center justify-center gap-4 text-[10px] text-slate-600 font-mono py-4 border-t border-slate-800/30">
        <span className="flex items-center gap-1">
          <Clock className="w-3 h-3" /> Created: {formatDatetime(c.created_at)}
        </span>
        <span>•</span>
        <span>Updated: {formatDatetime(c.updated_at)}</span>
      </div>
    </div>
  );
}
