"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import {
  ShieldAlert,
  LayoutDashboard,
  BarChart3,
  Map,
  BrainCircuit,
  Network,
  Scale,
  Bell,
  FileSpreadsheet,
  ShieldCheck,
  Database,
  Pin,
  PinOff,
  Sparkles,
  Layers
} from "lucide-react";

interface SidebarProps {
  onPinnedChange?: (pinned: boolean) => void;
}

const menuItems = [
  { name: "Get Started", href: "/", icon: Sparkles, group: "Start" },
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard, group: "Operations" },
  { name: "Alerts Panel", href: "/alerts", icon: Bell, group: "Operations" },
  { name: "Crime Analytics", href: "/analytics", icon: BarChart3, group: "Intelligence" },
  { name: "Geo Intelligence", href: "/geo", icon: Map, group: "Intelligence" },
  { name: "Predictive Intel", href: "/prediction", icon: BrainCircuit, group: "Intelligence" },
  { name: "Network Intel", href: "/network", icon: Network, group: "Intelligence" },
  { name: "Decision Support", href: "/decision-support", icon: Scale, group: "Intelligence" },
  { name: "Executive Reports", href: "/reports", icon: FileSpreadsheet, group: "Administration" },
  { name: "Admin Portal", href: "/admin", icon: ShieldCheck, group: "Administration" },
  { name: "Dataset Manager", href: "/dataset-manager", icon: Layers, group: "Administration" },
  { name: "ML Model Manager", href: "/admin/models", icon: BrainCircuit, group: "Administration" },
  { name: "Database Management", href: "/database-management", icon: Database, group: "Administration" },
];

const groups = ["Start", "Operations", "Intelligence", "Administration"];

export default function Sidebar({ onPinnedChange }: SidebarProps) {
  const pathname = usePathname();
  const [isPinned, setIsPinned] = useState(() => (typeof window !== "undefined" ? sessionStorage.getItem("datathon_sidebar_pinned") === "true" : false));
  const [isHovering, setIsHovering] = useState(false);
  const isOpen = isPinned || isHovering;

  useEffect(() => {
    onPinnedChange?.(isPinned);
  }, [isPinned, onPinnedChange]);

  const setPinnedPreference = (pinned: boolean) => {
    setIsPinned(pinned);
    sessionStorage.setItem("datathon_sidebar_pinned", String(pinned));
    onPinnedChange?.(pinned);
  };

  return (
    <aside
      onMouseEnter={() => setIsHovering(true)}
      onMouseLeave={() => !isPinned && setIsHovering(false)}
      className={`fixed left-0 top-0 z-50 h-screen bg-[#0a0f1d]/98 border-r border-[#1e293b]/70 text-slate-300 flex flex-col shadow-2xl shadow-black/30 transition-[width] duration-300 ease-out ${isOpen ? "w-64" : "w-[4.5rem]"}`}
    >
      <div className={`border-b border-[#1e293b]/50 flex items-center gap-3 ${isOpen ? "p-5 justify-between" : "px-3 py-5 justify-center"}`}>
        <div className="flex items-center gap-3 min-w-0">
          <div className="bg-indigo-600/20 p-2 rounded-lg border border-indigo-500/30 shrink-0">
            <ShieldAlert className="w-6 h-6 text-indigo-400" />
          </div>
          {isOpen && (
            <div className="min-w-0">
              <h1 className="font-bold text-sm text-slate-100 tracking-wider truncate">PREDICTIVE</h1>
              <p className="text-[10px] text-indigo-400 font-semibold tracking-widest">GUARDIANS</p>
            </div>
          )}
        </div>
        {isOpen && (
          <button
            type="button"
            onClick={() => setPinnedPreference(!isPinned)}
            className="p-2 rounded-lg border border-slate-800 bg-slate-950/60 text-slate-500 hover:text-indigo-300 hover:border-indigo-500/30 transition-colors"
            aria-label={isPinned ? "Unpin sidebar" : "Pin sidebar"}
            title={isPinned ? "Unpin sidebar" : "Pin sidebar"}
          >
            {isPinned ? <PinOff className="w-4 h-4" /> : <Pin className="w-4 h-4" />}
          </button>
        )}
      </div>

      <nav className={`flex-1 py-4 overflow-y-auto ${isOpen ? "px-4 space-y-6" : "px-2 space-y-4"}`}>
        {groups.map((group) => {
          const items = menuItems.filter((item) => item.group === group);
          return (
            <div key={group}>
              {isOpen && <div className="text-[9px] uppercase font-bold text-slate-600 tracking-widest px-3 mb-2">{group}</div>}
              <div className="space-y-1">
                {items.map((item) => {
                  const isActive = pathname === item.href;
                  const Icon = item.icon;
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      title={item.name}
                      aria-label={item.name}
                      className={`flex items-center rounded-lg text-sm font-medium transition-all duration-200 group border ${
                        isOpen ? "justify-start gap-3 px-3 py-2.5" : "justify-center h-11 w-11 mx-auto"
                      } ${
                        isActive
                          ? "bg-indigo-600/10 text-indigo-400 border-indigo-500/20 shadow-[inset_0_1px_0_rgba(99,102,241,0.1)]"
                          : "text-slate-400 hover:bg-slate-800/50 hover:text-slate-200 border-transparent"
                      }`}
                    >
                      <Icon className={`w-4 h-4 transition-colors shrink-0 ${isActive ? "text-indigo-400" : "text-slate-500 group-hover:text-slate-300"}`} />
                      {isOpen && <span className="truncate">{item.name}</span>}
                    </Link>
                  );
                })}
              </div>
            </div>
          );
        })}
      </nav>

      <div className={`border-t border-slate-800/60 ${isOpen ? "p-4" : "p-3"}`}>
        {isOpen ? (
          <div className="rounded-xl border border-slate-800 bg-slate-950/50 px-3 py-2">
            <p className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">Public Deployment</p>
            <p className="text-xs text-slate-300 font-semibold mt-0.5">No login required</p>
          </div>
        ) : (
          <button
            type="button"
            onClick={() => setPinnedPreference(!isPinned)}
            className="h-11 w-11 mx-auto flex items-center justify-center rounded-lg border border-slate-800 bg-slate-950/60 text-slate-500 hover:text-indigo-300 hover:border-indigo-500/30 transition-colors"
            aria-label={isPinned ? "Unpin sidebar" : "Pin sidebar"}
            title={isPinned ? "Unpin sidebar" : "Pin sidebar"}
          >
            {isPinned ? <PinOff className="w-4 h-4" /> : <Pin className="w-4 h-4" />}
          </button>
        )}
      </div>
    </aside>
  );
}
