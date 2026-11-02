"use client";

import { useState } from "react";
import { AlertTriangle, ArrowRight, ChevronDown, ChevronUp, X } from "lucide-react";

interface LowConfidenceRibbonProps {
  fields: string[];
  overallScore?: number | null;
  onFocusField: (fieldName: string) => void;
  className?: string;
}

export function LowConfidenceRibbon({
  fields,
  overallScore,
  onFocusField,
  className = "",
}: LowConfidenceRibbonProps) {
  const [isDismissed, setIsDismissed] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(false);

  if (!fields || fields.length === 0 || isDismissed) {
    return null;
  }

  const formatFieldLabel = (rawName: string): string => {
    const clean = rawName.replace(/^personal_info\./, "").replace(/_/g, " ");
    return clean.charAt(0).toUpperCase() + clean.slice(1);
  };

  return (
    <div
      role="region"
      aria-label="Fields requiring manual verification"
      className={`rounded-lg border border-amber-200 bg-amber-50/70 p-3.5 text-slate-800 transition-all ${className}`}
    >
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div className="flex items-start gap-2.5">
          <AlertTriangle className="w-4 h-4 text-amber-700 shrink-0 mt-0.5" />
          <div className="space-y-0.5">
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-amber-900">
                {fields.length} {fields.length === 1 ? "field needs verification" : "fields need verification"}
              </span>
              {overallScore !== null && overallScore !== undefined && (
                <span className="text-[11px] text-amber-800/80 font-mono tabular-nums">
                  ({Math.round(overallScore * 100)}% overall)
                </span>
              )}
            </div>
            {!isCollapsed && (
              <p className="text-xs text-amber-800/90">
                Low-confidence extraction detected. Select a field to review its source text and correct any errors.
              </p>
            )}
          </div>
        </div>

        {/* Controls: Collapse / Dismiss */}
        <div className="flex items-center gap-1.5 self-end sm:self-center">
          <button
            type="button"
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-1 rounded text-amber-800/70 hover:text-amber-900 hover:bg-amber-100/60 transition-colors"
            aria-label={isCollapsed ? "Expand alert details" : "Collapse alert details"}
            title={isCollapsed ? "Expand" : "Collapse"}
          >
            {isCollapsed ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
          </button>
          <button
            type="button"
            onClick={() => setIsDismissed(true)}
            className="p-1 rounded text-amber-800/70 hover:text-amber-900 hover:bg-amber-100/60 transition-colors"
            aria-label="Dismiss warning banner"
            title="Dismiss"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Actionable field buttons */}
      {!isCollapsed && (
        <div className="mt-3 pt-2.5 border-t border-amber-200/60 flex flex-wrap items-center gap-1.5">
          <span className="text-[11px] font-medium text-amber-900 mr-1">
            Jump to field:
          </span>
          {fields.map((field) => (
            <button
              key={field}
              onClick={() => onFocusField(field)}
              type="button"
              className="inline-flex items-center gap-1 px-2.5 py-1 rounded text-xs font-medium bg-white hover:bg-amber-100 text-slate-800 border border-amber-300 shadow-2xs transition-colors cursor-pointer min-h-[32px]"
            >
              <span>{formatFieldLabel(field)}</span>
              <ArrowRight className="w-3 h-3 text-amber-700" />
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
