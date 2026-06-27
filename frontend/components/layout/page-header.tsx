"use client";

import React from "react";
import { LucideIcon } from "lucide-react";

interface PageHeaderProps {
  icon: LucideIcon;
  iconColor?: string;       // e.g. "text-indigo-400"
  iconBg?: string;          // e.g. "bg-indigo-500/10 border-indigo-500/20"
  badge?: string;           // small uppercase pill badge
  badgeColor?: string;      // e.g. "text-indigo-400 bg-indigo-500/10 border-indigo-500/20"
  title: string;
  subtitle?: string;
  description?: string;
  children?: React.ReactNode; // right-side actions/status
}

export default function PageHeader({
  icon: Icon,
  iconColor = "text-indigo-400",
  iconBg = "bg-indigo-500/10 border border-indigo-500/20",
  badge,
  badgeColor = "text-indigo-400 bg-indigo-500/10 border border-indigo-500/20",
  title,
  subtitle,
  description,
  children,
}: PageHeaderProps) {
  return (
    <div className="flex flex-col md:flex-row md:items-start justify-between gap-4 border-b border-slate-800/70 pb-6 animate-fade-in">
      <div className="flex items-start gap-3.5">
        <div className={`p-2.5 rounded-xl shrink-0 mt-0.5 ${iconBg}`}>
          <Icon className={`w-5 h-5 ${iconColor}`} />
        </div>
        <div>
          {badge && (
            <span className={`text-[10px] font-bold uppercase tracking-widest px-2.5 py-0.5 rounded-full border ${badgeColor} block w-fit mb-1.5`}>
              {badge}
            </span>
          )}
          <h1 className="text-2xl font-black text-slate-100 uppercase tracking-tight leading-tight">
            {title}
          </h1>
          {subtitle && (
            <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-widest mt-1">
              {subtitle}
            </p>
          )}
          {description && (
            <p className="text-sm text-slate-400 mt-2.5 max-w-2xl leading-relaxed">
              {description}
            </p>
          )}
        </div>
      </div>
      {children && (
        <div className="flex items-center gap-3 shrink-0 self-start md:self-auto">
          {children}
        </div>
      )}
    </div>
  );
}
