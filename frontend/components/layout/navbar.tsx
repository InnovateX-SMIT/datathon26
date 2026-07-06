"use client";

import { Bell, RefreshCw, Cpu, CheckCircle } from "lucide-react";
import { usePathname } from "next/navigation";

const BREADCRUMBS: Record<string, string> = {
  "/": "Get Started",
  "/dashboard": "Command Center",
  "/analytics": "Crime Analytics",
  "/geo": "Geo Intelligence",
  "/prediction": "Predictive Intel",
  "/network": "Network Intel",
  "/decision-support": "Decision Support",
  "/alerts": "Alerts Panel",
  "/reports": "Executive Reports",
  "/admin": "Admin Portal",
  "/database-management": "Database Management",
};

export default function Navbar() {
  const pathname = usePathname();
  const currentPage = BREADCRUMBS[pathname] || "Intelligence Platform";

  return (
    <header role="banner" className="h-14 border-b border-slate-800/60 bg-[#070b13]/90 backdrop-blur-md sticky top-0 z-40 px-6 flex items-center justify-between gap-4">
      <div className="flex items-center gap-4 min-w-0">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900/80 border border-slate-800/60 text-xs shrink-0">
          <Cpu className="w-3 h-3 text-indigo-400" />
          <span className="text-slate-500 font-medium hidden sm:inline">API</span>
          <span className="text-emerald-400 font-bold flex items-center gap-1">
            <CheckCircle className="w-2.5 h-2.5" />
            <span className="hidden sm:inline">Live</span>
          </span>
        </div>
        <div className="flex items-center gap-2 text-xs text-slate-500 min-w-0">
          <span className="text-slate-600 hidden sm:inline">Predictive Guardians</span>
          <span className="text-slate-700 hidden sm:inline">/</span>
          <span className="font-semibold text-slate-300 truncate">{currentPage}</span>
        </div>
      </div>

      <div className="flex items-center gap-1 shrink-0">
        <button onClick={() => window.location.reload()} aria-label="Refresh page data" title="Refresh Data" className="text-slate-500 hover:text-slate-200 transition-colors p-2 rounded-lg hover:bg-slate-800/60 focus-visible:ring-1 focus-visible:ring-indigo-500">
          <RefreshCw className="w-4 h-4" />
        </button>
        <button aria-label="View system alerts" title="System alerts" className="text-slate-500 hover:text-slate-200 transition-colors p-2 rounded-lg hover:bg-slate-800/60 relative">
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 bg-indigo-500 rounded-full" aria-hidden="true" />
        </button>
      </div>
    </header>
  );
}
