"use client";

import React, { useState, useEffect, useCallback } from "react";
import { 
  FileSpreadsheet, 
  Calendar, 
  Plus, 
  RefreshCw, 
  FileText, 
  ShieldAlert, 
  BookOpen,
  Printer
} from "lucide-react";

import { 
  fetchReports, 
  fetchReportTypes, 
  fetchReportById, 
  generateReport,
  downloadReportCSV
} from "@/features/reports/services/report-service";
import type { Report, ReportSummary, ReportType } from "@/features/reports/types/report";

import ReportSummaryCard from "@/features/reports/components/report-summary-card";
import ReportMetricsGrid from "@/features/reports/components/report-metrics-grid";
import ReportTrendsSection from "@/features/reports/components/report-trends-section";
import ReportNetworkSummary from "@/features/reports/components/report-network-summary";
import ReportRecommendationsSection from "@/features/reports/components/report-recommendations-section";
import ReportAlertsSection from "@/features/reports/components/report-alerts-section";

export default function ReportsPage() {
  const [reports, setReports] = useState<ReportSummary[]>([]);
  const [reportTypes, setReportTypes] = useState<ReportType[]>([]);
  const [selectedReportId, setSelectedReportId] = useState<number | null>(null);
  const [selectedReport, setSelectedReport] = useState<Report | null>(null);
  
  // Loading & Error states
  const [loadingList, setLoadingList] = useState(true);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form states
  const [showGenerateForm, setShowGenerateForm] = useState(false);
  const [titleInput, setTitleInput] = useState("");
  const [typeInput, setTypeInput] = useState("");

  const [downloading, setDownloading] = useState(false);

  const handleDownload = async () => {
    if (!selectedReportId || !selectedReport) return;
    setDownloading(true);
    setError(null);
    try {
      const sanitizedTitle = selectedReport.title.toLowerCase().replace(/[^a-z0-9]+/g, "_");
      const filename = `dossier_intel_${sanitizedTitle}_${selectedReportId}.csv`;
      await downloadReportCSV(selectedReportId, filename);
    } catch (err: unknown) {
      console.error(err);
      setError("Failed to download CSV dossier. Access might be restricted or network error.");
    } finally {
      setDownloading(false);
    }
  };

  const loadReportDetails = useCallback(async (id: number) => {
    setLoadingDetail(true);
    setError(null);
    try {
      const detail = await fetchReportById(id);
      setSelectedReport(detail);
      setSelectedReportId(id);
    } catch (err: unknown) {
      console.error(err);
      setError("Failed to load details for the selected report.");
    } finally {
      setLoadingDetail(false);
    }
  }, []);

  const loadInitialData = useCallback(async () => {
    setLoadingList(true);
    setError(null);
    try {
      const typesData = await fetchReportTypes();
      setReportTypes(typesData);

      const listData = await fetchReports();
      setReports(listData);

      if (listData.length > 0) {
        setSelectedReportId(listData[0].report_id);
        await loadReportDetails(listData[0].report_id);
      }
    } catch (err: unknown) {
      console.error(err);
      setError("Failed to load reports history or report configurations.");
    } finally {
      setLoadingList(false);
    }
  }, [loadReportDetails]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadInitialData();

    const handleDatasetChange = () => {
      loadInitialData();
    };
    window.addEventListener("activeDatasetChanged", handleDatasetChange);
    return () => {
      window.removeEventListener("activeDatasetChanged", handleDatasetChange);
    };
  }, [loadInitialData]);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!titleInput.trim() || !typeInput) return;

    setGenerating(true);
    setError(null);
    try {
      const newReport = await generateReport(titleInput, typeInput);
      
      // Update list
      const listData = await fetchReports();
      setReports(listData);
      
      // Select new report
      setSelectedReport(newReport);
      setSelectedReportId(newReport.report_id);
      
      // Reset form
      setTitleInput("");
      setTypeInput("");
      setShowGenerateForm(false);
    } catch (err: unknown) {
      console.error(err);
      setError("Failed to generate executive report. Please check server logs.");
    } finally {
      setGenerating(false);
    }
  };

  const formatDate = (dateStr: string) => {
    try {
      const d = new Date(dateStr);
      return d.toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "long",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return dateStr;
    }
  };

  const getReportTypeLabel = (typeKey: string) => {
    const t = reportTypes.find(x => x.key === typeKey);
    return t ? t.name : typeKey;
  };

  return (
    <div className="report-page-container min-h-screen pb-12 space-y-8 animate-fade-in relative">
      {/* Background glowing gradients */}
      <div className="absolute top-[10%] right-[10%] w-[400px] h-[400px] rounded-full bg-indigo-500/5 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[20%] left-[5%] w-[350px] h-[350px] rounded-full bg-violet-500/5 blur-[100px] pointer-events-none" />

      {/* Header Block */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-900 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-indigo-500/10 border border-indigo-500/20 rounded-2xl">
              <FileSpreadsheet className="w-6 h-6 text-indigo-400" />
            </div>
            <div>
              <h1 className="text-3xl font-black text-slate-100 uppercase tracking-tight">
                Executive Dossier Briefings
              </h1>
            </div>
          </div>
        </div>

        {/* Action Button */}
        <button
          onClick={() => setShowGenerateForm(!showGenerateForm)}
          className="flex items-center gap-2 px-5 py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-extrabold text-xs uppercase tracking-wider rounded-2xl shadow-lg transition-all w-fit cursor-pointer"
        >
          <Plus className="w-4 h-4" />
          Generate New Dossier
        </button>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-2xl text-red-400 text-xs flex gap-2.5 items-center max-w-4xl animate-shake">
          <ShieldAlert className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* New Report Generation Form (Inline expander) */}
      {showGenerateForm && (
        <div className="glass-card p-6 rounded-3xl border border-indigo-500/20 bg-indigo-950/5 relative overflow-hidden animate-slide-down">
          <div className="absolute inset-0 opacity-5 bg-[radial-gradient(#6366f1_1px,transparent_1px)] [background-size:16px_16px] pointer-events-none" />
          <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider mb-4 flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-indigo-400" />
            New Intelligence dossier parameters
          </h3>

          <form onSubmit={handleGenerate} className="grid grid-cols-1 md:grid-cols-3 gap-6 items-end">
            <div className="space-y-1.5">
              <label htmlFor="title-input" className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                Dossier Title
              </label>
              <input
                id="title-input"
                type="text"
                required
                value={titleInput}
                onChange={(e) => setTitleInput(e.target.value)}
                placeholder="e.g. Bengaluru North Security briefing - Q2"
                className="w-full text-xs bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              />
            </div>

            <div className="space-y-1.5">
              <label htmlFor="type-select" className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                Intelligence Focus / Report Type
              </label>
              <select
                id="type-select"
                required
                value={typeInput}
                onChange={(e) => setTypeInput(e.target.value)}
                className="w-full text-xs bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-3 text-slate-300 focus:outline-none focus:border-indigo-500"
              >
                <option value="">Select report type...</option>
                {reportTypes.map((type) => (
                  <option key={type.key} value={type.key}>
                    {type.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex gap-3">
              <button
                type="submit"
                disabled={generating}
                className="flex-1 flex items-center justify-center gap-2 px-5 py-3 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-extrabold text-xs uppercase tracking-wider rounded-xl transition-all cursor-pointer shadow-md"
              >
                {generating ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    Generating...
                  </>
                ) : (
                  "Create Dossier"
                )}
              </button>
              <button
                type="button"
                onClick={() => setShowGenerateForm(false)}
                className="px-5 py-3 bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 font-extrabold text-xs uppercase tracking-wider rounded-xl transition-all cursor-pointer"
              >
                Cancel
              </button>
            </div>
          </form>

          {/* Helper notes */}
          {typeInput && (
            <p className="text-[10px] text-slate-500 font-medium mt-3 uppercase tracking-wider">
              {reportTypes.find(x => x.key === typeInput)?.description}
            </p>
          )}
        </div>
      )}

      {/* Global CSS injection for printing */}
      <style dangerouslySetInnerHTML={{ __html: `
        @media print {
          /* Reset root background, colors, and layout heights */
          html, body, #__next,
          div[class*="h-screen"],
          div[class*="overflow-hidden"],
          div[class*="overflow-y-auto"],
          main {
            background-color: #ffffff !important;
            background-image: none !important;
            color: #000000 !important;
            height: auto !important;
            min-height: 0 !important;
            max-height: none !important;
            overflow: visible !important;
            position: static !important;
            padding: 0 !important;
            margin: 0 !important;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
          }

          /* Define page margins and layout */
          @page {
            size: A4 portrait;
            margin: 20mm;
          }

          /* Hide UI/navigation components, icons, and non-text visual wrappers */
          .no-print,
          aside,
          nav,
          header,
          footer,
          form,
          button,
          .sidebar-container,
          .navbar-container,
          svg,
          i {
            display: none !important;
            width: 0 !important;
            height: 0 !important;
            overflow: hidden !important;
          }

          /* Remove sidebar padding offsets on the layout wrap */
          .pl-64, .pl-\[4\.5rem\], .pl-18 {
            padding-left: 0 !important;
          }

          /* Flatten the main columns grid */
          .report-page-grid {
            display: block !important;
          }
          
          /* Force container to fill full A4 width */
          .print-container {
            display: block !important;
            width: 100% !important;
            max-width: 100% !important;
            padding: 0 !important;
            margin: 0 !important;
            background: transparent !important;
            position: static !important;
          }
          
          .lg\:col-span-3, .lg\:col-span-4 {
            width: 100% !important;
            max-width: 100% !important;
          }

          /* Strip all boxes, borders, shadows, backgrounds, and roundings */
          .glass-card,
          .report-header-card,
          .report-narrative-card,
          div[class*="bg-slate-950"],
          div[class*="bg-slate-900"],
          div[class*="bg-indigo-950"],
          div[class*="border-slate-800"],
          div[class*="border-slate-900"],
          div[class*="bg-indigo-500/10"],
          div[class*="bg-pink-500/10"],
          div[class*="bg-rose-500/10"],
          div[class*="bg-cyan-500/10"],
          div[class*="bg-red-500/10"],
          div[class*="bg-amber-500/10"],
          div[class*="bg-emerald-500/10"],
          div[class*="bg-slate-950/40"],
          div[class*="bg-slate-950/60"],
          div[class*="bg-indigo-950/5"],
          span[class*="bg-indigo-500/10"],
          span[class*="bg-pink-500/10"],
          span[class*="bg-rose-500/10"],
          span[class*="bg-cyan-500/10"],
          span[class*="bg-red-500/10"],
          span[class*="bg-amber-500/10"],
          span[class*="bg-emerald-500/10"],
          div[class*="border-indigo-500/15"],
          div[class*="border-slate-800/80"] {
            background: transparent !important;
            background-color: transparent !important;
            border: none !important;
            border-radius: 0 !important;
            box-shadow: none !important;
            padding: 0 !important;
            margin: 0 0 16px 0 !important;
            color: #000000 !important;
          }

          /* Remove left accent line on executive briefing */
          .report-narrative-card {
            border-left: none !important;
            padding-left: 0 !important;
          }

          /* Section container styles - simple heading underlays */
          .report-section-container {
            break-inside: avoid !important;
            page-break-inside: avoid !important;
            margin-bottom: 24px !important;
          }

          .report-section-container h3 {
            color: #000000 !important;
            font-size: 12pt !important;
            font-weight: 800 !important;
            border-bottom: 1.5px solid #000000 !important;
            padding-bottom: 4px !important;
            margin-bottom: 12px !important;
            text-transform: uppercase !important;
            letter-spacing: 0.05em !important;
          }

          /* Flatten sub-component grids during print to natural text flow */
          .report-metrics-grid,
          .report-trends-grid,
          .report-network-grid,
          .report-recommendations-grid {
            display: block !important;
          }

          /* Sub-grid block items mapping */
          .report-metrics-grid > div,
          .report-trends-grid > div,
          .report-network-grid > div,
          .report-recommendations-grid > div {
            margin-bottom: 16px !important;
            padding-bottom: 8px !important;
            border-bottom: 1px dashed #cccccc !important;
          }

          .report-metrics-grid > div:last-child,
          .report-trends-grid > div:last-child,
          .report-network-grid > div:last-child,
          .report-recommendations-grid > div:last-child {
            border-bottom: none !important;
            margin-bottom: 0 !important;
            padding-bottom: 0 !important;
          }

          /* Reduce spacing utility classes */
          .space-y-8 > :not([hidden]) ~ :not([hidden]),
          .space-y-3 > :not([hidden]) ~ :not([hidden]) {
            margin-top: 12px !important;
          }

          /* Clean Document Table Formatting: simple lines, no background */
          table {
            width: 100% !important;
            border-collapse: collapse !important;
            margin-top: 8px !important;
            margin-bottom: 8px !important;
          }
          th {
            background-color: transparent !important;
            color: #000000 !important;
            font-weight: 700 !important;
            padding: 4px 8px !important;
            border-bottom: 1.5px solid #000000 !important;
            font-size: 9.5pt !important;
            text-transform: uppercase !important;
            text-align: left !important;
          }
          td {
            padding: 4px 8px !important;
            border-bottom: 1px solid #e2e8f0 !important;
            color: #000000 !important;
            font-size: 9.5pt !important;
          }
          tr {
            break-inside: avoid !important;
          }

          /* Set standard high-contrast document font */
          * {
            color: #000000 !important;
            font-family: "Times New Roman", Times, Georgia, serif !important;
            text-shadow: none !important;
          }

          body {
            font-family: "Times New Roman", Times, Georgia, serif !important;
            font-size: 11pt !important;
            line-height: 1.4 !important;
          }

          /* Badges simplicity: text representation with brackets if needed */
          span[class*="rounded"],
          span[class*="bg-"] {
            background: transparent !important;
            border: none !important;
            padding: 0 !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
          }
        }
      `}} />

      {/* Main Panel Layout */}
      <div className="report-page-grid grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Left Side: Past Dossiers List (Hidden on Print) */}
        <div className="lg:col-span-1 space-y-4 no-print">
          <div className="flex items-center justify-between border-b border-slate-900 pb-2">
            <h2 className="text-xs font-black text-slate-300 uppercase tracking-widest flex items-center gap-2">
              <FileText className="w-4 h-4 text-slate-400" />
              Dossier Registry
            </h2>
            <span className="px-2 py-0.5 bg-slate-950 border border-slate-900 rounded font-mono text-[9px] text-slate-500 font-bold">
              {reports.length}
            </span>
          </div>

          {loadingList ? (
            <div className="space-y-3">
              {[1, 2, 3].map((n) => (
                <div key={n} className="h-24 bg-slate-900/30 border border-slate-900 rounded-xl animate-pulse" />
              ))}
            </div>
          ) : reports.length === 0 ? (
            <div className="p-6 border border-dashed border-slate-850 bg-slate-900/10 rounded-2xl text-center">
              <p className="text-xs text-slate-500">No generated dossiers in the registry. Generate your first briefing to view insights.</p>
            </div>
          ) : (
            <div className="space-y-3 max-h-[70vh] overflow-y-auto pr-1">
              {reports.map((summary) => (
                <ReportSummaryCard
                  key={summary.report_id}
                  summary={summary}
                  isSelected={summary.report_id === selectedReportId}
                  onSelect={loadReportDetails}
                />
              ))}
            </div>
          )}
        </div>

        {/* Right Side: Detailed Intelligence Dossier */}
        <div className="lg:col-span-3 print-container">
          {loadingDetail ? (
            <div className="glass-card p-12 rounded-3xl border border-slate-800/80 flex flex-col items-center justify-center min-h-[50vh]">
              <RefreshCw className="w-8 h-8 text-indigo-400 animate-spin mb-4" />
              <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Assembling dossier intelligence...</p>
            </div>
          ) : !selectedReport ? (
            <div className="glass-card p-12 rounded-3xl border border-slate-800/60 flex flex-col items-center justify-center min-h-[50vh] text-center">
              <BookOpen className="w-12 h-12 text-slate-700 mb-4" />
              <h3 className="text-base font-bold text-slate-300">No Selected Briefing</h3>
              <p className="text-xs text-slate-500 max-w-sm mt-2 leading-relaxed">
                Select an executive dossier from the registry on the left, or generate a fresh, dynamic intelligence summary.
              </p>
            </div>
          ) : (
            <div className="space-y-8 animate-fade-in">
              {/* Dossier Header Card */}
              <div className="report-header-card glass-card p-6 rounded-3xl border border-slate-800/80 relative overflow-hidden flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="absolute inset-0 opacity-5 bg-[radial-gradient(#6366f1_1px,transparent_1px)] [background-size:16px_16px] pointer-events-none" />
                <div className="space-y-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="px-2.5 py-0.5 bg-indigo-500/10 border border-indigo-500/25 text-indigo-400 rounded text-[9px] font-black uppercase tracking-wider">
                      {getReportTypeLabel(selectedReport.report_type)}
                    </span>
                    <span className="text-slate-500 text-[10px]">•</span>
                    <div className="flex items-center gap-1 text-[10px] text-slate-500 font-semibold uppercase">
                      <Calendar className="w-3.5 h-3.5" />
                      {formatDate(selectedReport.generated_at)}
                    </div>
                  </div>
                  <h2 className="text-2xl font-black text-white tracking-tight mt-2">{selectedReport.title}</h2>
                  
                  {/* Model version & Dataset name */}
                  <div className="flex flex-wrap items-center gap-2 mt-2">
                    {selectedReport.dataset_name && (
                      <span className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-450 text-[9px] font-mono font-bold uppercase">
                        Dataset: {selectedReport.dataset_name}
                      </span>
                    )}
                    {selectedReport.model_version && (
                      <span className="px-2 py-0.5 rounded bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-[9px] font-mono font-bold uppercase flex items-center gap-1">
                        Model: {selectedReport.model_version} (Acc: {selectedReport.prediction_accuracy ? (selectedReport.prediction_accuracy * 100).toFixed(1) : "85.0"}%)
                      </span>
                    )}
                  </div>
                  
                  <p className="text-[10px] font-mono text-slate-500 tracking-wider mt-2.5 uppercase">Dossier ID: INTEL-{selectedReport.report_id}</p>
                </div>

                <div className="flex items-center gap-2.5 shrink-0 no-print">
                  <button
                    onClick={() => window.print()}
                    className="flex items-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs uppercase tracking-wider rounded-xl transition-all cursor-pointer shadow-md"
                  >
                    <Printer className="w-4.5 h-4.5" />
                    Print Dossier
                  </button>

                  <button
                    onClick={handleDownload}
                    disabled={downloading}
                    className="flex items-center gap-2 px-4 py-2.5 bg-slate-900 hover:bg-slate-800 disabled:opacity-50 text-slate-350 hover:text-white border border-slate-800 rounded-xl font-bold text-xs uppercase tracking-wider transition-all cursor-pointer shadow-md"
                  >
                    {downloading ? (
                      <RefreshCw className="w-4.5 h-4.5 animate-spin text-indigo-400" />
                    ) : (
                      <FileSpreadsheet className="w-4.5 h-4.5 text-emerald-400" />
                    )}
                    {downloading ? "Exporting..." : "Export CSV"}
                  </button>
                </div>
              </div>

              {/* Executive Summary */}
              <div className="report-narrative-card glass-card p-6 rounded-3xl border border-indigo-500/15 bg-indigo-950/5 relative overflow-hidden">
                <div className="absolute top-0 left-0 w-1 h-full bg-indigo-500" />
                <div className="flex items-center gap-2 mb-3">
                  <FileText className="w-4 h-4 text-indigo-400" />
                  <h3 className="text-xs font-black text-indigo-300 uppercase tracking-widest">
                    Executive Briefing Narrative
                  </h3>
                </div>
                <p className="text-slate-200 text-xs sm:text-sm font-medium leading-relaxed italic pr-2">
                  &ldquo;{selectedReport.executive_summary}&rdquo;
                </p>
              </div>

              {/* Crime Overview Grid */}
              <div className="space-y-3 report-section-container">
                <h3 className="text-xs font-black text-slate-400 uppercase tracking-widest">I. Crime Analytics Overview</h3>
                <ReportMetricsGrid overview={selectedReport.crime_overview} />
              </div>

              {/* Predictive Intelligence */}
              <div className="space-y-3 report-section-container">
                <h3 className="text-xs font-black text-slate-400 uppercase tracking-widest">II. Predictive Risk and Spot Forecasts</h3>
                <ReportTrendsSection insights={selectedReport.predictive_insights} />
              </div>

              {/* Network Intelligence Summary */}
              <div className="space-y-3 report-section-container">
                <h3 className="text-xs font-black text-slate-400 uppercase tracking-widest">III. Criminal Co-Offending Network Intelligence</h3>
                <ReportNetworkSummary insights={selectedReport.network_insights} />
              </div>

              {/* Recommendations Section */}
              <div className="space-y-3 report-section-container">
                <h3 className="text-xs font-black text-slate-400 uppercase tracking-widest">IV. Strategic Operational Recommendations</h3>
                <ReportRecommendationsSection recommendations={selectedReport.recommendations} />
              </div>

              {/* Alerts Section */}
              <div className="space-y-3 report-section-container">
                <h3 className="text-xs font-black text-slate-400 uppercase tracking-widest">V. System & Patrol Escalations</h3>
                <ReportAlertsSection alerts={selectedReport.alerts} />
              </div>
            </div>
          )}
        </div>
      </div>

    </div>
  );
}
