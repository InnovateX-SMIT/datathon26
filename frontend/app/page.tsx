"use client";

import Link from "next/link";
import {
  ArrowRight,
  BarChart3,
  Bell,
  BrainCircuit,
  Database,
  FileSpreadsheet,
  GitBranch,
  Layers3,
  Map,
  Network,
  Rocket,
  Scale,
  ShieldAlert,
  ShieldCheck,
  UploadCloud,
  Workflow
} from "lucide-react";

const workflow = [
  ["Upload Dataset", "CSV or Excel records enter the platform through managed import."],
  ["Dataset Validation", "Headers, required fields, districts, dates, and stations are checked before import."],
  ["Dataset Registry", "Every dataset is tracked with status, row counts, summaries, and provenance."],
  ["Activate Dataset", "The active dataset becomes the single source for analytics and intelligence modules."],
  ["Dashboard Updates", "KPIs, temporal trends, categories, districts, and recent incidents refresh dynamically."],
  ["Geo Intelligence", "District, station, heatmap, and hotspot maps render from active records."],
  ["Network Intelligence", "Criminal, crime, and location relationships are explored as interactive graphs."],
  ["Predictions", "ML models generate crime risk, type, hotspot, and repeat-offender forecasts."],
  ["Decision Support", "Recommendations and resource allocation support operational planning."],
  ["Executive Reports", "Structured intelligence dossiers combine analytics, risks, networks, and alerts."],
  ["Deployment Ready Intelligence", "The result is a polished command experience ready for live demonstration."],
];

const features = [
  [LayoutDashboardIcon, "Dashboard", "Live command overview for KPIs, temporal trends, category distribution, district load, and latest incidents.", "/dashboard"],
  [Database, "Dataset Registry", "Upload, validate, register, activate, summarize, and govern datasets from one operational control surface.", "/admin"],
  [Map, "Geo Intelligence", "Interactive district maps, station markers, heat density, hotspot detection, and fullscreen map investigation.", "/geo"],
  [Network, "Network Intelligence", "Explore offender-to-crime and crime-to-location links with active-dataset-aware graph lookups.", "/network"],
  [BrainCircuit, "Prediction Engine", "Run repeat-offender, hotspot, crime risk, and crime type predictions with explainability output.", "/prediction"],
  [Scale, "Decision Support", "Convert intelligence into recommended actions, tactical triage, and resource optimization scenarios.", "/decision-support"],
  [FileSpreadsheet, "Executive Reports", "Generate and export executive-ready intelligence dossiers for leadership review and judging.", "/reports"],
  [Bell, "Alert System", "Review generated operational alerts, severity, status, source signals, and dispatch-oriented monitoring.", "/alerts"],
  [Layers3, "Database Management", "Inspect, upload, export, and manage operational tables through a controlled data workspace.", "/database-management"],
  [ShieldCheck, "Administration", "Monitor platform health, models, datasets, users, and audit activity from the admin portal.", "/admin"],
];

const howTo = [
  "Upload a dataset",
  "Activate the dataset",
  "Explore the dashboard",
  "Analyze geo intelligence",
  "Explore criminal networks",
  "Generate predictions",
  "Generate executive reports",
  "Use decision support"
];

function LayoutDashboardIcon(props: React.ComponentProps<typeof BarChart3>) {
  return <BarChart3 {...props} />;
}

