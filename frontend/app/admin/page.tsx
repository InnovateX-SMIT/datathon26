"use client";

import React, { useState } from "react";
import { ShieldCheck, ShieldAlert } from "lucide-react";
import { useAdmin } from "@/hooks/useAdmin";
import UserManagementPanel from "@/features/admin/components/user-management-panel";
import SystemHealthPanel from "@/features/admin/components/system-health-panel";
import AuditLogsPanel from "@/features/admin/components/audit-logs-panel";
import DatasetManagementPanel from "@/features/admin/components/dataset-management-panel";

type TabId = "users" | "system" | "audit" | "dataset";

const TABS: { id: TabId; label: string }[] = [
  { id: "users", label: "User Management" },
  { id: "system", label: "System Monitoring" },
  { id: "audit", label: "Audit Logs" },
  { id: "dataset", label: "Dataset Status" },
];

export default function AdminPage() {
  const {
    users,
    systemHealth,
    modelStatus,
    auditLogs,
    datasetStatus,

    usersLoading,
    healthLoading,
    modelsLoading,
    auditLoading,
    datasetLoading,
    actionLoading,

    error,

    auditPage,
    auditPageSize,
    auditActionFilter,
    setAuditPage,
    setAuditActionFilter,

    loadUsers,
    createUser,
    updateUser,
    deactivateUser,
    activateUser,
    loadSystemHealth,
    loadModelStatus,
    loadAuditLogs,
    loadDatasetStatus,
  } = useAdmin();

  const [activeTab, setActiveTab] = useState<TabId>("users");

  const handleTabChange = (tab: TabId) => {
    setActiveTab(tab);
    // Auto-load tab data on first visit
    if (tab === "system" && systemHealth === null) {
      loadSystemHealth();
      loadModelStatus();
    }
    if (tab === "audit" && auditLogs === null) {
      loadAuditLogs();
    }
    if (tab === "dataset" && datasetStatus === null) {
      loadDatasetStatus();
    }
  };

  return (
    <div className="min-h-screen py-8 px-4 sm:px-6 lg:px-8 space-y-8 animate-fade-in relative">
      {/* Background ambient glows */}
      <div className="absolute top-[10%] right-[5%] w-[500px] h-[500px] rounded-full bg-violet-500/5 blur-[130px] pointer-events-none" />
      <div className="absolute bottom-[10%] left-[8%] w-[400px] h-[400px] rounded-full bg-indigo-500/5 blur-[110px] pointer-events-none" />

      {/* ── Header ──────────────────────────────────────────────────────────── */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-900/80 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-violet-500/10 border border-violet-500/20 rounded-2xl">
              <ShieldCheck className="w-6 h-6 text-violet-400" />
            </div>
            <div>
              <h1 className="text-3xl font-black text-slate-100 uppercase tracking-tight">
                Admin Portal
              </h1>
              <p className="text-slate-400 text-xs font-semibold uppercase tracking-widest mt-1">
                Platform Administration & Operational Control
              </p>
            </div>
          </div>
          <p className="text-slate-400 text-sm mt-3 max-w-2xl leading-relaxed">
            Centralized control layer for managing platform users, monitoring
            system health, inspecting ML model availability, and reviewing the
            full operational audit trail.
          </p>
        </div>

        {/* Live Status Badge */}
        <div className="flex items-center gap-2 px-4 py-2.5 bg-violet-500/10 border border-violet-500/20 rounded-2xl self-start">
          <span className="w-2 h-2 rounded-full bg-violet-400 animate-pulse" />
          <span className="text-violet-400 text-xs font-black uppercase tracking-wider">
            Admin Active
          </span>
        </div>
      </div>

      {/* ── Global Error ─────────────────────────────────────────────────────── */}
      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-3xl text-red-400 text-xs flex gap-2.5 items-center max-w-4xl">
          <ShieldAlert className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* ── Tabs ─────────────────────────────────────────────────────────────── */}
      <div className="flex border-b border-slate-900" role="tablist" aria-label="Admin sections">
        <div className="flex gap-2">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              role="tab"
              aria-selected={activeTab === tab.id}
              onClick={() => handleTabChange(tab.id)}
              className={`pb-4 px-4 text-xs uppercase tracking-widest font-black transition-all relative cursor-pointer ${
                activeTab === tab.id
                  ? "text-violet-400 border-b-2 border-violet-500 bg-violet-500/5"
                  : "text-slate-500 hover:text-slate-350"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* ── Tab Panels ───────────────────────────────────────────────────────── */}
      <div className="min-h-[400px]">
        {activeTab === "users" && (
          <UserManagementPanel
            users={users}
            loading={usersLoading}
            actionLoading={actionLoading}
            onCreateUser={createUser}
            onUpdateUser={updateUser}
            onDeactivate={deactivateUser}
            onActivate={activateUser}
          />
        )}

        {activeTab === "system" && (
          <SystemHealthPanel
            health={systemHealth}
            modelStatus={modelStatus}
            healthLoading={healthLoading}
            modelsLoading={modelsLoading}
            onRefreshHealth={loadSystemHealth}
            onRefreshModels={loadModelStatus}
          />
        )}

        {activeTab === "audit" && (
          <AuditLogsPanel
            auditLogs={auditLogs}
            loading={auditLoading}
            auditPage={auditPage}
            auditPageSize={auditPageSize}
            auditActionFilter={auditActionFilter}
            onPageChange={setAuditPage}
            onActionFilterChange={setAuditActionFilter}
            onLoad={loadAuditLogs}
          />
        )}

        {activeTab === "dataset" && (
          <DatasetManagementPanel
            datasetStatus={datasetStatus}
            loading={datasetLoading}
            onRefresh={loadDatasetStatus}
          />
        )}
      </div>

      {/* ── Footer ───────────────────────────────────────────────────────────── */}
      <div className="pt-6 mt-4 border-t border-slate-900/60 flex justify-between items-center text-[9px] font-mono text-slate-700/60 tracking-widest select-none">
        <span>ADMIN CONTROL INFRASTRUCTURE</span>
        <span>PHASE 10 ENGINE ACTIVE</span>
      </div>
    </div>
  );
}
