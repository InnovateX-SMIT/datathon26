"use client";

import React, { useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { ShieldAlert, Mail, Lock, Loader2, ArrowRight, KeyRound } from "lucide-react";

export default function LoginPage() {
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [formLoading, setFormLoading] = useState(false);

  // Client validation states
  const [emailError, setEmailError] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);

  const validateEmail = (val: string) => {
    if (!val) {
      return "Email is required";
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(val)) {
      return "Please enter a valid email address";
    }
    return null;
  };

  const validatePassword = (val: string) => {
    if (!val) {
      return "Password is required";
    }
    if (val.length < 5) {
      return "Password must be at least 5 characters";
    }
    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setEmailError(null);
    setPasswordError(null);

    const eErr = validateEmail(email);
    const pErr = validatePassword(password);

    if (eErr || pErr) {
      setEmailError(eErr);
      setPasswordError(pErr);
      return;
    }

    setFormLoading(true);
    try {
      await login(email, password);
    } catch (err: any) {
      setError(err.message || "Failed to establish secure session. Please check credentials.");
      setFormLoading(false);
    }
  };

  // Quick seed logins for user convenience
  const handleQuickLogin = (seedEmail: string, seedPass: string) => {
    setEmail(seedEmail);
    setPassword(seedPass);
    setError(null);
    setEmailError(null);
    setPasswordError(null);
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-[#070b13] relative overflow-hidden px-4">
      {/* Background ambient lighting effects */}
      <div className="absolute top-[-20%] left-[-20%] w-[60%] h-[60%] rounded-full bg-indigo-500/10 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-20%] right-[-20%] w-[60%] h-[60%] rounded-full bg-violet-500/10 blur-[120px] pointer-events-none" />
      <div className="absolute inset-0 opacity-[0.03] bg-[radial-gradient(#6366f1_1px,transparent_1px)] [background-size:24px_24px] pointer-events-none" />

      <div className="w-full max-w-lg z-10 space-y-6">
        {/* Logo and branding */}
        <div className="text-center space-y-2">
          <div className="inline-flex bg-indigo-600/10 border border-indigo-500/20 p-4 rounded-2xl shadow-[0_0_20px_rgba(99,102,241,0.15)] animate-pulse">
            <ShieldAlert className="w-10 h-10 text-indigo-400" />
          </div>
          <div>
            <h1 className="text-2xl font-black tracking-widest text-slate-100 uppercase">PREDICTIVE GUARDIANS</h1>
            <p className="text-xs text-indigo-400 font-bold uppercase tracking-widest mt-1">Crime Intelligence & Decision Support Platform</p>
          </div>
        </div>

        {/* Main login card */}
        <div className="glass-card p-8 rounded-3xl border border-[#1e293b]/60 shadow-[0_20px_50px_rgba(0,0,0,0.5)] space-y-6 relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-transparent via-indigo-500/50 to-transparent" />
          
          <div className="text-center">
            <h2 className="text-lg font-extrabold text-slate-200">Terminal Authentication</h2>
            <p className="text-xs text-slate-500 mt-1">Enter credentials to establish encrypted pipeline</p>
          </div>

          {error && (
            <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-xs text-red-400 font-medium leading-relaxed flex items-start gap-3 animate-shake">
              <ShieldAlert className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Email Input */}
            <div className="space-y-1.5">
              <label className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">Authorized Email</label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-500 pointer-events-none">
                  <Mail className="w-4 h-4" />
                </span>
                <input
                  type="email"
                  value={email}
                  disabled={formLoading}
                  onChange={(e) => {
                    setEmail(e.target.value);
                    if (emailError) setEmailError(null);
                  }}
                  placeholder="officer@police.gov.in"
                  className={`w-full bg-[#090e1a]/80 border ${
                    emailError ? "border-red-500/40 focus:border-red-500" : "border-[#1e293b] focus:border-indigo-500"
                  } text-sm rounded-xl pl-10 pr-4 py-3 text-slate-100 placeholder-slate-600 focus:outline-none transition-all duration-200 bg-clip-padding`}
                />
              </div>
              {emailError && <p className="text-[10px] text-red-400 font-bold">{emailError}</p>}
            </div>

            {/* Password Input */}
            <div className="space-y-1.5">
              <label className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">Security Password</label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-500 pointer-events-none">
                  <Lock className="w-4 h-4" />
                </span>
                <input
                  type="password"
                  value={password}
                  disabled={formLoading}
                  onChange={(e) => {
                    setPassword(e.target.value);
                    if (passwordError) setPasswordError(null);
                  }}
                  placeholder="••••••••"
                  className={`w-full bg-[#090e1a]/80 border ${
                    passwordError ? "border-red-500/40 focus:border-red-500" : "border-[#1e293b] focus:border-indigo-500"
                  } text-sm rounded-xl pl-10 pr-4 py-3 text-slate-100 placeholder-slate-600 focus:outline-none transition-all duration-200 bg-clip-padding`}
                />
              </div>
              {passwordError && <p className="text-[10px] text-red-400 font-bold">{passwordError}</p>}
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={formLoading}
              className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-800 text-slate-100 font-bold py-3 px-4 rounded-xl text-sm transition-all flex items-center justify-center gap-2 cursor-pointer shadow-lg shadow-indigo-600/10 hover:shadow-indigo-600/20 active:scale-[0.98] mt-6"
            >
              {formLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Connecting to Guard Grid...</span>
                </>
              ) : (
                <>
                  <span>Sign In to System</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>
        </div>

        {/* Quick Credentials Panel for datathon evaluators */}
        <div className="glass-card p-6 rounded-2xl border border-[#1e293b]/40 shadow-xl space-y-4">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-300">
            <KeyRound className="w-4 h-4 text-indigo-400" />
            <span className="uppercase tracking-wider">Sandbox Credentials</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <button
              onClick={() => handleQuickLogin("admin@police.gov.in", "admin123")}
              disabled={formLoading}
              className="p-3 bg-slate-900/60 hover:bg-slate-900 border border-slate-800/80 hover:border-indigo-500/30 rounded-xl text-left transition-all group cursor-pointer"
            >
              <div className="text-[10px] font-bold text-indigo-400 uppercase">Admin</div>
              <div className="text-[11px] font-semibold text-slate-300 truncate mt-1">admin@police.gov.in</div>
              <div className="text-[9px] text-slate-600 font-mono mt-0.5">pass: admin123</div>
            </button>
            <button
              onClick={() => handleQuickLogin("sp@police.gov.in", "sp123")}
              disabled={formLoading}
              className="p-3 bg-slate-900/60 hover:bg-slate-900 border border-slate-800/80 hover:border-violet-500/30 rounded-xl text-left transition-all group cursor-pointer"
            >
              <div className="text-[10px] font-bold text-violet-400 uppercase">Superintendent</div>
              <div className="text-[11px] font-semibold text-slate-300 truncate mt-1">sp@police.gov.in</div>
              <div className="text-[9px] text-slate-600 font-mono mt-0.5">pass: sp123</div>
            </button>
            <button
              onClick={() => handleQuickLogin("officer@police.gov.in", "officer123")}
              disabled={formLoading}
              className="p-3 bg-slate-900/60 hover:bg-slate-900 border border-slate-800/80 hover:border-emerald-500/30 rounded-xl text-left transition-all group cursor-pointer"
            >
              <div className="text-[10px] font-bold text-emerald-400 uppercase">Officer</div>
              <div className="text-[11px] font-semibold text-slate-300 truncate mt-1">officer@police.gov.in</div>
              <div className="text-[9px] text-slate-600 font-mono mt-0.5">pass: officer123</div>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
