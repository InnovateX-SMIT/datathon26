"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { useRouter } from "next/navigation";

export interface User {
  id: number;
  name: string;
  email: string;
  role: "ADMIN" | "SUPERINTENDENT" | "OFFICER";
  status: string;
  created_at: string;
  updated_at: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  // Check for stored token and load user details on startup
  useEffect(() => {
    async function restoreSession() {
      const storedToken = localStorage.getItem("datathon_auth_token");
      if (storedToken) {
        try {
          const res = await fetch(`${API_URL}/api/v1/auth/me`, {
            headers: {
              Authorization: `Bearer ${storedToken}`,
            },
          });
          if (res.ok) {
            const userData = await res.json();
            setToken(storedToken);
            setUser(userData);
          } else {
            // Token is invalid/expired
            localStorage.removeItem("datathon_auth_token");
          }
        } catch (err) {
          console.error("Failed to restore session", err);
          // Network errors should not clear token instantly to prevent losing session on transient offline,
          // but we can choose to clear it if it's explicitly a 401/403.
        }
      }
      setLoading(false);
    }
    restoreSession();
  }, [API_URL]);

  const login = async (email: string, password: string) => {
    try {
      const res = await fetch(`${API_URL}/api/v1/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Incorrect email or password");
      }

      const data = await res.json();
      localStorage.setItem("datathon_auth_token", data.access_token);
      setToken(data.access_token);
      setUser(data.user);
      router.push("/dashboard");
    } catch (err) {
      throw err;
    }
  };

  const logout = () => {
    localStorage.removeItem("datathon_auth_token");
    setToken(null);
    setUser(null);
    router.push("/login");
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
