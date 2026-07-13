"use client";

import React, { useCallback, useState, useEffect } from "react";
import axios from "axios";
import Sidebar from "./sidebar";
import Navbar from "./navbar";

// 1. Setup Axios interceptor to unwrap standardized success envelope globally
axios.interceptors.response.use(
  (response) => {
    if (
      response.data &&
      typeof response.data === "object" &&
      response.data.success === true &&
      "data" in response.data
    ) {
      return {
        ...response,
        data: response.data.data,
      };
    }
    return response;
  },
  (error) => {
    if (error.response && error.response.data && typeof error.response.data === "object") {
      const errData = error.response.data;
      if (errData.success === false && errData.message) {
        error.message = errData.message;
      }
    }
    return Promise.reject(error);
  }
);

// 2. Setup window.fetch override to unwrap standardized success envelope globally
if (typeof window !== "undefined") {
  const originalFetch = window.fetch;
  window.fetch = async function (...args) {
    const response = await originalFetch(...args);
    const contentType = response.headers.get("content-type");
    if (response.ok && contentType && contentType.includes("application/json")) {
      const cloned = response.clone();
      try {
        const json = await cloned.json();
        if (
          json &&
          typeof json === "object" &&
          json.success === true &&
          "data" in json
        ) {
          return new Response(JSON.stringify(json.data), {
            status: response.status,
            statusText: response.statusText,
            headers: response.headers,
          });
        }
      } catch (e) {
        // Decodes failed or non-enveloped json response, return original response
      }
    }
    return response;
  };
}

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
        <main className="flex-1 overflow-y-auto px-4 py-6 sm:px-6 sm:py-7 md:px-8 md:py-8 relative bg-radial from-[#0d1527] to-[#070b13] animate-fade-in">
          {children}
        </main>
      </div>
    </div>
  );
}

