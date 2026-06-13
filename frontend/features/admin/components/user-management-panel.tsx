"use client";

import React, { useState } from "react";
import { Users, Plus, X, Check, Edit2, UserCheck, UserX } from "lucide-react";
import type {
  AdminUser,
  CreateUserPayload,
  UpdateUserPayload,
  UserRole,
} from "@/features/admin/types/admin";

interface UserManagementPanelProps {
  users: AdminUser[];
  loading: boolean;
  actionLoading: boolean;
  onCreateUser: (payload: CreateUserPayload) => Promise<void>;
  onUpdateUser: (id: number, payload: UpdateUserPayload) => Promise<void>;
  onDeactivate: (id: number) => Promise<void>;
  onActivate: (id: number) => Promise<void>;
}

const ROLE_COLORS: Record<string, string> = {
  ADMIN: "text-violet-400 bg-violet-500/10 border-violet-500/20",
  SUPERINTENDENT: "text-amber-400 bg-amber-500/10 border-amber-500/20",
  OFFICER: "text-blue-400 bg-blue-500/10 border-blue-500/20",
  ANALYST: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
  SUPERVISOR: "text-cyan-400 bg-cyan-500/10 border-cyan-500/20",
};

const ROLES: UserRole[] = ["OFFICER", "SUPERINTENDENT", "ADMIN", "ANALYST", "SUPERVISOR"];

function SkeletonRow() {
  return (
    <tr>
      {[...Array(6)].map((_, i) => (
        <td key={i} className="px-4 py-3">
          <div className="h-4 bg-slate-800 rounded animate-pulse w-24" />
        </td>
      ))}
    </tr>
  );
}

