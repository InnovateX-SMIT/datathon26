"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
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
  User
} from "lucide-react";

interface SidebarProps {
  role: string;
}

export default function Sidebar({ role }: SidebarProps) {
  const pathname = usePathname();

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
  ];

  return (
    <aside className="w-64 bg-[#0a0f1d] border-r border-[#1e293b]/50 text-slate-300 flex flex-col h-screen sticky top-0">
      {/* Brand Section */}
      <div className="p-6 border-b border-[#1e293b]/50 flex items-center gap-3">
        <div className="bg-indigo-600/20 p-2 rounded-lg border border-indigo-500/30">
          <ShieldAlert className="w-6 h-6 text-indigo-400 animate-pulse" />
        </div>
        <div>
          <h1 className="font-bold text-sm text-slate-100 tracking-wider">PREDICTIVE</h1>
          <p className="text-[10px] text-indigo-400 font-semibold tracking-widest">GUARDIANS</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-1.5 overflow-y-auto">
        <div className="text-[10px] uppercase font-bold text-slate-500 tracking-widest px-3 mb-3">
          Intelligence Suite
        </div>
        {menuItems.map((item) => {
          const isActive = pathname === item.href;
          const hasAccess = item.roles.includes(role);

          return (
            <Link
              key={item.href}
              href={hasAccess ? item.href : "#"}
              className={`flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 group ${
                !hasAccess
                  ? "opacity-40 cursor-not-allowed"
                  : isActive
                  ? "bg-indigo-600/10 text-indigo-400 border border-indigo-500/25 shadow-[0_0_15px_-3px_rgba(99,102,241,0.2)]"
                  : "hover:bg-slate-800/40 hover:text-slate-100 border border-transparent"
              }`}
            >
              <div className="flex items-center gap-3">
                <item.icon className={`w-4 h-4 transition-colors ${
                  isActive ? "text-indigo-400" : "text-slate-400 group-hover:text-slate-200"
                }`} />
                <span>{item.name}</span>
              </div>
              
              {!hasAccess && (
                <Lock className="w-3.5 h-3.5 text-slate-500" />
              )}
            </Link>
          );
        })}
      </nav>

      {/* Footer Info */}
      <div className="p-4 border-t border-[#1e293b]/50 bg-slate-900/20">
        <div className="flex items-center gap-3">
          <div className="bg-slate-800 p-2 rounded-full border border-slate-700">
            <User className="w-4 h-4 text-slate-300" />
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-xs font-semibold text-slate-200 truncate">DATATHON OFFICER</p>
            <p className="text-[10px] text-indigo-400 font-bold truncate">ROLE: {role}</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
