"use client";

import { Bell, RefreshCw, Cpu, CheckCircle } from "lucide-react";

interface NavbarProps {
  role: string;
  onRoleChange: (newRole: string) => void;
}

export default function Navbar({ role, onRoleChange }: NavbarProps) {
  return (
    <header className="h-16 border-b border-[#1e293b]/50 bg-[#070b13]/85 backdrop-blur-md sticky top-0 z-40 px-8 flex items-center justify-between">
      {/* Search / Context */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900 border border-[#1e293b]/50 text-xs">
          <Cpu className="w-3.5 h-3.5 text-indigo-400" />
          <span className="text-slate-400 font-medium">Node API:</span>
          <span className="text-emerald-400 font-bold flex items-center gap-1">
            Connected <CheckCircle className="w-2.5 h-2.5 fill-emerald-400/20" />
          </span>
        </div>
      </div>

      {/* Right side items */}
      <div className="flex items-center gap-6">
        {/* Role Selector (Demo purpose) */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Demo Role:</span>
          <select
            value={role}
            onChange={(e) => onRoleChange(e.target.value)}
            className="bg-[#0f172a] border border-[#1e293b] text-indigo-400 text-xs font-bold rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-1 focus:ring-indigo-500 cursor-pointer"
          >
            <option value="OFFICER">Officer</option>
            <option value="SUPERINTENDENT">Superintendent</option>
            <option value="ADMIN">Admin</option>
          </select>
        </div>

        {/* Sync Trigger */}
        <button 
          onClick={() => window.location.reload()} 
          className="text-slate-400 hover:text-slate-200 transition-colors p-1.5 rounded-lg hover:bg-slate-800/40"
          title="Refresh Data"
        >
          <RefreshCw className="w-4 h-4" />
        </button>

        {/* Notifications */}
        <div className="relative">
          <button className="text-slate-400 hover:text-slate-200 transition-colors p-1.5 rounded-lg hover:bg-slate-800/40 relative">
            <Bell className="w-4 h-4" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-indigo-500 rounded-full animate-ping" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-indigo-500 rounded-full" />
          </button>
        </div>

        <div className="h-6 w-px bg-[#1e293b]" />

        {/* App Title Badge */}
        <span className="text-xs font-bold text-slate-300 bg-indigo-600/10 border border-indigo-500/20 px-3 py-1 rounded-full uppercase tracking-wider">
          Datathon 2026 Sandbox
        </span>
      </div>
    </header>
  );
}
