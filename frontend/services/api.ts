import axios from "axios";

/**
 * AppSail production backend. Used when NEXT_PUBLIC_API_URL is unset at build time.
 * Local `next dev` should set NEXT_PUBLIC_API_URL (see .env.development).
 */
export const PRODUCTION_API_URL =
  "https://crimenexus-backend-50045204017.development.catalystappsail.in";

/**
 * Central API Base URL Configuration.
 * NEXT_PUBLIC_* is inlined at Next.js build time; Catalyst console env cannot
 * rewrite an already-built static client.
 */
export const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ||
  (process.env.NODE_ENV === "production" ? PRODUCTION_API_URL : "http://localhost:8000");

/**
 * JSON Content-Type for requests that actually send a JSON body.
 * Do not attach this to GET/HEAD — application/json is not CORS-safelisted
 * and forces a preflight that Catalyst's edge currently answers without CORS headers.
 */
export function getAuthHeaders(isMultipart = false): Record<string, string> {
  return isMultipart ? {} : { "Content-Type": "application/json" };
}

export const apiClient = axios.create({
  baseURL: API_BASE,
});

function stripContentTypeOnSafeMethods(headers: unknown) {
  if (!headers) return;
  const h = headers as {
    delete?: (name: string) => void;
    [key: string]: unknown;
  };
  if (typeof h.delete === "function") {
    h.delete("Content-Type");
    h.delete("content-type");
    return;
  }
  delete h["Content-Type"];
  delete h["content-type"];
}

axios.interceptors.request.use((config) => {
  const method = (config.method ?? "get").toLowerCase();
  if (method === "get" || method === "head") {
    stripContentTypeOnSafeMethods(config.headers);
  }
  return config;
});
