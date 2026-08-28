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
 * Retrieves or generates a unique session identifier stored in browser localStorage.
 * This guarantees complete multi-user data isolation per browser session.
 */
export function getOrCreateSessionId(): string {
  if (typeof window === "undefined") return "server-session";
  let sid = localStorage.getItem("crimenexus_session_id");
  if (!sid) {
    sid =
      typeof crypto !== "undefined" && crypto.randomUUID
        ? crypto.randomUUID()
        : "session_" + Date.now() + "_" + Math.random().toString(36).substring(2);
    localStorage.setItem("crimenexus_session_id", sid);
  }
  return sid;
}

/**
 * JSON Content-Type for requests that actually send a JSON body.
 * Automatically attaches X-Session-ID header.
 */
export function getAuthHeaders(isMultipart = false): Record<string, string> {
  const headers: Record<string, string> = {
    "X-Session-ID": getOrCreateSessionId(),
  };
  if (!isMultipart) {
    headers["Content-Type"] = "application/json";
  }
  return headers;
}

export const apiClient = axios.create({
  baseURL: API_BASE,
});

function stripContentTypeOnSafeMethods(headers: unknown) {
  if (!headers) return;
  const h = headers as {
    delete?: (name: string) => void;
    set?: (name: string, value: string) => void;
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

const attachSessionHeader = (config: any) => {
  const method = (config.method ?? "get").toLowerCase();
  if (method === "get" || method === "head") {
    stripContentTypeOnSafeMethods(config.headers);
  }
  if (config.headers) {
    const sid = getOrCreateSessionId();
    if (typeof config.headers.set === "function") {
      config.headers.set("X-Session-ID", sid);
    } else {
      config.headers["X-Session-ID"] = sid;
    }
  }
  return config;
};

axios.interceptors.request.use(attachSessionHeader);
apiClient.interceptors.request.use(attachSessionHeader);
