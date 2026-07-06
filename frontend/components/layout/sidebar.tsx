"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { useAuth } from "@/context/AuthContext";
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
  Lock,
  User,
  Database,
  Pin,
  PinOff
} from "lucide-react";

interface SidebarProps {
  role: string;
  onPinnedChange?: (pinned: boolean) => void;
}

export default function Sidebar({ role, onPinnedChange }: SidebarProps) {
  const pathname = usePathname();
  const { user } = useAuth();
  const [isPinned, setIsPinned] = useState(() => (typeof window !== "undefined" ? sessionStorage.getItem("datathon_sidebar_pinned") === "true" : false));
  const [isHovering, setIsHovering] = useState(false);

  useEffect(() => {
    onPinnedChange?.(isPinned);
  }, [isPinned, onPinnedChange]);

  const setPinnedPreference = (pinned: boolean) => {
    setIsPinned(pinned);
    sessionStorage.setItem("datathon_sidebar_pinned", String(pinned));
    onPinnedChange?.(pinned);
  };

  const isOpen = isPinned || isHovering;

  const menuItems = [
    { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard, roles: ["ADMIN", "SUPERINTENDENT", "OFFICER"] },
    { name: "Crime Analytics", href: "/analytics", icon: BarChart3, roles: ["ADMIN", "SUPERINTENDENT", "OFFICER"] },
    { name: "Geo Intelligence", href: "/geo", icon: Map, roles: ["ADMIN", "SUPERINTENDENT", "OFFICER"] },
    { name: "Predictive Intel", href: "/prediction", icon: BrainCircuit, roles: ["ADMIN", "SUPERINTENDENT", "OFFICER"] },
    { name: "Network Intel", href: "/network", icon: Network, roles: ["ADMIN", "SUPERINTENDENT", "OFFICER"] },
    { name: "Decision Support", href: "/decision-support", icon: Scale, roles: ["ADMIN", "SUPERINTENDENT"] },
    { name: "Alerts Panel", href: "/alerts", icon: Bell, roles: ["ADMIN", "SUPERINTENDENT", "OFFICER"] },
    { name: "Executive Reports", href: "/reports", icon: FileSpreadsheet, roles: ["ADMIN", "SUPERINTENDENT"] },
    { name: "Admin Portal", href: "/admin", icon: ShieldCheck, roles: ["ADMIN"] },
    { name: "Database Management", href: "/database-management", icon: Database, roles: ["ADMIN"] },
  ];

  const groups = [
    { label: "Operations", items: menuItems.filter(i => ["/dashboard", "/alerts"].includes(i.href)) },
    { label: "Intelligence", items: menuItems.filter(i => ["/analytics", "/geo", "/prediction", "/network", "/decision-support"].includes(i.href)) },
    { label: "Administration", items: menuItems.filter(i => ["/reports", "/admin", "/database-management"].includes(i.href)) },
  ];

  return (
    <>
      {!isPinned && (
        <div
          className="fixed left-0 top-0 z-50 h-screen w-4"
          onMouseEnter={() => setIsHovering(true)}
          aria-hidden="true"
        />
      )}
      <aside
        onMouseEnter={() => setIsHovering(true)}
        onMouseLeave={() => !isPinned && setIsHovering(false)}
        className={`fixed left-0 top-0 z-50 w-64 bg-[#0a0f1d]/98 border-r border-[#1e293b]/70 text-slate-300 flex flex-col h-screen shadow-2xl shadow-black/30 transition-transform duration-300 ease-out ${isOpen ? "translate-x-0" : "-translate-x-[calc(100%-10px)]"}`}
      >
        <div className="p-5 border-b border-[#1e293b]/50 flex items-center justify-between gap-3">
          <div className="flex items-center gap-3 min-w-0">
            <div className="bg-indigo-600/20 p-2 rounded-lg border border-indigo-500/30">
              <ShieldAlert className="w-6 h-6 text-indigo-400" />
            </div>
            <div className="min-w-0">
              <h1 className="font-bold text-sm text-slate-100 tracking-wider truncate">PREDICTIVE</h1>
              <p className="text-[10px] text-indigo-400 font-semibold tracking-widest">GUARDIANS</p>
            </div>
          </div>
          <button
            type="button"
            onClick={() => setPinnedPreference(!isPinned)}
            className="p-2 rounded-lg border border-slate-800 bg-slate-950/60 text-slate-500 hover:text-indigo-300 hover:border-indigo-500/30 transition-colors"
            aria-label={isPinned ? "Unpin sidebar" : "Pin sidebar"}
            title={isPinned ? "Unpin sidebar" : "Pin sidebar"}
          >
            {isPinned ? <PinOff className="w-4 h-4" /> : <Pin className="w-4 h-4" />}
          </button>
        </div>

        <nav className="flex-1 px-4 py-5 space-y-6 overflow-y-auto">
          {groups.map((group) => (
            <div key={group.label}>
              <div className="text-[9px] uppercase font-bold text-slate-600 tracking-widest px-3 mb-2">
                {group.label}
              </div>
              <div className="space-y-0.5">
                {group.items.map((item) => {
                  const isActive = pathname === item.href;
                  const hasAccess = item.roles.includes(role);
                  return (
                    <Link
                      key={item.href}
                      href={hasAccess ? item.href : "#"}
                      title={!hasAccess ? `Requires ${item.roles.filter(r => r !== "OFFICER").join(" or ")} clearance` : undefined}
                      aria-disabled={!hasAccess}
                      className={`flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 group ${
                        !hasAccess
                          ? "opacity-35 cursor-not-allowed pointer-events-none"
                          : isActive
                          ? "bg-indigo-600/10 text-indigo-400 border border-indigo-500/20 shadow-[inset_0_1px_0_rgba(99,102,241,0.1)]"
                          : "text-slate-400 hover:bg-slate-800/50 hover:text-slate-200 border border-transparent"
                      }`}
                    >
                      <div className="flex items-center gap-3 min-w-0">
                        <item.icon className={`w-4 h-4 transition-colors shrink-0 ${
                          isActive ? "text-indigo-400" : "text-slate-500 group-hover:text-slate-300"
                        }`} />
                        <span className="truncate">{item.name}</span>
                      </div>
                      {!hasAccess && <Lock className="w-3 h-3 text-slate-600 shrink-0" />}
                    </Link>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        <div className="p-4 border-t border-slate-800/60">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="bg-slate-800 p-2 rounded-lg border border-slate-700/60">
                <User className="w-3.5 h-3.5 text-slate-300" />
              </div>
              <span className="absolute bottom-0 right-0 w-2 h-2 bg-green-500 rounded-full border border-[#0a0f1d]" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-xs font-semibold text-slate-200 truncate">{user?.name || "OFFICER"}</p>
              <p className="text-[10px] text-indigo-400 font-bold truncate">{user?.role || role}</p>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}
