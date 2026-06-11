import React from "react";

interface InputFieldProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
}

export function InputField({ label, error, className = "", ...props }: InputFieldProps) {
  return (
    <div className={`flex flex-col gap-1.5 w-full ${className}`}>
      <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">{label}</label>
      <input
        className="w-full px-4 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl text-slate-200 text-sm font-medium focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/30 outline-none transition-all"
        {...props}
      />
      {error && <span className="text-[10px] font-bold text-red-500 tracking-wide">{error}</span>}
    </div>
  );
}

interface SelectFieldProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label: string;
  options: { value: string | number; label: string }[];
  error?: string;
}

export function SelectField({ label, options, error, className = "", ...props }: SelectFieldProps) {
  return (
    <div className={`flex flex-col gap-1.5 w-full ${className}`}>
      <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">{label}</label>
      <select
        className="w-full px-4 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl text-slate-200 text-sm font-medium focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/30 outline-none transition-all cursor-pointer appearance-none"
        {...props}
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value} className="bg-slate-950 text-slate-200">
            {opt.label}
          </option>
        ))}
      </select>
      {error && <span className="text-[10px] font-bold text-red-500 tracking-wide">{error}</span>}
    </div>
  );
}

interface CardContainerProps {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  className?: string;
}

export function CardContainer({ title, subtitle, children, className = "" }: CardContainerProps) {
  return (
    <div className={`glass-card p-6 rounded-3xl border border-slate-800/60 relative overflow-hidden transition-all duration-300 ${className}`}>
      <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-indigo-500/20 to-transparent" />
      <div className="mb-5">
        <h3 className="text-lg font-bold text-slate-100 uppercase tracking-tight">{title}</h3>
        {subtitle && <p className="text-xs text-slate-400 font-medium mt-0.5">{subtitle}</p>}
      </div>
      {children}
    </div>
  );
}