export default function AboutPage() {
  return (
    <div className="min-h-screen pb-12 space-y-10 animate-fade-in">
      <section className="relative overflow-hidden rounded-2xl border border-slate-800/70 bg-slate-950/50 px-6 py-8 sm:px-8 lg:px-10">
        <div className="absolute inset-0 opacity-10 bg-[radial-gradient(#6366f1_1px,transparent_1px)] [background-size:18px_18px] pointer-events-none" />
        <div className="relative grid gap-8 lg:grid-cols-[1.25fr_0.75fr] lg:items-center">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-indigo-500/25 bg-indigo-500/10 px-3 py-1 text-[10px] font-black uppercase tracking-widest text-indigo-300">
              <ShieldAlert className="h-3.5 w-3.5" />
              Enterprise Crime Intelligence Platform
            </div>
            <h1 className="mt-5 max-w-4xl text-4xl font-black tracking-tight text-white sm:text-5xl">
              CrimeNexus AI
            </h1>
            <p className="mt-4 max-w-3xl text-sm leading-7 text-slate-300">
              CrimeNexus AI transforms structured crime records into operational intelligence: dashboards, geospatial analysis, criminal network graphs, prediction workflows, decision support, alerts, and executive reports. It is designed as a deployment-ready command platform for data-driven law enforcement planning and hackathon demonstration.
            </p>
            <div className="mt-6 flex flex-wrap gap-3">
              <Link href="/dashboard" className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-5 py-3 text-xs font-black uppercase tracking-widest text-white shadow-lg transition-colors hover:bg-indigo-500">
                Open Dashboard
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link href="/admin" className="inline-flex items-center gap-2 rounded-xl border border-slate-800 bg-slate-950/70 px-5 py-3 text-xs font-black uppercase tracking-widest text-slate-300 transition-colors hover:border-indigo-500/40 hover:text-indigo-300">
                Manage Datasets
                <UploadCloud className="h-4 w-4" />
              </Link>
            </div>
          </div>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-1">
            {[
              [Database, "Active Dataset Core", "Every module reads from the Dataset Resolver."],
              [BrainCircuit, "AI Capability", "Prediction and explainability workflows are built in."],
              [Rocket, "Deployment Ready", "Optimized build, public entry, and clean module flow."],
            ].map(([Icon, title, text]) => {
              const TypedIcon = Icon as typeof Database;
              return (
                <div key={title as string} className="rounded-xl border border-slate-800/80 bg-slate-950/70 p-4">
                  <TypedIcon className="h-5 w-5 text-indigo-400" />
                  <h3 className="mt-3 text-sm font-black uppercase tracking-wider text-slate-200">{title as string}</h3>
                  <p className="mt-1 text-xs leading-5 text-slate-500">{text as string}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      <section className="space-y-4">
        <div className="flex items-center gap-3">
          <Workflow className="h-5 w-5 text-indigo-400" />
          <h2 className="text-xl font-black uppercase tracking-tight text-slate-100">Complete Project Workflow</h2>
        </div>
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {workflow.map(([title, desc], index) => (
            <div key={title} className="relative rounded-xl border border-slate-800/70 bg-slate-950/45 p-4 transition-colors hover:border-indigo-500/30">
              <div className="flex items-start gap-3">
                <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-indigo-500/25 bg-indigo-500/10 text-xs font-black text-indigo-300">{index + 1}</span>
                <div>
                  <h3 className="text-sm font-black uppercase tracking-wider text-slate-200">{title}</h3>
                  <p className="mt-1 text-xs leading-5 text-slate-500">{desc}</p>
                </div>
              </div>
              {index < workflow.length - 1 && <GitBranch className="absolute right-4 top-4 h-4 w-4 text-slate-700" />}
            </div>
          ))}
        </div>
      </section>

      <section className="space-y-4">
        <h2 className="text-xl font-black uppercase tracking-tight text-slate-100">Feature Surface</h2>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {features.map(([Icon, title, desc, href]) => {
            const TypedIcon = Icon as typeof Database;
            return (
              <Link key={title as string} href={href as string} className="group rounded-xl border border-slate-800/70 bg-slate-950/45 p-5 transition-all hover:-translate-y-0.5 hover:border-indigo-500/35 hover:bg-slate-950/70">
                <div className="flex items-start justify-between gap-3">
                  <div className="rounded-lg border border-slate-800 bg-slate-950 p-2 text-indigo-400 group-hover:border-indigo-500/30">
                    <TypedIcon className="h-5 w-5" />
                  </div>
                  <ArrowRight className="h-4 w-4 text-slate-700 transition-colors group-hover:text-indigo-400" />
                </div>
                <h3 className="mt-4 text-sm font-black uppercase tracking-wider text-slate-200">{title as string}</h3>
                <p className="mt-2 text-xs leading-5 text-slate-500">{desc as string}</p>
              </Link>
            );
          })}
        </div>
      </section>

      <section className="rounded-2xl border border-slate-800/70 bg-slate-950/45 p-6">
        <h2 className="text-xl font-black uppercase tracking-tight text-slate-100">How To Use</h2>
        <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {howTo.map((item, index) => (
            <div key={item} className="rounded-xl border border-slate-800 bg-[#0a0f1d] p-4">
              <span className="text-[10px] font-black uppercase tracking-widest text-indigo-400">Step {index + 1}</span>
              <p className="mt-2 text-sm font-bold text-slate-200">{item}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
