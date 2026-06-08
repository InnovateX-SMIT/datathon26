"use client";

import React from "react";
import { ShieldCheck, UserCheck, Key, Settings } from "lucide-react";

export default function AdminPortal() {
  const users = [
    { name: "Superintendent A", email: "sp@police.gov.in", role: "SUPERINTENDENT", status: "active" },
    { name: "Officer B", email: "officer@police.gov.in", role: "OFFICER", status: "active" },
    { name: "Admin C", email: "admin@police.gov.in", role: "ADMIN", status: "active" },
  ];

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div>
        <span className="text-xs font-bold text-indigo-400 uppercase tracking-widest px-2.5 py-1 bg-indigo-500/10 border border-indigo-500/20 rounded-full">
          Supervisory Suite
        </span>
        <h1 className="text-3xl font-extrabold tracking-tight mt-2 text-slate-100">
          Platform Administration
        </h1>
        <p className="text-slate-400 mt-1 max-w-2xl">
          Manage system configurations, user role credentials, audit locks, and model updates.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* User Management List */}
        <div className="lg:col-span-2 glass-card p-6 rounded-2xl space-y-6">
          <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
            <UserCheck className="w-4 h-4 text-indigo-400" /> Active System Users
          </h2>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-[#1e293b] text-slate-500 font-bold uppercase">
                  <th className="py-2.5">User Identity</th>
                  <th className="py-2.5">Email Address</th>
                  <th className="py-2.5">Assigned Role</th>
                  <th className="py-2.5 text-right">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1e293b]/50 text-slate-300 font-medium">
                {users.map((u, i) => (
                  <tr key={i} className="hover:bg-slate-900/30 transition-colors">
                    <td className="py-3 font-semibold text-slate-200">{u.name}</td>
                    <td className="py-3 text-slate-400">{u.email}</td>
                    <td className="py-3">
                      <span className="text-[10px] font-bold text-indigo-400 bg-indigo-500/5 px-2 py-0.5 border border-indigo-500/10 rounded-full">
                        {u.role}
                      </span>
                    </td>
                    <td className="py-3 text-right text-emerald-400">{u.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Configurations Settings Stub */}
        <div className="glass-card p-6 rounded-2xl space-y-6 lg:col-span-1 h-fit">
          <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
            <Settings className="w-4 h-4 text-indigo-400" /> Platform Locks
          </h2>

          <div className="space-y-4">
            <div className="flex justify-between items-center text-xs">
              <span className="text-slate-400 font-medium flex items-center gap-1.5">
                <Key className="w-3.5 h-3.5 text-indigo-400" />
                API Audits Logs
              </span>
              <span className="text-emerald-400 font-bold">Enabled</span>
            </div>
            
            <div className="flex justify-between items-center text-xs">
              <span className="text-slate-400 font-medium flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-violet-400" />
                DB Read replica
              </span>
              <span className="text-slate-500 font-bold">Offline</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
