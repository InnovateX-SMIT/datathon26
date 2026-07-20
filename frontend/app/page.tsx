"use client";

import Link from "next/link";
import {
  ArrowRight,
  BarChart3,
  Bell,
  Database,
  FileSpreadsheet,
  FileText,
  FilePlus,
  Map,
  Network,
  Scale,
  ShieldAlert,
} from "lucide-react";

const modules = [
  {
    icon: BarChart3,
    label: "Command Center",
    desc: "Live KPIs, crime trends, district rankings, and recent incident feed.",
    href: "/dashboard",
    accent: "indigo",
  },
  {
    icon: FileText,
    label: "FIR Cases",
    desc: "Browse, search, and manage all registered First Information Reports.",
    href: "/fir/cases",
    accent: "indigo",
  },
  {
    icon: Map,
    label: "Geo Intelligence",
    desc: "Interactive district maps, station markers, crime heatmaps, and hotspot clusters.",
    href: "/geo",
    accent: "cyan",
  },
  {
    icon: Network,
    label: "Network Intelligence",
    desc: "Criminal co-accused relationship graphs and gang structure exploration.",
    href: "/network",
    accent: "violet",
  },

  {
    icon: Scale,
    label: "Decision Support",
    desc: "Tactical recommendations, LP-solver resource optimization, and patrol assignments.",
    href: "/decision-support",
    accent: "emerald",
  },
  {
    icon: FileSpreadsheet,
    label: "Executive Reports",
    desc: "Generate, print, and export structured intelligence dossiers.",
    href: "/reports",
    accent: "indigo",
  },
  {
    icon: Bell,
    label: "Alerts Panel",
    desc: "Operational alerts with severity triage and dispatch-oriented monitoring.",
    href: "/alerts",
    accent: "rose",
  },
  {
    icon: Database,
    label: "Dataset Manager",
    desc: "Upload, validate, activate, and govern datasets that power every module.",
    href: "/dataset-manager",
    accent: "violet",
  },
  {
    icon: FilePlus,
    label: "Register FIR",
    desc: "Create a new First Information Report directly into the active dataset.",
    href: "/fir/cases/new",
    accent: "indigo",
  },
];

const accentMap: Record<string, { bg: string; border: string; text: string; glow: string }> = {
  indigo: { bg: "bg-indigo-500/10", border: "border-indigo-500/20", text: "text-indigo-400", glow: "group-hover:border-indigo-500/40" },
  cyan: { bg: "bg-cyan-500/10", border: "border-cyan-500/20", text: "text-cyan-400", glow: "group-hover:border-cyan-500/40" },
  violet: { bg: "bg-violet-500/10", border: "border-violet-500/20", text: "text-violet-400", glow: "group-hover:border-violet-500/40" },
  emerald: { bg: "bg-emerald-500/10", border: "border-emerald-500/20", text: "text-emerald-400", glow: "group-hover:border-emerald-500/40" },
  rose: { bg: "bg-rose-500/10", border: "border-rose-500/20", text: "text-rose-400", glow: "group-hover:border-rose-500/40" },
};

export default function HomePage() {
  return (
    <div className="space-y-10 pb-12 animate-fade-in">

      {/* ── Hero ─────────────────────────────────────────────────────────── */}
      <section className="relative overflow-hidden rounded-2xl border border-slate-800/70 bg-slate-950/60 px-6 py-10 sm:px-10">
        {/* Dot grid background */}
        <div className="absolute inset-0 opacity-[0.07] bg-[radial-gradient(#6366f1_1px,transparent_1px)] [background-size:20px_20px] pointer-events-none" />
        {/* Ambient glow */}
        <div className="absolute -top-20 -right-20 w-80 h-80 rounded-full bg-indigo-600/10 blur-[80px] pointer-events-none" />

        <div className="relative flex flex-col lg:flex-row lg:items-center justify-between gap-8">
          <div className="max-w-2xl">
            <div className="inline-flex items-center gap-2 rounded-full border border-indigo-500/30 bg-indigo-500/10 px-3 py-1 text-[10px] font-black uppercase tracking-widest text-indigo-300 mb-4">
              <ShieldAlert className="h-3.5 w-3.5" />
              Crime Intelligence &amp; Decision Support Platform
            </div>

            <h1 className="text-4xl sm:text-5xl font-black tracking-tight text-white leading-tight">
              CrimeNexus 
            </h1>
            <p className="mt-4 text-sm leading-7 text-slate-400 max-w-xl">
              Unified operational intelligence for law enforcement connecting structured crime records into real-time dashboards, geospatial maps, network graphs, ML predictions, and executive dossiers.
            </p>

            <div className="mt-6 flex flex-wrap gap-3">
              <Link
                href="/dashboard"
                className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 px-5 py-2.5 text-xs font-black uppercase tracking-widest text-white shadow-lg shadow-indigo-600/20 transition-all"
              >
                Open Command Center
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                href="/dataset-manager"
                className="inline-flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-900/70 hover:border-indigo-500/40 hover:text-indigo-300 px-5 py-2.5 text-xs font-black uppercase tracking-widest text-slate-300 transition-all"
              >
                Dataset Manager
                <Database className="h-4 w-4" />
              </Link>
            </div>
          </div>

          {/* Quick stats */}
          <div className="grid grid-cols-2 gap-3 lg:min-w-[260px]">
            {[
              { label: "Modules", value: "9" },
              { label: "Active Datasets", value: "1+" },
              { label: "Map Layers", value: "4" },
              { label: "Report Types", value: "5+" },
            ].map(({ label, value }) => (
              <div key={label} className="rounded-xl border border-slate-800/80 bg-slate-950/70 p-4 text-center">
                <p className="text-2xl font-black text-indigo-400">{value}</p>
                <p className="mt-0.5 text-[10px] font-bold text-slate-500 uppercase tracking-widest">{label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Module Grid ──────────────────────────────────────────────────── */}
      <section className="space-y-4">
        <h2 className="text-xs font-black uppercase tracking-widest text-slate-500">Platform Modules</h2>
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">
          {modules.map(({ icon: Icon, label, desc, href, accent }) => {
            const a = accentMap[accent];
            return (
              <Link
                key={href}
                href={href}
                className={`group relative flex flex-col rounded-xl border border-slate-800/70 bg-slate-950/50 p-5 transition-all duration-200 hover:-translate-y-0.5 hover:bg-slate-950/80 ${a.glow}`}
              >
                <div className="flex items-start justify-between gap-3 mb-4">
                  <div className={`p-2.5 rounded-xl border ${a.bg} ${a.border} shrink-0`}>
                    <Icon className={`h-4.5 w-4.5 ${a.text}`} />
                  </div>
                  <ArrowRight className="h-4 w-4 text-slate-700 transition-colors group-hover:text-slate-400 mt-0.5" />
                </div>
                <h3 className="text-sm font-black uppercase tracking-wider text-slate-200 mb-1.5">{label}</h3>
                <p className="text-xs leading-5 text-slate-500">{desc}</p>
              </Link>
            );
          })}
        </div>
      </section>
    </div>
  );
}
