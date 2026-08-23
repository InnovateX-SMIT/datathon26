import axios from "axios";

/**
 * Central API Base URL Configuration.
 * Automatically resolves from process.env.NEXT_PUBLIC_API_URL set in .env.local or deployment env vars.
 */
export const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/backend";

/**
 * Helper to produce standard headers for HTTP requests.
 */
export function getAuthHeaders(isMultipart = false): HeadersInit {
  return isMultipart ? {} : { "Content-Type": "application/json" };
}

/**
 * Centralized Axios Client instance.
 */
export const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    "Content-Type": "application/json",
  },
});