export default function UserManagementPanel({
  users,
  loading,
  actionLoading,
  onCreateUser,
  onUpdateUser,
  onDeactivate,
  onActivate,
}: UserManagementPanelProps) {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editRole, setEditRole] = useState<UserRole>("OFFICER");

  // Create form state
  const [formName, setFormName] = useState("");
  const [formEmail, setFormEmail] = useState("");
  const [formPassword, setFormPassword] = useState("");
  const [formRole, setFormRole] = useState<UserRole>("OFFICER");
  const [formError, setFormError] = useState<string | null>(null);

  const handleCreate = async () => {
    if (!formName.trim() || !formEmail.trim() || !formPassword.trim()) {
      setFormError("All fields are required.");
      return;
    }
    setFormError(null);
    try {
      await onCreateUser({
        name: formName.trim(),
        email: formEmail.trim(),
        password: formPassword,
        role: formRole,
      });
      setShowCreateForm(false);
      setFormName("");
      setFormEmail("");
      setFormPassword("");
      setFormRole("OFFICER");
    } catch {
      setFormError("Failed to create user. Email may already be registered.");
    }
  };

  const handleStartEdit = (user: AdminUser) => {
    setEditingId(user.id);
    setEditRole(user.role);
  };

  const handleSaveEdit = async (id: number) => {
    await onUpdateUser(id, { role: editRole });
    setEditingId(null);
  };

  const formatDate = (iso: string) =>
    new Date(iso).toLocaleDateString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-violet-500/10 border border-violet-500/20 rounded-xl">
            <Users className="w-5 h-5 text-violet-400" />
          </div>
          <div>
            <h2 className="text-lg font-black text-slate-100 uppercase tracking-tight">
              User Management
            </h2>
            <p className="text-xs text-slate-500">
              {users.length} platform{" "}
              {users.length === 1 ? "user" : "users"} registered
            </p>
          </div>
        </div>
        <button
          onClick={() => setShowCreateForm((v) => !v)}
          className="flex items-center gap-2 px-4 py-2 bg-violet-500/10 hover:bg-violet-500/15 border border-violet-500/20 hover:border-violet-500/40 text-violet-400 font-bold text-xs uppercase tracking-wider rounded-xl transition-all cursor-pointer"
        >
          {showCreateForm ? <X className="w-4 h-4" /> : <Plus className="w-4 h-4" />}
          {showCreateForm ? "Cancel" : "Add User"}
        </button>
      </div>

      {/* Create User Form */}
      {showCreateForm && (
        <div className="bg-slate-950/60 border border-violet-500/20 rounded-2xl p-5 space-y-4 backdrop-blur-md">
          <h3 className="text-sm font-black text-violet-300 uppercase tracking-widest">
            New User
          </h3>
          {formError && (
            <p className="text-xs text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2">
              {formError}
            </p>
          )}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">
                Full Name
              </label>
              <input
                type="text"
                value={formName}
                onChange={(e) => setFormName(e.target.value)}
                placeholder="Officer Name"
                className="w-full bg-slate-900 border border-slate-800 text-slate-200 text-sm rounded-xl px-3 py-2 focus:outline-none focus:border-violet-500/50 placeholder-slate-600"
              />
            </div>
            <div className="space-y-1">
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">
                Email
              </label>
              <input
                type="email"
                value={formEmail}
                onChange={(e) => setFormEmail(e.target.value)}
                placeholder="officer@police.gov.in"
                className="w-full bg-slate-900 border border-slate-800 text-slate-200 text-sm rounded-xl px-3 py-2 focus:outline-none focus:border-violet-500/50 placeholder-slate-600"
              />
            </div>
            <div className="space-y-1">
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">
                Password
              </label>
              <input
                type="password"
                value={formPassword}
                onChange={(e) => setFormPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-slate-900 border border-slate-800 text-slate-200 text-sm rounded-xl px-3 py-2 focus:outline-none focus:border-violet-500/50 placeholder-slate-600"
              />
            </div>
            <div className="space-y-1">
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">
                Role
              </label>
              <select
                value={formRole}
                onChange={(e) => setFormRole(e.target.value as UserRole)}
                className="w-full bg-slate-900 border border-slate-800 text-slate-200 text-sm rounded-xl px-3 py-2 focus:outline-none focus:border-violet-500/50 cursor-pointer"
              >
                {ROLES.map((r) => (
                  <option key={r} value={r}>
                    {r}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <div className="flex gap-3 pt-1">
            <button
              onClick={handleCreate}
              disabled={actionLoading}
              className="px-5 py-2 bg-violet-500 hover:bg-violet-600 text-white font-bold text-xs uppercase tracking-wider rounded-xl transition-all cursor-pointer disabled:opacity-50"
            >
              {actionLoading ? "Creating..." : "Create User"}
            </button>
            <button
              onClick={() => {
                setShowCreateForm(false);
                setFormError(null);
              }}
              className="px-5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold text-xs uppercase tracking-wider rounded-xl transition-all cursor-pointer"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Users Table */}
      <div className="bg-slate-950/40 border border-slate-900/80 rounded-2xl overflow-hidden backdrop-blur-md">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-900">
                {["Name", "Email", "Role", "Status", "Created", "Actions"].map(
                  (h) => (
                    <th
                      key={h}
                      className="px-4 py-3 text-left text-[9px] font-bold text-slate-500 uppercase tracking-wider"
                    >
                      {h}
                    </th>
                  )
                )}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-900/60">
              {loading ? (
                [...Array(4)].map((_, i) => <SkeletonRow key={i} />)
              ) : users.length === 0 ? (
                <tr>
                  <td
                    colSpan={6}
                    className="text-center py-12 text-slate-600 text-xs uppercase tracking-widest"
                  >
                    No users found
                  </td>
                </tr>
              ) : (
                users.map((user) => (
                  <tr
                    key={user.id}
                    className="hover:bg-slate-900/30 transition-colors"
                  >
                    {/* Name */}
                    <td className="px-4 py-3 font-semibold text-slate-200">
                      {user.name}
                    </td>

                    {/* Email */}
                    <td className="px-4 py-3 text-slate-400 text-xs font-mono">
                      {user.email}
                    </td>

                    {/* Role */}
                    <td className="px-4 py-3">
                      {editingId === user.id ? (
                        <div className="flex items-center gap-2">
                          <select
                            value={editRole}
                            onChange={(e) =>
                              setEditRole(e.target.value as UserRole)
                            }
                            className="bg-slate-900 border border-slate-700 text-slate-200 text-xs rounded-lg px-2 py-1 focus:outline-none focus:border-violet-500/50 cursor-pointer"
                          >
                            {ROLES.map((r) => (
                              <option key={r} value={r}>
                                {r}
                              </option>
                            ))}
                          </select>
                          <button
                            onClick={() => handleSaveEdit(user.id)}
                            disabled={actionLoading}
                            className="p-1 text-green-400 hover:text-green-300 cursor-pointer disabled:opacity-50"
                            title="Save"
                          >
                            <Check className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => setEditingId(null)}
                            className="p-1 text-red-400 hover:text-red-300 cursor-pointer"
                            title="Cancel"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        </div>
                      ) : (
                        <span
                          className={`inline-flex items-center px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider border rounded-lg ${ROLE_COLORS[user.role] ?? ROLE_COLORS.OFFICER}`}
                        >
                          {user.role}
                        </span>
                      )}
                    </td>

                    {/* Status */}
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-1.5">
                        <span
                          className={`w-2 h-2 rounded-full ${user.status === "active" ? "bg-green-400" : "bg-red-400"}`}
                        />
                        <span
                          className={`text-xs font-semibold ${user.status === "active" ? "text-green-400" : "text-red-400"}`}
                        >
                          {user.status}
                        </span>
                      </div>
                    </td>

                    {/* Created */}
                    <td className="px-4 py-3 text-xs text-slate-500">
                      {formatDate(user.created_at)}
                    </td>

                    {/* Actions */}
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        {editingId !== user.id && (
                          <button
                            onClick={() => handleStartEdit(user)}
                            className="flex items-center gap-1 px-2 py-1 text-xs font-semibold text-slate-400 hover:text-slate-200 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg transition-all cursor-pointer"
                          >
                            <Edit2 className="w-3 h-3" />
                            Edit Role
                          </button>
                        )}
                        {user.status === "active" ? (
                          <button
                            onClick={() => onDeactivate(user.id)}
                            disabled={actionLoading}
                            className="flex items-center gap-1 px-2 py-1 text-xs font-semibold text-red-400 hover:text-red-300 bg-red-500/10 hover:bg-red-500/15 border border-red-500/20 rounded-lg transition-all cursor-pointer disabled:opacity-50"
                          >
                            <UserX className="w-3 h-3" />
                            Deactivate
                          </button>
                        ) : (
                          <button
                            onClick={() => onActivate(user.id)}
                            disabled={actionLoading}
                            className="flex items-center gap-1 px-2 py-1 text-xs font-semibold text-green-400 hover:text-green-300 bg-green-500/10 hover:bg-green-500/15 border border-green-500/20 rounded-lg transition-all cursor-pointer disabled:opacity-50"
                          >
                            <UserCheck className="w-3 h-3" />
                            Activate
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
