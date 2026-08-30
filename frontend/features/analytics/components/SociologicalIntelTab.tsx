import React from "react";
import { useSociologicalIntel } from "../hooks/useSociologicalIntel";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { AlertCircle, BrainCircuit, RefreshCw, BarChart2, ShieldAlert, Award, FileText } from "lucide-react";

export default function SociologicalIntelTab() {
  const {
    demographics,
    sociologicalRisk,
    socioEconomic,
    loading,
    error,
    retry,
  } = useSociologicalIntel();

  if (loading) {
    return (
      <div className="min-h-[400px] flex flex-col items-center justify-center gap-3">
        <RefreshCw className="w-8 h-8 text-indigo-500 animate-spin" />
        <p className="text-xs font-mono text-slate-400">Loading sociological intelligence and correlation pipelines...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass-card p-8 rounded-3xl border border-red-500/20 bg-red-500/5 max-w-md w-full mx-auto my-12 text-center">
        <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4 animate-pulse" />
        <h2 className="text-xl font-bold text-slate-200 mb-2">Sync Error</h2>
        <p className="text-sm text-slate-400 mb-6">{error}</p>
        <button
          onClick={retry}
          className="w-full flex items-center justify-center gap-2 py-3 px-4 bg-indigo-600 hover:bg-indigo-550 text-white font-bold text-sm uppercase tracking-wider rounded-xl transition-all cursor-pointer shadow-lg shadow-indigo-600/20"
        >
          <RefreshCw className="w-4 h-4" />
          Retry Pipeline Sync
        </button>
      </div>
    );
  }

  // Safe Fallback Data structures
  const offenderAgeData = demographics?.offender_age_distribution || [];
  const offenderGenderData = demographics?.offender_gender_distribution || [];
  const victimAgeData = demographics?.victim_age_distribution || [];
  const victimGenderData = demographics?.victim_gender_distribution || [];
  
  const ageVsCrime = demographics?.age_vs_crime || [];
  const genderVsCrime = demographics?.gender_vs_crime || [];
  const districtDemos = demographics?.district_demographics || [];
  const dataLimitations = demographics?.data_limitations || [];

  const ageGroupRisk = sociologicalRisk?.age_group_risk || [];
  const genderRisk = sociologicalRisk?.gender_risk || [];
  const districtRisk = sociologicalRisk?.district_risk || [];
  const repeatRisk = sociologicalRisk?.repeat_involvement_risk || [];
  const correlations = sociologicalRisk?.correlations || [];

  // Map charts data
  const ageChartData = offenderAgeData.map((item) => {
    const vMatch = victimAgeData.find((v) => v.category === item.category);
    return {
      name: item.category,
      Offenders: item.count,
      Victims: vMatch ? vMatch.count : 0,
    };
  });

  const genderChartData = offenderGenderData.map((item) => {
    const vMatch = victimGenderData.find((v) => v.category === item.category);
    return {
      name: item.category,
      Offenders: item.count,
      Victims: vMatch ? vMatch.count : 0,
    };
  });

  return (
    <div className="space-y-8 text-slate-200">
      
      {/* Overview Intro Banner */}
      <div className="relative overflow-hidden bg-slate-950/40 border border-indigo-500/10 p-6 rounded-2xl backdrop-blur-md">
        <div className="absolute top-0 right-0 w-[300px] h-[300px] bg-indigo-500/5 blur-3xl rounded-full -mr-20 -mt-20 pointer-events-none" />
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <BrainCircuit className="w-5 h-5 text-indigo-400" />
              <h2 className="text-lg font-bold text-white tracking-wide uppercase">Phase 7: Sociological intelligence</h2>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed max-w-3xl">
              This intelligence module correlates historically logged crimes, offender profiles, and victim demography to identify crime risk drivers.
              The calculations run across active dataset records using fallback prediction heuristic algorithms that map precisely to active ML output scoring.
            </p>
          </div>
          <span className="shrink-0 px-3.5 py-1 text-[10px] font-mono font-bold uppercase tracking-wider text-indigo-300 bg-indigo-500/10 border border-indigo-500/25 rounded-lg self-start md:self-auto">
            AESTHETIC VERIFICATION ACTIVE
          </span>
        </div>
      </div>

      {/* ── 1. DEMOGRAPHIC SUMMARY (Age & Gender distributions) ── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Age Distribution Chart */}
        <div className="glass-card p-6 rounded-2xl border border-slate-800/60 bg-[#0a0f1d]/40 flex flex-col min-h-[350px]">
          <div className="flex items-center gap-2 mb-6">
            <div className="w-1 h-4 bg-indigo-500 rounded" />
            <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">Age Group Distribution</h3>
          </div>
          <div className="flex-1 min-h-0 text-slate-200">
            {ageChartData.length === 0 ? (
              <div className="h-full flex items-center justify-center text-slate-500 text-xs border border-dashed border-slate-800 rounded-xl">No valid age logs found</div>
            ) : (
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={ageChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                  <XAxis dataKey="name" tick={{ fill: "#94a3b8", fontSize: 10 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: "#94a3b8", fontSize: 10 }} axisLine={false} tickLine={false} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: "#0f172a", borderColor: "#1e293b", borderRadius: "8px", fontSize: "12px" }}
                    itemStyle={{ color: "#94a3b8" }}
                    labelStyle={{ color: "#e2e8f0", fontWeight: "bold", textTransform: "uppercase", fontSize: "10px" }}
                  />
                  <Legend iconType="circle" wrapperStyle={{ fontSize: "11px", paddingTop: "10px" }} />
                  <Bar dataKey="Offenders" fill="#6366f1" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="Victims" fill="#ec4899" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Gender Distribution Chart */}
        <div className="glass-card p-6 rounded-2xl border border-slate-800/60 bg-[#0a0f1d]/40 flex flex-col min-h-[350px]">
          <div className="flex items-center gap-2 mb-6">
            <div className="w-1 h-4 bg-indigo-500 rounded" />
            <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">Gender Distribution</h3>
          </div>
          <div className="flex-1 min-h-0 text-slate-200">
            {genderChartData.length === 0 ? (
              <div className="h-full flex items-center justify-center text-slate-500 text-xs border border-dashed border-slate-800 rounded-xl">No valid gender logs found</div>
            ) : (
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={genderChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                  <XAxis dataKey="name" tick={{ fill: "#94a3b8", fontSize: 10 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: "#94a3b8", fontSize: 10 }} axisLine={false} tickLine={false} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: "#0f172a", borderColor: "#1e293b", borderRadius: "8px", fontSize: "12px" }}
                    itemStyle={{ color: "#94a3b8" }}
                    labelStyle={{ color: "#e2e8f0", fontWeight: "bold", textTransform: "uppercase", fontSize: "10px" }}
                  />
                  <Legend iconType="circle" wrapperStyle={{ fontSize: "11px", paddingTop: "10px" }} />
                  <Bar dataKey="Offenders" fill="#6366f1" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="Victims" fill="#ec4899" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

      </div>

      {/* ── 2. CRIME RELATIONSHIPS (Age vs Crime, Gender vs Crime) ── */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        
        {/* Age & Gender vs Crime Category heat grid */}
        <div className="glass-card p-6 rounded-2xl border border-slate-800/60 bg-[#0a0f1d]/40 space-y-4">
          <div className="flex items-center gap-2">
            <div className="w-1 h-4 bg-indigo-500 rounded" />
            <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">Crime Type Association Matrix</h3>
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            
            {/* Age vs Crime table */}
            <div className="space-y-2 border border-slate-800/50 rounded-xl p-3 bg-slate-900/10">
              <h4 className="text-xs font-bold text-indigo-400 font-mono tracking-wider">Age Group vs Crime Category</h4>
              <div className="max-h-[220px] overflow-y-auto text-xs space-y-1.5 scrollbar-thin">
                {ageVsCrime.slice(0, 15).map((item, idx) => (
                  <div key={idx} className="flex justify-between items-center py-1 border-b border-slate-800/40">
                    <span className="text-slate-400 font-medium">{item.age_group}</span>
                    <span className="text-slate-300 font-bold max-w-[120px] truncate">{item.crime_category}</span>
                    <span className="px-1.5 py-0.5 bg-indigo-500/10 text-indigo-400 rounded text-[10px] font-bold font-mono">{item.count}</span>
                  </div>
                ))}
                {ageVsCrime.length === 0 && <p className="text-slate-500 text-center py-4">No records found</p>}
              </div>
            </div>

            {/* Gender vs Crime table */}
            <div className="space-y-2 border border-slate-800/50 rounded-xl p-3 bg-slate-900/10">
              <h4 className="text-xs font-bold text-pink-400 font-mono tracking-wider">Gender vs Crime Category</h4>
              <div className="max-h-[220px] overflow-y-auto text-xs space-y-1.5 scrollbar-thin">
                {genderVsCrime.slice(0, 15).map((item, idx) => (
                  <div key={idx} className="flex justify-between items-center py-1 border-b border-slate-800/40">
                    <span className="text-slate-400 font-medium">{item.gender}</span>
                    <span className="text-slate-300 font-bold max-w-[120px] truncate">{item.crime_category}</span>
                    <span className="px-1.5 py-0.5 bg-pink-500/10 text-pink-400 rounded text-[10px] font-bold font-mono">{item.count}</span>
                  </div>
                ))}
                {genderVsCrime.length === 0 && <p className="text-slate-500 text-center py-4">No records found</p>}
              </div>
            </div>

          </div>
        </div>

        {/* Demographics vs District table */}
        <div className="glass-card p-6 rounded-2xl border border-slate-800/60 bg-[#0a0f1d]/40 flex flex-col justify-between">
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <div className="w-1 h-4 bg-indigo-500 rounded" />
              <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">Geographic Demographic Profiles</h3>
            </div>
            
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-500 font-semibold">
                    <th className="pb-2">District</th>
                    <th className="pb-2 text-center">Avg Offender Age</th>
                    <th className="pb-2">Predominant Gender</th>
                    <th className="pb-2">Predominant Category</th>
                    <th className="pb-2 text-right">Incidents</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/40 text-slate-300">
                  {districtDemos.slice(0, 5).map((item, idx) => (
                    <tr key={idx} className="hover:bg-slate-900/20 transition-colors">
                      <td className="py-2.5 font-bold">{item.district}</td>
                      <td className="py-2.5 text-center font-mono">{item.average_offender_age} yrs</td>
                      <td className="py-2.5"><span className="px-2 py-0.5 text-[10px] rounded font-semibold bg-slate-900 border border-slate-800">{item.predominant_gender}</span></td>
                      <td className="py-2.5 text-slate-400 max-w-[150px] truncate">{item.predominant_crime_category}</td>
                      <td className="py-2.5 text-right font-bold text-indigo-400 font-mono">{item.count.toLocaleString()}</td>
                    </tr>
                  ))}
                  {districtDemos.length === 0 && (
                    <tr>
                      <td colSpan={5} className="py-4 text-center text-slate-500">No district logs available</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
          <span className="text-[10px] text-slate-500 font-mono mt-4 block">* Aggregates based on coordinates mappings and district boundary intersections.</span>
        </div>

      </div>

      {/* ── 3. SOCIOLOGICAL RISK (Demographics vs Existing ML Risk) ── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Demographic Risk Scores (Age and Gender vs Average Heuristic Risk) */}
        <div className="glass-card p-6 rounded-2xl border border-slate-800/60 bg-[#0a0f1d]/40 flex flex-col justify-between">
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <div className="w-1 h-4 bg-indigo-500 rounded" />
              <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">Demographic Risk Correlation</h3>
            </div>
            
            <div className="space-y-3.5">
              
              {/* Age risk bar lines */}
              <div className="space-y-1.5">
                <span className="text-[10px] font-bold text-indigo-400 font-mono tracking-wider">Age Group vs Average Risk Score</span>
                <div className="space-y-1 max-h-[140px] overflow-y-auto">
                  {ageGroupRisk.map((item, idx) => (
                    <div key={idx} className="space-y-0.5">
                      <div className="flex justify-between text-[11px] text-slate-400">
                        <span>{item.group}</span>
                        <span className="font-mono text-indigo-300 font-bold">{(item.average_risk * 100).toFixed(1)}%</span>
                      </div>
                      <div className="h-1.5 w-full bg-slate-905 rounded-full overflow-hidden border border-slate-800">
                        <div className="h-full bg-indigo-500 rounded-full" style={{ width: `${item.average_risk * 100}%` }} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Gender risk bar lines */}
              <div className="space-y-1.5">
                <span className="text-[10px] font-bold text-pink-400 font-mono tracking-wider">Gender vs Average Risk Score</span>
                <div className="space-y-1">
                  {genderRisk.map((item, idx) => (
                    <div key={idx} className="space-y-0.5">
                      <div className="flex justify-between text-[11px] text-slate-400">
                        <span>{item.group}</span>
                        <span className="font-mono text-pink-300 font-bold">{(item.average_risk * 100).toFixed(1)}%</span>
                      </div>
                      <div className="h-1.5 w-full bg-slate-905 rounded-full overflow-hidden border border-slate-800">
                        <div className="h-full bg-pink-500 rounded-full" style={{ width: `${item.average_risk * 100}%` }} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

            </div>
          </div>
        </div>

        {/* District Risk Ranking & Repeat offender risk */}
        <div className="glass-card p-6 rounded-2xl border border-slate-800/60 bg-[#0a0f1d]/40 flex flex-col justify-between">
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <div className="w-1 h-4 bg-indigo-500 rounded" />
              <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">Geographic & Involvement Risk</h3>
            </div>

            <div className="space-y-4">
              
              {/* Repeat involvement risk bar */}
              <div className="space-y-1.5 p-3 rounded-xl border border-indigo-500/10 bg-indigo-500/5">
                <span className="text-[10px] font-bold text-indigo-400 font-mono tracking-wider">Recidivism / Repeat Involvement Risk</span>
                {repeatRisk.map((item, idx) => (
                  <div key={idx} className="space-y-1 mt-1.5">
                    <div className="flex justify-between text-[11px] text-slate-300 font-bold">
                      <span>{item.group}</span>
                      <span className="font-mono text-indigo-300">{(item.average_risk * 100).toFixed(1)}%</span>
                    </div>
                    <div className="h-2 w-full bg-slate-950 rounded-full overflow-hidden border border-slate-800">
                      <div className="h-full bg-indigo-400 rounded-full" style={{ width: `${item.average_risk * 100}%` }} />
                    </div>
                  </div>
                ))}
              </div>

              {/* District risk lists */}
              <div className="space-y-1.5">
                <span className="text-[10px] font-bold text-slate-400 font-mono tracking-wider">Top 4 Districts by Average Calculated Risk</span>
                <div className="space-y-1.5">
                  {districtRisk.slice(0, 4).map((item, idx) => (
                    <div key={idx} className="flex justify-between items-center text-xs py-1 border-b border-slate-800/40">
                      <div className="flex items-center gap-2">
                        <span className="w-4 text-[10px] text-slate-500 font-mono">{idx + 1}.</span>
                        <span className="text-slate-300 font-bold">{item.group}</span>
                      </div>
                      <span className="font-mono text-indigo-400 font-bold">{(item.average_risk * 100).toFixed(1)}%</span>
                    </div>
                  ))}
                </div>
              </div>

            </div>
          </div>
        </div>

        {/* Statistical Correlation Coefficients panel */}
        <div className="glass-card p-6 rounded-2xl border border-slate-800/60 bg-[#0a0f1d]/40 flex flex-col justify-between">
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <div className="w-1 h-4 bg-indigo-500 rounded" />
              <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">Statistical Correlation Metrics</h3>
            </div>

            {correlations.length === 0 ? (
              <div className="flex-1 flex items-center justify-center text-xs text-slate-500 py-6 border border-dashed border-slate-800 rounded-xl">Insufficient sample size to compute correlation coefficients</div>
            ) : (
              <div className="space-y-3.5 text-slate-200">
                {correlations.map((metric, idx) => (
                  <div key={idx} className="border border-slate-800/80 rounded-xl p-3 bg-slate-950/20 space-y-1.5">
                    <div className="flex justify-between items-center">
                      <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{metric.correlation_type}</span>
                      <span className="text-xs font-mono font-bold text-indigo-400 bg-indigo-500/10 px-2 py-0.5 border border-indigo-500/10 rounded">{metric.correlation_coefficient}</span>
                    </div>
                    <div className="text-[10px] text-slate-500 leading-relaxed font-mono">
                      Variables: {metric.variables}<br />
                      Sample size: {metric.sample_size} cases<br />
                      Time range: {metric.time_period}
                    </div>
                    <p className="text-[11px] text-slate-400 italic font-medium leading-normal border-t border-slate-900 pt-1">
                      &quot;{metric.interpretation}&quot;
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
          <span className="text-[10px] text-slate-500 font-mono mt-4 block">* Calculated using active database logs; does not assume causation.</span>
        </div>
      </div>

    </div>
  );
}
