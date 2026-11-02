"use client";

import { useState, useRef, useEffect } from "react";
import { FieldEvidence } from "@/types/resume";
import { ConfidenceBadge } from "@/components/confidence-badge";
import { FileText, Cpu, BookOpen, Layers, Info, X } from "lucide-react";

interface ProvenanceTooltipProps {
  evidence?: FieldEvidence | null;
  fieldName?: string;
  children: React.ReactNode;
  className?: string;
  asBlock?: boolean;
}

export function ProvenanceTooltip({
  evidence,
  fieldName,
  children,
  className = "",
  asBlock = false,
}: ProvenanceTooltipProps) {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    }
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setIsOpen(false);
      }
    }

    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
      document.addEventListener("keydown", handleKeyDown);
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen]);

  if (!evidence) {
    return <>{children}</>;
  }

  const getMethodLabel = (method?: string | null) => {
    switch (method?.toLowerCase()) {
      case "ml":
      case "ner":
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-medium text-slate-600">
            <Cpu className="w-3 h-3 text-slate-400" />
            <span>NER Model</span>
          </span>
        );
      case "semantic":
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-medium text-slate-600">
            <Layers className="w-3 h-3 text-slate-400" />
            <span>Semantic</span>
          </span>
        );
      case "rules":
      default:
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-medium text-slate-600">
            <BookOpen className="w-3 h-3 text-slate-400" />
            <span>Rule-based</span>
          </span>
        );
    }
  };

  return (
    <div
      ref={containerRef}
      className={`relative group ${
        asBlock ? "block" : "inline-flex items-center gap-1.5"
      } ${className}`}
      onMouseEnter={() => setIsOpen(true)}
      onMouseLeave={() => setIsOpen(false)}
    >
      {/* Primary child content */}
      <span className="inline-flex items-center">{children}</span>

      {/* Accessible inspection toggle button */}
      <button
        type="button"
        onClick={(e) => {
          e.stopPropagation();
          setIsOpen(!isOpen);
        }}
        aria-expanded={isOpen}
        aria-haspopup="dialog"
        aria-label={`Inspect source evidence for ${fieldName || "field"}`}
        className="inline-flex items-center justify-center w-4 h-4 rounded text-slate-400 hover:text-[#055B65] hover:bg-[#055B65]/10 transition-colors opacity-70 group-hover:opacity-100 focus:opacity-100 cursor-pointer shrink-0"
        title="Inspect source evidence"
      >
        <Info className="w-3 h-3" />
      </button>

      {/* Popover Inspector */}
      {isOpen && (
        <div
          role="dialog"
          aria-label={`Source evidence for ${fieldName || "field"}`}
          className="absolute z-50 bottom-full left-0 mb-2 w-80 sm:w-96 max-w-[calc(100vw-2rem)] p-3 bg-white rounded-lg border border-[#E0E5E9] shadow-lg text-left text-slate-900 pointer-events-auto"
        >
          {/* Header */}
          <div className="flex items-center justify-between gap-2 pb-2 mb-2 border-b border-[#E0E5E9]">
            <div className="flex items-center gap-1.5 min-w-0">
              <FileText className="w-3.5 h-3.5 text-[#055B65] shrink-0" />
              <span className="text-xs font-semibold text-[#055B65] truncate">
                {fieldName || "Source Evidence"}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <ConfidenceBadge
                score={evidence.confidence}
                calibratedScore={evidence.calibrated_confidence}
                size="sm"
              />
              <button
                type="button"
                onClick={() => setIsOpen(false)}
                className="p-1 rounded text-slate-400 hover:text-slate-600 hover:bg-slate-100"
                aria-label="Close evidence panel"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* Metadata chips */}
          <div className="flex items-center gap-2 mb-2 text-xs text-[#45828B]">
            <span className="font-semibold text-[#055B65]">
              {evidence.source_section || "Document"}
            </span>
            {evidence.page !== null && evidence.page !== undefined && (
              <>
                <span className="text-[#B2C9C5]">•</span>
                <span>Page {evidence.page}</span>
              </>
            )}
            <span className="text-[#B2C9C5]">•</span>
            {getMethodLabel(evidence.extraction_method)}
          </div>

          {/* Source Text Match */}
          <div className="rounded bg-[#FBFCFC] border border-[#E0E5E9] p-2 text-xs">
            <div className="text-[10px] font-semibold text-[#45828B] uppercase tracking-wide mb-1">
              Source Text
            </div>
            <p className="font-mono text-slate-800 text-[11px] leading-relaxed line-clamp-4 select-all">
              &ldquo;{evidence.source_text}&rdquo;
            </p>
          </div>

          {evidence.normalized_value &&
            evidence.normalized_value !== evidence.value && (
              <div className="mt-2 pt-1.5 border-t border-[#E0E5E9] flex items-center justify-between text-xs text-[#45828B]">
                <span className="text-[11px] text-[#45828B]">Normalized</span>
                <span className="font-mono text-[#055B65] text-[11px] font-semibold">
                  {evidence.normalized_value}
                </span>
              </div>
            )}
        </div>
      )}
    </div>
  );
}
