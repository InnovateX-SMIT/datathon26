import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { predictCrimeType, fetchShapExplanation } from "@/services/prediction.service";
import type { CrimeTypeResult, SHAPImpact } from "@/types/prediction";
import { InputField, SelectField, CardContainer } from "./prediction-form";
import { HelpCircle, ShieldAlert } from "lucide-react";

const schema = z.object({
  district: z.string().min(1, "District is required"),
  month: z.coerce.number().min(1, "Month must be 1-12").max(12, "Month must be 1-12"),
  hour: z.coerce.number().min(0, "Hour must be 0-23").max(23, "Hour must be 0-23"),
  day_of_week: z.coerce.number().min(0, "Day must be 0-6").max(6, "Day must be 0-6"),
  historical_crime_count: z.coerce.number().min(0, "Count must be at least 0"),
});

type FormData = z.infer<typeof schema>;

interface CrimeTypeCardProps {
  onSuccess: (result: CrimeTypeResult, shap: SHAPImpact[]) => void;
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

const MONTH_OPTIONS = [
  { value: "1", label: "January" },
  { value: "2", label: "February" },
  { value: "3", label: "March" },
  { value: "4", label: "April" },
  { value: "5", label: "May" },
  { value: "6", label: "June" },
  { value: "7", label: "July" },
  { value: "8", label: "August" },
  { value: "9", label: "September" },
  { value: "10", label: "October" },
  { value: "11", label: "November" },
  { value: "12", label: "December" },
];

const DAY_OPTIONS = [
  { value: "0", label: "Monday" },
  { value: "1", label: "Tuesday" },
  { value: "2", label: "Wednesday" },
  { value: "3", label: "Thursday" },
  { value: "4", label: "Friday" },
  { value: "5", label: "Saturday" },
  { value: "6", label: "Sunday" },
];

export default function CrimeTypeCard({ onSuccess, onSelect, isActive }: CrimeTypeCardProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<CrimeTypeResult | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { district: "", month: 6, hour: 12, day_of_week: 2, historical_crime_count: 100 },
  });

  const onSubmit = async (data: FormData) => {
    setLoading(true);
    setError(null);
    onSelect();
    try {
      const res = await predictCrimeType(data);
      const shap = await fetchShapExplanation("crime-type", data);
      setResult(res);
      onSuccess(res, shap);
    } catch (err) {
      console.error(err);
      setError("Prediction failed. Please ensure the backend engine is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <CardContainer
      title="Crime Type Forecasting"
      subtitle="Predict the most probable upcoming crime category under temporal trends"
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
            label="Target Month"
            options={MONTH_OPTIONS}
            error={errors.month?.message}
            {...register("month")}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <InputField
            label="Target Hour (0-23)"
            type="number"
            min={0}
            max={23}
            error={errors.hour?.message}
            {...register("hour")}
          />
          <SelectField
            label="Day of Week"
            options={DAY_OPTIONS}
            error={errors.day_of_week?.message}
            {...register("day_of_week")}
          />
        </div>

        <InputField
          label="Historical Crime Count in District"
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
              <span>Running classifier...</span>
            </>
          ) : (
            <>
              <HelpCircle className="w-4 h-4" />
              <span>Forecast Crime Type</span>
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
              Predicted Classification
            </span>
            <span className="text-base font-extrabold text-slate-100 mt-0.5 block uppercase">
              {result.crime_type}
            </span>
          </div>
          <span className="px-4 py-1.5 border border-indigo-500/20 bg-indigo-500/10 text-indigo-400 rounded-full text-xs font-black tracking-widest">
            {Math.round(result.confidence * 100)}% CONFIDENCE
          </span>
        </div>
      )}
    </CardContainer>
  );
}
