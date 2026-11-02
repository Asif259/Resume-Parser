"use client";

import { CheckCircle2, AlertTriangle, AlertCircle, HelpCircle } from "lucide-react";

interface ConfidenceBadgeProps {
  score: number | null | undefined;
  size?: "sm" | "md" | "lg";
  showLabel?: boolean;
  className?: string;
  calibratedScore?: number | null;
}

export function ConfidenceBadge({
  score,
  size = "md",
  showLabel = false,
  className = "",
  calibratedScore,
}: ConfidenceBadgeProps) {
  if (score === null || score === undefined) {
    return (
      <span
        className={`inline-flex items-center gap-1 font-medium rounded bg-[#E0E5E9]/40 text-slate-600 border border-[#E0E5E9] ${
          size === "sm"
            ? "px-1.5 py-0.5 text-[11px]"
            : size === "lg"
            ? "px-3 py-1 text-xs"
            : "px-2 py-0.5 text-xs"
        } ${className}`}
      >
        <HelpCircle className="w-3 h-3 text-slate-400" />
        <span className="tabular-nums font-mono">Unrated</span>
      </span>
    );
  }

  const pct = Math.round(score <= 1.0 ? score * 100 : score);
  const calibratedPct =
    calibratedScore !== undefined && calibratedScore !== null
      ? Math.round(calibratedScore <= 1.0 ? calibratedScore * 100 : calibratedScore)
      : null;

  let colorStyles = "";
  let icon = null;
  let label = "";

  if (pct >= 80) {
    colorStyles = "bg-[#1BD488]/15 text-[#033c43] border-[#1BD488]/40";
    icon = <CheckCircle2 className="w-3 h-3 text-[#055B65] shrink-0" />;
    label = "High confidence";
  } else if (pct >= 60) {
    colorStyles = "bg-[#B2C9C5]/25 text-[#055B65] border-[#B2C9C5]";
    icon = <CheckCircle2 className="w-3 h-3 text-[#45828B] shrink-0" />;
    label = "Acceptable";
  } else if (pct >= 40) {
    colorStyles = "bg-amber-50 text-amber-900 border-amber-200";
    icon = <AlertTriangle className="w-3 h-3 text-amber-700 shrink-0" />;
    label = "Review needed";
  } else {
    colorStyles = "bg-rose-50 text-rose-900 border-rose-200";
    icon = <AlertCircle className="w-3 h-3 text-rose-700 shrink-0" />;
    label = "Low confidence";
  }

  const sizeStyles = {
    sm: "px-1.5 py-0.5 text-[11px] gap-1",
    md: "px-2 py-0.5 text-xs gap-1.5",
    lg: "px-2.5 py-1 text-xs gap-1.5 font-medium",
  }[size];

  return (
    <span
      className={`inline-flex items-center rounded border font-medium ${colorStyles} ${sizeStyles} ${className}`}
      title={
        calibratedPct !== null
          ? `Raw confidence: ${pct}%, Calibrated: ${calibratedPct}%`
          : `Extraction confidence: ${pct}%`
      }
    >
      {icon}
      <span className="tabular-nums font-mono font-medium">
        {pct}%
      </span>
      {showLabel && (
        <span className="text-[11px] text-slate-600 ml-0.5">
          {label}
        </span>
      )}
    </span>
  );
}
