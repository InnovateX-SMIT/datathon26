import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { predictHotspot, fetchShapExplanation } from "@/services/prediction.service";
import type { HotspotResult, SHAPImpact } from "@/types/prediction";
import { InputField, SelectField, CardContainer } from "./prediction-form";
import { Flame, ShieldAlert } from "lucide-react";

const schema = z.object({
  district: z.string().min(1, "District is required"),
  trend_metrics: z.coerce.number().min(0, "Metrics must be at least 0"),
  historical_crime_growth: z.coerce.number().min(0, "Growth must be positive"),
});

type FormData = z.infer<typeof schema>;

interface HotspotCardProps {
  onSuccess: (result: HotspotResult, shap: SHAPImpact[]) => void;
  onSelect: () => void;
  isActive: boolean;
}

const DISTRICT_OPTIONS = [
  { value: "", label: "Select District" },
  { value: "Ballari", label: "Ballari" },
  { value: "Belagavi", label: "Belagavi" },
  { value: "Bengaluru Rural", label: "Bengaluru Rural" },
  { value: "Bengaluru Urban", label: "Bengaluru Urban" },
  { value: "Hubballi", label: "Hubballi" },
  { value: "Kalaburagi", label: "Kalaburagi" },
  { value: "Mangaluru", label: "Mangaluru" },
  { value: "Mysuru", label: "Mysuru" },
  { value: "Shivamogga", label: "Shivamogga" },
  { value: "Tumakuru", label: "Tumakuru" },
];

export default function HotspotCard({ onSuccess, onSelect, isActive }: HotspotCardProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<HotspotResult | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { district: "", trend_metrics: 50, historical_crime_growth: 1.1 },
  });

  const onSubmit = async (data: FormData) => {
    setLoading(true);
    setError(null);
    onSelect();
    try {
      const res = await predictHotspot(data);
      const shap = await fetchShapExplanation("hotspot", data);
      setResult(res);
      onSuccess(res, shap);
    } catch (err) {
      console.error(err);
      setError("Prediction failed. Please ensure the backend engine is running.");
    } finally {
      setLoading(false);
    }
  };

  const getTrendBadgeColor = (trend: string) => {
    switch (trend) {
      case "RISING":
        return "text-red-400 bg-red-500/10 border-red-500/20 animate-pulse";
      case "STABLE":
        return "text-indigo-400 bg-indigo-500/10 border-indigo-500/20";
      case "FALLING":
        return "text-green-400 bg-green-500/10 border-green-500/20";
      default:
        return "text-slate-400 bg-slate-500/10 border-slate-500/20";
    }
  };

  return (
    <CardContainer
      title="Emerging Hotspot Forecasting"
      subtitle="Analyze geographical indices for upcoming spatial crime clusters"
      className={isActive ? "border-indigo-500/50 shadow-[0_0_20px_rgba(99,102,241,0.15)]" : ""}
    >
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <SelectField
            label="District Name"
            options={DISTRICT_OPTIONS}
            error={errors.district?.message}
            {...register("district")}
          />
          <InputField
            label="Historical Crime Growth Index"
            type="number"
            step="0.01"
            error={errors.historical_crime_growth?.message}
            {...register("historical_crime_growth")}
          />
        </div>

        <InputField
          label="Recent Trend Count (Crime Count)"
          type="number"
          error={errors.trend_metrics?.message}
          {...register("trend_metrics")}
        />

        <button
          type="submit"
          disabled={loading}
          className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-800 text-slate-100 font-extrabold text-sm uppercase tracking-wider rounded-xl cursor-pointer transition-all duration-200 flex justify-center items-center gap-2 shadow-[0_4px_15px_rgba(99,102,241,0.3)] hover:shadow-[0_4px_25px_rgba(99,102,241,0.4)]"
        >
          {loading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-slate-100 border-r-2 border-transparent" />
              <span>Running analyzer...</span>
            </>
          ) : (
            <>
              <Flame className="w-4 h-4" />
              <span>Forecast Hotspot Index</span>
            </>
          )}
        </button>
      </form>

      {error && (
        <div className="mt-4 p-3 bg-red-500/10 border border-red-500/20 rounded-xl text-red-500 text-xs font-bold flex items-start gap-2">
          <ShieldAlert className="w-4 h-4 shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {result && !loading && (
        <div className="mt-5 pt-4 border-t border-slate-800/50 flex items-center justify-between">
          <div>
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block">
              Hotspot Probability Index
            </span>
            <span className="text-2xl font-black text-slate-100 mt-0.5 block">
              {(result.hotspot_probability * 100).toFixed(1)}%
            </span>
          </div>
          <span className={`px-4 py-1.5 border rounded-full text-xs font-black tracking-widest ${getTrendBadgeColor(result.trend)}`}>
            {result.trend} TREND
          </span>
        </div>
      )}
    </CardContainer>
  );
}
