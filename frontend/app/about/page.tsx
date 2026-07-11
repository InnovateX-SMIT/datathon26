"use client";

import {
  Users,
  ShieldAlert,
  BrainCircuit,
  Map,
  Network,
  Scale,
  BarChart3,
  Award,
  ExternalLink,
} from "lucide-react";

const teamMembers = [
  { name: "Krish Anand", role: "Team Leader", initial: "K" },
  { name: "Abhinav Puri", role: "Team Member", initial: "A" },
  { name: "Debojit Deb", role: "Team Member", initial: "D" },
  { name: "Dishaba Siddhrajsinh Zala", role: "Team Member", initial: "D" },
  { name: "Shreya Singh", role: "Team Member", initial: "S" },
];

const techStack = [
  { label: "Next.js", desc: "Frontend framework & UI" },
  { label: "FastAPI", desc: "Backend REST API" },
  { label: "PostgreSQL", desc: "Relational database" },
  { label: "Machine Learning", desc: "XGBoost prediction models" },
  { label: "Leaflet / GeoJSON", desc: "Geospatial mapping" },
  { label: "Recharts", desc: "Data visualization" },
];

const capabilities = [
  { icon: BarChart3, label: "Predictive Analytics", color: "text-indigo-400", bg: "bg-indigo-500/10 border-indigo-500/20" },
  { icon: Map, label: "Hotspot Detection", color: "text-cyan-400", bg: "bg-cyan-500/10 border-cyan-500/20" },
  { icon: Network, label: "Criminal Network Intelligence", color: "text-violet-400", bg: "bg-violet-500/10 border-violet-500/20" },
  { icon: Scale, label: "Resource Optimization", color: "text-emerald-400", bg: "bg-emerald-500/10 border-emerald-500/20" },
  { icon: BrainCircuit, label: "AI Decision Support", color: "text-indigo-400", bg: "bg-indigo-500/10 border-indigo-500/20" },
  { icon: ShieldAlert, label: "Proactive Policing", color: "text-rose-400", bg: "bg-rose-500/10 border-rose-500/20" },
];

