"use client";

import { Bell, RefreshCw, Cpu, CheckCircle, LogOut } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { usePathname } from "next/navigation";

// Map routes to human-readable breadcrumbs
const BREADCRUMBS: Record<string, string> = {
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
  const { user, logout } = useAuth();
  const pathname = usePathname();
  const currentPage = BREADCRUMBS[pathname] || "Intelligence Platform";

  return (
    <header
      role="banner"
      className="h-14 border-b border-slate-800/60 bg-[#070b13]/90 backdrop-blur-md sticky top-0 z-40 px-6 flex items-center justify-between gap-4"
    >
      {/* Left: Status + Breadcrumb */}
      <div className="flex items-center gap-4 min-w-0">
        {/* API Status pill */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900/80 border border-slate-800/60 text-xs shrink-0">
          <Cpu className="w-3 h-3 text-indigo-400" />
          <span className="text-slate-500 font-medium hidden sm:inline">API</span>
          <span className="text-emerald-400 font-bold flex items-center gap-1">
            <CheckCircle className="w-2.5 h-2.5" />
            <span className="hidden sm:inline">Live</span>
          </span>
        </div>
        {/* Breadcrumb */}
        <div className="flex items-center gap-2 text-xs text-slate-500 min-w-0">
          <span className="text-slate-600 hidden sm:inline">Predictive Guardians</span>
          <span className="text-slate-700 hidden sm:inline">/</span>
          <span className="font-semibold text-slate-300 truncate">{currentPage}</span>
        </div>
      </div>

      {/* Right: Actions */}
      <div className="flex items-center gap-1 shrink-0">
        {/* Refresh */}
        <button
          onClick={() => window.location.reload()}
          aria-label="Refresh page data"
          title="Refresh Data"
          className="text-slate-500 hover:text-slate-200 transition-colors p-2 rounded-lg hover:bg-slate-800/60 focus-visible:ring-1 focus-visible:ring-indigo-500"
        >
          <RefreshCw className="w-4 h-4" />
        </button>

        {/* Notifications */}
        <div className="relative">
          <button
            aria-label="View notifications"
            className="text-slate-500 hover:text-slate-200 transition-colors p-2 rounded-lg hover:bg-slate-800/60 relative"
          >
            <Bell className="w-4 h-4" />
            <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 bg-indigo-500 rounded-full" aria-hidden="true" />
          </button>
        </div>

        <div className="h-5 w-px bg-slate-800 mx-1" />

        {/* User + Logout */}
        {user && (
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-slate-300 hidden md:inline max-w-[120px] truncate">
              {user.name}
            </span>
            <button
              onClick={logout}
              aria-label="Sign out of platform"
              title="Sign out"
              className="flex items-center gap-1.5 text-slate-500 hover:text-red-400 hover:bg-red-500/10 transition-all duration-200 px-3 py-1.5 rounded-lg border border-transparent hover:border-red-500/20 text-xs font-semibold cursor-pointer"
            >
              <LogOut className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Logout</span>
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
