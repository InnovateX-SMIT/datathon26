"use client";

import React, { useCallback, useState } from "react";
import Sidebar from "./sidebar";
import Navbar from "./navbar";

export default function ClientLayout({ children }: { children: React.ReactNode }) {
  const [sidebarPinned, setSidebarPinned] = useState(false);
  const handleSidebarPinnedChange = useCallback((pinned: boolean) => {
    setSidebarPinned(pinned);
  }, []);

  return (
    <div className="flex h-screen overflow-hidden bg-[#070b13] text-slate-100 font-sans">
      <Sidebar onPinnedChange={handleSidebarPinnedChange} />
      <div className={`flex flex-col flex-1 min-w-0 overflow-hidden transition-[padding] duration-300 ${sidebarPinned ? "pl-64" : "pl-[4.5rem]"}`}>
        <Navbar />
        <main className="flex-1 overflow-y-auto px-8 py-8 relative bg-radial from-[#0d1527] to-[#070b13] animate-fade-in">
          {children}
        </main>
      </div>
    </div>
  );
}
