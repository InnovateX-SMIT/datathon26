import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { predictCrimeRisk, fetchShapExplanation } from "@/services/prediction.service";
import type { CrimeRiskResult, SHAPImpact } from "@/types/prediction";
import { InputField, SelectField, CardContainer } from "./prediction-form";
import { BarChart3, ShieldAlert } from "lucide-react";

const schema = z.object({
  district: z.string().min(1, "District is required"),
  crime_category: z.string().min(1, "Crime category is required"),
  historical_crime_count: z.coerce.number().min(0, "Count must be at least 0"),
});

type FormData = z.infer<typeof schema>;

interface CrimeRiskCardProps {
  onSuccess: (result: CrimeRiskResult, shap: SHAPImpact[]) => void;
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

const CATEGORY_OPTIONS = [
  { value: "", label: "Select Crime Category" },
  { value: "Assault", label: "Assault" },
  { value: "Burglary", label: "Burglary" },
  { value: "Cyber Crime", label: "Cyber Crime" },
  { value: "Drug Offense", label: "Drug Offense" },
  { value: "Fraud", label: "Fraud" },
  { value: "Kidnapping", label: "Kidnapping" },
  { value: "Murder", label: "Murder" },
  { value: "Robbery", label: "Robbery" },
  { value: "Theft", label: "Theft" },
];

export default function CrimeRiskCard({ onSuccess, onSelect, isActive }: CrimeRiskCardProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<CrimeRiskResult | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { district: "", crime_category: "", historical_crime_count: 50 },
  });

  const onSubmit = async (data: FormData) => {
    setLoading(true);
    setError(null);
    onSelect();
    try {
      const res = await predictCrimeRisk(data);
      const shap = await fetchShapExplanation("crime-risk", data);
      setResult(res);
      onSuccess(res, shap);
    } catch (err) {
      console.error(err);
      setError("Prediction failed. Please ensure the backend engine is running.");
    } finally {
      setLoading(false);
    }
  };

  const getRiskBadgeColor = (level: string) => {
    switch (level) {
      case "HIGH":
        return "text-red-400 bg-red-500/10 border-red-500/20";
      case "MEDIUM":
        return "text-amber-400 bg-amber-500/10 border-amber-500/20";
      case "LOW":
        return "text-green-400 bg-green-500/10 border-green-500/20";
      default:
        return "text-slate-400 bg-slate-500/10 border-slate-500/20";
    }
  };

  return (
    <CardContainer
      title="Crime Occurrence Risk Scoring"
      subtitle="Assess general probability index of specific offenses per district"
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
          <SelectField
            label="Crime Group"
            options={CATEGORY_OPTIONS}
            error={errors.crime_category?.message}
            {...register("crime_category")}
          />
        </div>

        <InputField
          label="Historical Crime Count in Area"
          type="number"
          error={errors.historical_crime_count?.message}
          {...register("historical_crime_count")}
        />

        <button
          type="submit"
          disabled={loading}
          className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-800 text-slate-100 font-extrabold text-sm uppercase tracking-wider rounded-xl cursor-pointer transition-all duration-200 flex justify-center items-center gap-2 shadow-[0_4px_15px_rgba(99,102,241,0.3)] hover:shadow-[0_4px_25px_rgba(99,102,241,0.4)]"
        >
          {loading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-slate-100 border-r-2 border-transparent" />
              <span>Calculating score...</span>
            </>
          ) : (
            <>
              <BarChart3 className="w-4 h-4" />
              <span>Evaluate Risk Index</span>
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
              Calculated Risk Index
            </span>
            <span className="text-2xl font-black text-slate-100 mt-0.5 block">
              {result.risk_score.toFixed(1)} / 100
            </span>
          </div>
          <span className={`px-4 py-1.5 border rounded-full text-xs font-black tracking-widest ${getRiskBadgeColor(result.risk_level)}`}>
            {result.risk_level} LEVEL
          </span>
        </div>
      )}
    </CardContainer>
  );
}
