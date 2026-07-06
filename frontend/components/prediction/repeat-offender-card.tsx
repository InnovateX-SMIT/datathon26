import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { predictRepeatOffender, fetchShapExplanation } from "@/services/prediction.service";
import type { RepeatOffenderResult, SHAPImpact } from "@/types/prediction";
import { InputField, SelectField, CardContainer } from "./prediction-form";
import { UserCheck, ShieldAlert } from "lucide-react";

const schema = z.object({
  age: z.coerce.number().min(1, "Age must be at least 1").max(120, "Age must be less than 120"),
  occupation: z.string().min(1, "Occupation is required"),
  caste: z.string().min(1, "Caste is required"),
  district: z.string().min(1, "District is required"),
});

type FormData = z.infer<typeof schema>;

interface RepeatOffenderCardProps {
  onSuccess: (result: RepeatOffenderResult, shap: SHAPImpact[]) => void;
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

const CASTE_OPTIONS = [
  { value: "", label: "Select Caste" },
  { value: "General", label: "General" },
  { value: "OBC", label: "OBC" },
  { value: "SC", label: "SC" },
  { value: "ST", label: "ST" },
];

const OCCUPATION_OPTIONS = [
  { value: "", label: "Select Occupation" },
  { value: "Business", label: "Business" },
  { value: "Driver", label: "Driver" },
  { value: "Engineer", label: "Engineer" },
  { value: "Farmer", label: "Farmer" },
  { value: "Government Employee", label: "Government Employee" },
  { value: "Labourer", label: "Labourer" },
  { value: "Salesman", label: "Salesman" },
  { value: "Student", label: "Student" },
  { value: "Teacher", label: "Teacher" },
  { value: "Unemployed", label: "Unemployed" },
];

export default function RepeatOffenderCard({ onSuccess, onSelect, isActive }: RepeatOffenderCardProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<RepeatOffenderResult | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { age: 30, occupation: "", caste: "", district: "" },
  });

  const onSubmit = async (data: FormData) => {
    setLoading(true);
    setError(null);
    onSelect();
    try {
      const res = await predictRepeatOffender(data);
      const shap = await fetchShapExplanation("repeat-offender", data);
      setResult(res);
      onSuccess(res, shap);
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || "Prediction failed. Please ensure the backend engine is running.");
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
      title="Repeat Offender Predictor"
      subtitle="Assess probability of criminal recidivism based on profile variables"
      className={isActive ? "border-indigo-500/50 shadow-[0_0_20px_rgba(99,102,241,0.15)]" : ""}
    >
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <InputField
            label="Suspect Age"
            type="number"
            error={errors.age?.message}
            {...register("age")}
          />
          <SelectField
            label="Caste / Social Group"
            options={CASTE_OPTIONS}
            error={errors.caste?.message}
            {...register("caste")}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <SelectField
            label="Occupation"
            options={OCCUPATION_OPTIONS}
            error={errors.occupation?.message}
            {...register("occupation")}
          />
          <SelectField
            label="District Jurisdiction"
            options={DISTRICT_OPTIONS}
            error={errors.district?.message}
            {...register("district")}
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-800 text-slate-100 font-extrabold text-sm uppercase tracking-wider rounded-xl cursor-pointer transition-all duration-200 flex justify-center items-center gap-2 shadow-[0_4px_15px_rgba(99,102,241,0.3)] hover:shadow-[0_4px_25px_rgba(99,102,241,0.4)]"
        >
          {loading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-slate-100 border-r-2 border-transparent" />
              <span>Analyzing profile...</span>
            </>
          ) : (
            <>
              <UserCheck className="w-4 h-4" />
              <span>Evaluate Recidivism</span>
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
              Recidivism Risk Score
            </span>
            <span className="text-2xl font-black text-slate-100 mt-0.5 block">
              {(result.probability * 100).toFixed(1)}%
            </span>
          </div>
          <span className={`px-4 py-1.5 border rounded-full text-xs font-black tracking-widest ${getRiskBadgeColor(result.risk_level)}`}>
            {result.risk_level} RISK
          </span>
        </div>
      )}
    </CardContainer>
  );
}
