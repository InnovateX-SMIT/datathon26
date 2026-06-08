"use client";

import React, { useState, useEffect } from "react";
import Sidebar from "./sidebar";
import Navbar from "./navbar";

export default function ClientLayout({ children }: { children: React.ReactNode }) {
  const [role, setRole] = useState<string>("SUPERINTENDENT");

  // Load from localStorage on client side
  useEffect(() => {
    const savedRole = localStorage.getItem("demo-role");
    if (savedRole) {
      setRole(savedRole);
    }
  }, []);

  const handleRoleChange = (newRole: string) => {
    setRole(newRole);
    localStorage.setItem("demo-role", newRole);
    // Reload or trigger dynamic changes
    window.dispatchEvent(new Event("role-changed"));
  };

  return (
    <div className="flex h-screen overflow-hidden bg-[#070b13] text-slate-100 font-sans">
      {/* Sidebar Navigation */}
      <Sidebar role={role} />

      {/* Main Content Area */}
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        {/* Top Navbar */}
        <Navbar role={role} onRoleChange={handleRoleChange} />

        {/* Dynamic Route View */}
        <main className="flex-1 overflow-y-auto px-8 py-8 relative bg-radial from-[#0d1527] to-[#070b13]">
          {children}
        </main>
      </div>
    </div>
  );
}
