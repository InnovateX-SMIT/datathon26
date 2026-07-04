import axios from "axios";
import type { Report, ReportSummary, ReportType } from "../types/report";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function getAuthHeaders() {
  const token = typeof window !== "undefined" ? localStorage.getItem("datathon_auth_token") : null;
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

export async function fetchReports(): Promise<ReportSummary[]> {
  const res = await axios.get<ReportSummary[]>(`${API_BASE}/api/v1/reports/`, {
    headers: getAuthHeaders(),
    timeout: 30000,
  });
  return res.data;
}

export async function fetchReportTypes(): Promise<ReportType[]> {
  const res = await axios.get<{ types: ReportType[] }>(`${API_BASE}/api/v1/reports/types`, {
    headers: getAuthHeaders(),
    timeout: 30000,
  });
  return res.data.types;
}

export async function fetchReportById(id: number): Promise<Report> {
  const res = await axios.get<Report>(`${API_BASE}/api/v1/reports/${id}`, {
    headers: getAuthHeaders(),
    timeout: 45000,
  });
  return res.data;
}

export async function generateReport(title: string, reportType: string): Promise<Report> {
  const res = await axios.post<Report>(
    `${API_BASE}/api/v1/reports/generate`,
    {
      title,
      report_type: reportType,
    },
    {
      headers: getAuthHeaders(),
      timeout: 60000,
    }
  );
  return res.data;
}

export async function downloadReportCSV(id: number, filename: string): Promise<void> {
  const res = await axios.get(`${API_BASE}/api/v1/reports/${id}/download`, {
    headers: getAuthHeaders(),
    responseType: "blob",
    timeout: 30000,
  });
  const url = window.URL.createObjectURL(new Blob([res.data], { type: "text/csv" }));
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}
