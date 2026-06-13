import { useState, useEffect, useCallback } from "react";
import type {
  AdminUser,
  CreateUserPayload,
  UpdateUserPayload,
  AuditLogListResponse,
  SystemHealth,
  ModelStatusResponse,
  DatasetStatusResponse,
} from "@/features/admin/types/admin";
import {
  fetchAdminUsers,
  createAdminUser,
  updateAdminUser,
  deactivateAdminUser,
  activateAdminUser,
  fetchSystemHealth,
  fetchModelStatus,
  fetchAuditLogs,
  fetchDatasetStatus,
} from "@/features/admin/services/admin-service";

export function useAdmin() {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [modelStatus, setModelStatus] = useState<ModelStatusResponse | null>(null);
  const [auditLogs, setAuditLogs] = useState<AuditLogListResponse | null>(null);
  const [datasetStatus, setDatasetStatus] = useState<DatasetStatusResponse | null>(null);

  const [usersLoading, setUsersLoading] = useState(false);
  const [healthLoading, setHealthLoading] = useState(false);
  const [modelsLoading, setModelsLoading] = useState(false);
  const [auditLoading, setAuditLoading] = useState(false);
  const [datasetLoading, setDatasetLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  const [error, setError] = useState<string | null>(null);
  const [auditPage, setAuditPage] = useState(1);
  const [auditPageSize] = useState(50);
  const [auditActionFilter, setAuditActionFilter] = useState("ALL");

  // ── User Management ─────────────────────────────────────────────────────

  const loadUsers = useCallback(async () => {
    setUsersLoading(true);
    setError(null);
    try {
      const data = await fetchAdminUsers();
      setUsers(data);
    } catch (err: unknown) {
      console.error("Error loading users:", err);
      setError("Failed to load users.");
    } finally {
      setUsersLoading(false);
    }
  }, []);

  const createUser = useCallback(async (payload: CreateUserPayload) => {
    setActionLoading(true);
    setError(null);
    try {
      const newUser = await createAdminUser(payload);
      setUsers((prev) => [newUser, ...prev]);
    } catch (err: unknown) {
      console.error("Error creating user:", err);
      setError("Failed to create user.");
      throw err;
    } finally {
      setActionLoading(false);
    }
  }, []);

  const updateUser = useCallback(
    async (id: number, payload: UpdateUserPayload) => {
      setActionLoading(true);
      setError(null);
      try {
        const updated = await updateAdminUser(id, payload);
        setUsers((prev) => prev.map((u) => (u.id === id ? updated : u)));
      } catch (err: unknown) {
        console.error("Error updating user:", err);
        setError("Failed to update user.");
        throw err;
      } finally {
        setActionLoading(false);
      }
    },
    []
  );

  const deactivateUser = useCallback(async (id: number) => {
    setActionLoading(true);
    setError(null);
    try {
      const updated = await deactivateAdminUser(id);
      setUsers((prev) => prev.map((u) => (u.id === id ? updated : u)));
    } catch (err: unknown) {
      console.error("Error deactivating user:", err);
      setError("Failed to deactivate user.");
      throw err;
    } finally {
      setActionLoading(false);
    }
  }, []);

  const activateUser = useCallback(async (id: number) => {
    setActionLoading(true);
    setError(null);
    try {
      const updated = await activateAdminUser(id);
      setUsers((prev) => prev.map((u) => (u.id === id ? updated : u)));
    } catch (err: unknown) {
      console.error("Error activating user:", err);
      setError("Failed to activate user.");
      throw err;
    } finally {
      setActionLoading(false);
    }
  }, []);

  // ── System Monitoring ────────────────────────────────────────────────────

  const loadSystemHealth = useCallback(async () => {
    setHealthLoading(true);
    setError(null);
    try {
      const data = await fetchSystemHealth();
      setSystemHealth(data);
    } catch (err: unknown) {
      console.error("Error loading system health:", err);
      setError("Failed to load system health.");
    } finally {
      setHealthLoading(false);
    }
  }, []);

  const loadModelStatus = useCallback(async () => {
    setModelsLoading(true);
    setError(null);
    try {
      const data = await fetchModelStatus();
      setModelStatus(data);
    } catch (err: unknown) {
      console.error("Error loading model status:", err);
      setError("Failed to load model status.");
    } finally {
      setModelsLoading(false);
    }
  }, []);

  // ── Audit Logs ───────────────────────────────────────────────────────────

  const loadAuditLogs = useCallback(async () => {
    setAuditLoading(true);
    setError(null);
    try {
      const data = await fetchAuditLogs(
        auditPage,
        auditPageSize,
        auditActionFilter !== "ALL" ? auditActionFilter : undefined
      );
      setAuditLogs(data);
    } catch (err: unknown) {
      console.error("Error loading audit logs:", err);
      setError("Failed to load audit logs.");
    } finally {
      setAuditLoading(false);
    }
  }, [auditPage, auditPageSize, auditActionFilter]);

  // ── Dataset Status ───────────────────────────────────────────────────────

  const loadDatasetStatus = useCallback(async () => {
    setDatasetLoading(true);
    setError(null);
    try {
      const data = await fetchDatasetStatus();
      setDatasetStatus(data);
    } catch (err: unknown) {
      console.error("Error loading dataset status:", err);
      setError("Failed to load dataset status.");
    } finally {
      setDatasetLoading(false);
    }
  }, []);

  // ── Effects ──────────────────────────────────────────────────────────────

  // Load users on mount
  useEffect(() => {
    loadUsers();
  }, [loadUsers]);

  // Reload audit logs when pagination or filter changes
  useEffect(() => {
    if (auditLogs !== null) {
      loadAuditLogs();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [auditPage, auditActionFilter]);

  return {
    // State
    users,
    systemHealth,
    modelStatus,
    auditLogs,
    datasetStatus,

    // Loading flags
    usersLoading,
    healthLoading,
    modelsLoading,
    auditLoading,
    datasetLoading,
    actionLoading,

    error,

    // Audit pagination/filter
    auditPage,
    auditPageSize,
    auditActionFilter,
    setAuditPage,
    setAuditActionFilter,

    // Methods
    loadUsers,
    createUser,
    updateUser,
    deactivateUser,
    activateUser,
    loadSystemHealth,
    loadModelStatus,
    loadAuditLogs,
    loadDatasetStatus,
  };
}
