"use client";

import React, { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { Maximize2, Minimize2, X } from "lucide-react";
import { useMap } from "react-leaflet";

interface MapFullscreenPanelProps {
  title: string;
  children: (fullscreen: boolean) => React.ReactNode;
  loading?: boolean;
  className?: string;
}

export function LeafletMapResizer({ resizeKey }: { resizeKey: string | number | boolean }) {
  const map = useMap();

  useEffect(() => {
    const timers = [80, 240, 480].map((delay) =>
      window.setTimeout(() => map.invalidateSize({ animate: false }), delay)
    );
    return () => timers.forEach(window.clearTimeout);
  }, [map, resizeKey]);

  return null;
}

export default function MapFullscreenPanel({ title, children, loading, className = "" }: MapFullscreenPanelProps) {
  const [open, setOpen] = useState(false);
  const [browserFullscreen, setBrowserFullscreen] = useState(false);
  const overlayRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
    };

    const handleFullscreenChange = () => {
      const isActive = document.fullscreenElement === overlayRef.current;
      setBrowserFullscreen(isActive);
      if (!document.fullscreenElement) setOpen(false);
    };

    if (open) {
      document.addEventListener("keydown", handleKeyDown);
      document.addEventListener("fullscreenchange", handleFullscreenChange);
      document.body.style.overflow = "hidden";
    }

    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.removeEventListener("fullscreenchange", handleFullscreenChange);
      document.body.style.overflow = "";
    };
  }, [open]);

  useEffect(() => {
    if (!open || !overlayRef.current || document.fullscreenElement) return;
    overlayRef.current.requestFullscreen?.().catch(() => {
      setBrowserFullscreen(false);
    });
  }, [open]);

  const closeFullscreen = async () => {
    if (document.fullscreenElement === overlayRef.current) {
      await document.exitFullscreen?.().catch(() => undefined);
    }
    setOpen(false);
  };

  const header = (fullscreen: boolean) => (
    <div className="flex items-center justify-between gap-3 mb-4">
      <div className="flex items-center gap-2 min-w-0">
        <div className="w-1.5 h-5 bg-indigo-500 rounded shrink-0" />
        <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider truncate">
          {title}
        </h3>
      </div>
      {fullscreen ? (
        <div className="flex items-center gap-2 shrink-0">
          <span className="hidden sm:inline text-[10px] font-bold uppercase tracking-widest text-slate-500">
            {browserFullscreen ? "Browser Fullscreen" : "Expanded View"}
          </span>
          <button
            type="button"
            onClick={closeFullscreen}
            className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-slate-800 bg-slate-950/80 text-slate-400 hover:border-rose-500/40 hover:text-rose-300 transition-colors"
            aria-label="Close fullscreen map"
            title="Close fullscreen map"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      ) : (
        <button
          type="button"
          onClick={() => setOpen(true)}
          className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-slate-800 bg-slate-950/70 text-slate-400 hover:border-indigo-500/40 hover:text-indigo-300 transition-colors disabled:opacity-50"
          aria-label={`Expand ${title}`}
          title={`Expand ${title}`}
          disabled={loading}
        >
          <Maximize2 className="h-4 w-4" />
        </button>
      )}
    </div>
  );

  return (
    <>
      <div className={`glass-card p-6 rounded-2xl border border-slate-800/60 h-[450px] flex flex-col mb-6 relative overflow-hidden bg-slate-950/40 ${className}`}>
        {header(false)}
        {children(false)}
      </div>
      {open && typeof document !== "undefined" && createPortal(
        <div
          ref={overlayRef}
          className="fixed inset-0 z-[1000] bg-[#070b13] p-3 sm:p-5 md:p-6 flex flex-col animate-fade-in"
          role="dialog"
          aria-modal="true"
          aria-label={`${title} fullscreen map`}
        >
          <div className="flex flex-col h-full min-h-0 rounded-2xl border border-slate-800/80 bg-slate-950/95 p-4 sm:p-5 shadow-2xl">
            {header(true)}
            <div className="min-h-0 flex-1 rounded-xl overflow-hidden border border-slate-800/80 bg-[#0c1020] relative">
              {children(true)}
            </div>
            <div className="mt-3 flex items-center justify-between gap-3 text-[10px] font-bold uppercase tracking-widest text-slate-600">
              <span>Esc closes map</span>
              <button
                type="button"
                onClick={closeFullscreen}
                className="inline-flex items-center gap-1.5 text-slate-500 hover:text-indigo-300 transition-colors"
                title="Return to panel view"
              >
                <Minimize2 className="h-3.5 w-3.5" />
                Return to panel
              </button>
            </div>
          </div>
        </div>,
        document.body
      )}
    </>
  );
}
