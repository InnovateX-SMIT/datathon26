import React from "react";

interface SectionHeaderProps {
  title: string;
  accentColor?: string; // Tailwind bg color e.g. "bg-indigo-500"
  className?: string;
}

export default function SectionHeader({
  title,
  accentColor = "bg-indigo-500",
  className = "",
}: SectionHeaderProps) {
  return (
    <div className={`flex items-center gap-2.5 mb-5 ${className}`}>
      <div className={`w-1 h-[18px] ${accentColor} rounded-sm shrink-0`} />
      <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider leading-none">
        {title}
      </h3>
    </div>
  );
}
