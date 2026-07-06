"use client";

import React, { useCallback, useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import Sidebar from "./sidebar";
import Navbar from "./navbar";
import { useAuth } from "@/context/AuthContext";
import { ShieldX, ArrowLeft, Loader2, ShieldAlert } from "lucide-react";

export default function ClientLayout({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const pathname = usePathname();
  const router = useRouter();
  const [sidebarPinned, setSidebarPinned] = useState(false);
  const handleSidebarPinnedChange = useCallback((pinned: boolean) => {
    setSidebarPinned(pinned);
  }, []);

  const isLoginPage = pathname === "/login";

  // Redirect users dynamically inside useEffect to avoid rendering-time updates
  useEffect(() => {
    if (!loading) {
      if (!user && !isLoginPage) {
        router.push("/login");
      } else if (user && isLoginPage) {
        router.push("/dashboard");
      }
    }
  }, [user, loading, isLoginPage, router]);

  // Premium loading screen
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-[#070b13] text-slate-100">
        <div className="relative flex flex-col items-center justify-center p-8 glass-card rounded-2xl max-w-sm w-full border border-indigo-500/20 shadow-2xl">
          <div className="absolute inset-0 opacity-10 bg-[radial-gradient(#6366f1_1px,transparent_1px)] [background-size:16px_16px] pointer-events-none" />
          <div className="bg-indigo-600/10 p-3 rounded-full border border-indigo-500/30 mb-4 animate-pulse">
            <ShieldAlert className="w-8 h-8 text-indigo-400" />
          </div>
          <Loader2 className="w-8 h-8 text-indigo-400 animate-spin mb-4" />
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-200">Verifying Identity</h2>
          <p className="text-[11px] text-slate-500 mt-1">Connecting to Secure Intel Grid...</p>
        </div>
      </div>
    );
  }

  // If not logged in and on protected page, show loading during redirect
  if (!user && !isLoginPage) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-[#070b13] text-slate-100">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="w-6 h-6 text-indigo-400 animate-spin" />
          <p className="text-xs text-slate-500 font-medium">Redirecting...</p>
        </div>
      </div>
    );
  }

  // If logged in and goes to /login, show loading during redirect
  if (user && isLoginPage) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-[#070b13] text-slate-100">
        <Loader2 className="w-8 h-8 text-indigo-400 animate-spin" />
      </div>
    );
  }

  // If on login page and not authenticated, just render form directly without layout
  if (isLoginPage) {
    return <>{children}</>;
  }

  // Role Access Control validation
  const userRole = user?.role || "OFFICER";
  let hasAccess = true;

  if (pathname.startsWith("/admin") && userRole !== "ADMIN") {
    hasAccess = false;
  } else if (pathname.startsWith("/database-management") && userRole !== "ADMIN") {
    hasAccess = false;
  } else if (pathname.startsWith("/reports") && !["ADMIN", "SUPERINTENDENT"].includes(userRole)) {
    hasAccess = false;
  } else if (pathname.startsWith("/decision-support") && !["ADMIN", "SUPERINTENDENT"].includes(userRole)) {
    hasAccess = false;
  }

  return (
    <div className="flex h-screen overflow-hidden bg-[#070b13] text-slate-100 font-sans">
      {/* Sidebar Navigation */}
      <Sidebar role={userRole} onPinnedChange={handleSidebarPinnedChange} />

      {/* Main Content Area */}
      <div className={`flex flex-col flex-1 min-w-0 overflow-hidden transition-[padding] duration-300 ${sidebarPinned ? "pl-64" : "pl-3"}`}>
        {/* Top Navbar */}
        <Navbar />

        {/* Dynamic Route View */}
        <main className="flex-1 overflow-y-auto px-8 py-8 relative bg-radial from-[#0d1527] to-[#070b13] animate-fade-in">
          {hasAccess ? (
            children
          ) : (
            // Premium Access Denied View
            <div className="flex flex-col items-center justify-center min-h-[70vh] animate-fade-in">
              <div className="glass-card max-w-md w-full p-8 rounded-2xl border border-red-500/20 shadow-[0_0_50px_-12px_rgba(239,68,68,0.2)] text-center relative overflow-hidden">
                <div className="absolute inset-0 opacity-5 bg-[radial-gradient(#ef4444_1px,transparent_1px)] [background-size:16px_16px] pointer-events-none" />
                
                <div className="mx-auto bg-red-500/10 border border-red-500/25 p-4 rounded-full w-fit mb-6 shadow-[0_0_20px_rgba(239,68,68,0.1)]">
                  <ShieldX className="w-10 h-10 text-red-500 animate-bounce" />
                </div>
                
                <h1 className="text-xl font-black uppercase tracking-wider text-red-500">Access Restricted</h1>
                <p className="text-xs font-bold text-slate-400 mt-1.5">UNAUTHORIZED COMMAND LEVEL</p>
                
                <div className="p-4 bg-slate-950/40 border border-slate-900 rounded-xl mt-6 text-xs text-slate-400 leading-relaxed">
                  Your identity clearance level (<span className="text-red-400 font-bold">{userRole}</span>) does not permit access to the module at <span className="text-slate-300 font-mono">{pathname}</span>. Contact Platform Administration if this is an error.
                </div>
                
                <button
                  onClick={() => router.push("/dashboard")}
                  className="mt-6 inline-flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700/60 font-semibold px-5 py-2.5 rounded-lg text-xs transition-all duration-200 cursor-pointer shadow-md hover:shadow-indigo-500/10"
                >
                  <ArrowLeft className="w-4 h-4" />
                  Return to Dashboard
                </button>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