export default function AboutPage() {
  return (
    <div className="space-y-8 pb-12 animate-fade-in max-w-5xl">

      {/* ── Page Header ──────────────────────────────────────────────────── */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/70 pb-6">
        <div className="flex items-center gap-3.5">
          <div className="p-2.5 bg-indigo-500/10 border border-indigo-500/20 rounded-xl shrink-0">
            <Users className="w-5 h-5 text-indigo-400" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-slate-100 uppercase tracking-tight leading-tight">
              About Us
            </h1>
            <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-widest mt-0.5">
              Team InnovateX · SMIT · Datathon 2026
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 px-4 py-2.5 bg-indigo-500/10 border border-indigo-500/20 rounded-2xl self-start">
          <Award className="w-4 h-4 text-indigo-400" />
          <span className="text-indigo-400 text-xs font-black uppercase tracking-wider">
            Datathon 2026
          </span>
        </div>
      </div>

      {/* ── Hero Card ────────────────────────────────────────────────────── */}
      <section className="relative overflow-hidden rounded-2xl border border-slate-800/70 bg-slate-950/60 px-6 py-8 sm:px-8">
        <div className="absolute inset-0 opacity-[0.06] bg-[radial-gradient(#6366f1_1px,transparent_1px)] [background-size:20px_20px] pointer-events-none" />
        <div className="absolute -top-16 -right-16 w-64 h-64 rounded-full bg-indigo-600/8 blur-[60px] pointer-events-none" />

        <div className="relative space-y-4 max-w-3xl">
          <div className="inline-flex items-center gap-2 rounded-full border border-indigo-500/30 bg-indigo-500/10 px-3 py-1 text-[10px] font-black uppercase tracking-widest text-indigo-300">
            <ShieldAlert className="h-3.5 w-3.5" />
            AI-Powered Crime Intelligence &amp; Decision Support Platform
          </div>

          <p className="text-sm leading-7 text-slate-300">
            We are <span className="font-bold text-slate-100">Team InnovateX</span> from{" "}
            <span className="font-bold text-indigo-300">Sikkim Manipal Institute of Technology (SMIT)</span>,
            participating in <span className="font-bold text-slate-100">Datathon 2026</span>. We are a team of
            passionate undergrads dedicated to building innovative, AI-driven solutions that address
            real-world challenges in public safety and law enforcement.
          </p>

          <p className="text-sm leading-7 text-slate-400">
            Our project leverages Artificial Intelligence, Machine Learning, Data Analytics, Geospatial
            Intelligence, and Interactive Dashboards to transform fragmented crime data into actionable
            intelligence — empowering law enforcement agencies with predictive analytics, hotspot detection,
            criminal network intelligence, resource optimization, and data-driven decision support.
          </p>
        </div>
      </section>

      {/* ── Core Capabilities ────────────────────────────────────────────── */}
      <section className="space-y-4">
        <h2 className="text-xs font-black uppercase tracking-widest text-slate-500">Platform Capabilities</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {capabilities.map(({ icon: Icon, label, color, bg }) => (
            <div
              key={label}
              className="flex items-center gap-3 rounded-xl border border-slate-800/70 bg-slate-950/50 px-4 py-3"
            >
              <div className={`p-2 rounded-lg border shrink-0 ${bg}`}>
                <Icon className={`w-4 h-4 ${color}`} />
              </div>
              <span className="text-xs font-semibold text-slate-300 leading-tight">{label}</span>
            </div>
          ))}
        </div>
      </section>

      {/* ── Team Members ─────────────────────────────────────────────────── */}
      <section className="space-y-4">
        <h2 className="text-xs font-black uppercase tracking-widest text-slate-500">The Team</h2>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {teamMembers.map(({ name, role, initial }, idx) => (
            <div
              key={name}
              className="flex items-center gap-4 rounded-xl border border-slate-800/70 bg-slate-950/50 px-4 py-4 transition-colors hover:border-indigo-500/30"
            >
              <div className="w-10 h-10 rounded-xl bg-indigo-600/20 border border-indigo-500/25 flex items-center justify-center text-sm font-black text-indigo-300 shrink-0">
                {initial}
              </div>
              <div className="min-w-0">
                <p className="text-sm font-bold text-slate-200 truncate">{name}</p>
                <p className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold mt-0.5">
                  {idx === 0 ? (
                    <span className="text-indigo-400">{role}</span>
                  ) : (
                    role
                  )}
                </p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── Tech Stack ───────────────────────────────────────────────────── */}
      <section className="space-y-4">
        <h2 className="text-xs font-black uppercase tracking-widest text-slate-500">Technology Stack</h2>
        <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
          {techStack.map(({ label, desc }) => (
            <div
              key={label}
              className="flex items-start gap-3 rounded-xl border border-slate-800/70 bg-slate-950/50 px-4 py-3"
            >
              <div className="w-1.5 h-1.5 rounded-full bg-indigo-500 mt-1.5 shrink-0" />
              <div>
                <span className="text-xs font-black text-slate-200 uppercase tracking-wider">{label}</span>
                <p className="text-[11px] text-slate-500 mt-0.5">{desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── Copyright Footer ─────────────────────────────────────────────── */}
      <div className="rounded-xl border border-slate-800/60 bg-slate-950/40 px-5 py-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <p className="text-[11px] text-slate-500 leading-relaxed">
          Copyright ©️ 2026{" "}
          <span className="font-bold text-slate-300">Team InnovateX</span>,{" "}
          <span className="font-semibold text-slate-400">Sikkim Manipal Institute of Technology (SMIT)</span>.
          All rights reserved.
        </p>
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full border border-indigo-500/20 bg-indigo-500/10 text-indigo-400 text-[10px] font-bold uppercase tracking-widest shrink-0">
          <ExternalLink className="w-3 h-3" />
          Datathon 2026
        </span>
      </div>
    </div>
  );
}
