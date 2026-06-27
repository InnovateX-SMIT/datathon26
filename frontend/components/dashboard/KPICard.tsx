"use client";

import React, { useEffect, useState, useRef } from "react";
import { LucideIcon, AlertCircle } from "lucide-react";

interface KPICardProps {
  title: string;
  value: number;
  subtitle?: string;
  icon: LucideIcon;
  accentColor?: "indigo" | "red" | "green" | "amber";
  loading?: boolean;
  error?: string;
  onRetry?: () => void;
}

export default function KPICard({
  title,
  value,
  subtitle,
  icon: Icon,
  accentColor = "indigo",
  loading = false,
  error,
  onRetry,
}: KPICardProps) {
  const [displayValue, setDisplayValue] = useState(0);
  const rafRef = useRef<number | null>(null);
  const startValRef = useRef(0);
  const targetValRef = useRef(value);

  // Number counting animation
  useEffect(() => {
    if (loading || error) return;

    // Reset animation when target value changes
    startValRef.current = displayValue;
    targetValRef.current = value;
    const duration = 1200; // ms
    const startTime = performance.now();

    const animate = (currentTime: number) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // Ease-out quad formula
      const easeProgress = progress * (2 - progress);
      const currentVal = Math.round(
        startValRef.current + (targetValRef.current - startValRef.current) * easeProgress
      );

      setDisplayValue(currentVal);

      if (progress < 1) {
        rafRef.current = requestAnimationFrame(animate);
      }
    };

    rafRef.current = requestAnimationFrame(animate);

    return () => {
      if (rafRef.current) {
        cancelAnimationFrame(rafRef.current);
      }
    };
  }, [value, loading, error]);

  // Color mapping configurations
  const colorMap = {
    indigo: {
      text: "text-indigo-400",
      bg: "bg-indigo-500/10",
      border: "border-indigo-500/20",
      hover: "hover:border-indigo-500/40 hover:shadow-[0_0_15px_rgba(99,102,241,0.15)]",
    },
    red: {
      text: "text-red-400",
      bg: "bg-red-500/10",
      border: "border-red-500/20",
      hover: "hover:border-red-500/40 hover:shadow-[0_0_15px_rgba(239,68,68,0.15)]",
    },
    green: {
      text: "text-green-400",
      bg: "bg-green-500/10",
      border: "border-green-500/20",
      hover: "hover:border-green-500/40 hover:shadow-[0_0_15px_rgba(34,197,94,0.15)]",
    },
    amber: {
      text: "text-amber-400",
      bg: "bg-amber-500/10",
      border: "border-amber-500/20",
      hover: "hover:border-amber-500/40 hover:shadow-[0_0_15px_rgba(245,158,11,0.15)]",
    },
  };

  const colors = colorMap[accentColor];

  if (loading) {
    return (
      <div className="glass-card p-6 rounded-2xl border border-slate-800/60 flex flex-col justify-between min-h-[140px]">
        <div className="flex items-start justify-between">
          <div className="w-10 h-10 bg-slate-800/50 rounded-xl animate-pulse" />
        </div>
        <div>
          <div className="h-3 w-24 bg-slate-800/50 rounded animate-pulse mt-3" />
          <div className="h-8 w-20 bg-slate-800/50 rounded animate-pulse mt-2" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass-card p-5 rounded-2xl border-l-4 border-red-500 border border-slate-800/60 flex flex-col justify-between min-h-[140px]">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
          <div className="min-w-0">
            <h4 className="text-xs font-bold text-red-500 uppercase tracking-wider">Error</h4>
            <p className="text-[11px] text-slate-400 line-clamp-2 mt-0.5">{error}</p>
          </div>
        </div>
        {onRetry && (
          <button
            onClick={onRetry}
            className="text-[10px] uppercase font-bold text-indigo-400 hover:text-indigo-300 w-fit cursor-pointer self-end transition-colors"
          >
            Retry
          </button>
        )}
      </div>
    );
  }

  return (
    <div className={`glass-card p-6 rounded-2xl border border-slate-800/60 flex flex-col justify-between min-h-[140px] relative overflow-hidden transition-all duration-300 ${colors.hover}`}>
      <div className="flex items-start justify-between">
        <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
          {title}
        </span>
        <div className={`p-2.5 rounded-xl border ${colors.bg} ${colors.border}`}>
          <Icon className={`w-5 h-5 ${colors.text}`} />
        </div>
      </div>
      <div>
        <h2 className="text-3xl font-extrabold text-slate-50 tracking-tight leading-none mt-2">
          {displayValue.toLocaleString()}
        </h2>
        {subtitle && (
          <p className="text-[10px] text-slate-500 font-semibold tracking-wider mt-1 uppercase">
            {subtitle}
          </p>
        )}
      </div>
    </div>
  );
}
