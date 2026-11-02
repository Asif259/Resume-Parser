"use client";

import { useState } from "react";
import { Experience, FieldEvidence } from "@/types/resume";
import { ProvenanceTooltip } from "@/components/provenance-tooltip";
import { Calendar, ChevronDown, ChevronUp } from "lucide-react";

interface ExperienceTimelineProps {
  experience: Experience[];
  evidence?: Record<string, FieldEvidence> | null;
  className?: string;
}

export function ExperienceTimeline({
  experience,
  evidence,
  className = "",
}: ExperienceTimelineProps) {
  if (!experience || experience.length === 0) {
    return (
      <p className="text-xs text-slate-500 py-3 italic">
        No work experience records extracted.
      </p>
    );
  }

  return (
    <div className={`relative pl-4 sm:pl-6 space-y-6 ${className}`}>
      {/* Subtle continuous vertical timeline guideline */}
      <div
        className="absolute left-[7px] sm:left-[11px] top-2 bottom-2 w-[1.5px] bg-[#E0E5E9]"
        aria-hidden="true"
      />

      {experience.map((item, idx) => (
        <ExperienceTimelineCard
          key={`${item.company}-${idx}`}
          experience={item}
          index={idx}
          evidence={evidence}
        />
      ))}
    </div>
  );
}

interface ExperienceTimelineCardProps {
  experience: Experience;
  index: number;
  evidence?: Record<string, FieldEvidence> | null;
}

export function ExperienceTimelineCard({
  experience,
  index,
  evidence,
}: ExperienceTimelineCardProps) {
  const { job_title, company, start_date, end_date, is_current, description } = experience;
  const [isExpanded, setIsExpanded] = useState(false);

  const roleEvidence =
    evidence?.[`experience[${index}].job_title`] ||
    evidence?.[`experience.${index}.job_title`] ||
    evidence?.["experience"];

  const companyEvidence =
    evidence?.[`experience[${index}].company`] ||
    evidence?.[`experience.${index}.company`];

  const dateEvidence =
    evidence?.[`experience[${index}].date`] ||
    evidence?.[`experience[${index}].start_date`];

  const displayEnd = is_current ? "Present" : end_date || "Present";
  const dateFormatted =
    start_date || end_date
      ? `${start_date || "Unknown"} – ${displayEnd}`
      : null;

  const hasLongDescription = description && description.length > 3;
  const visibleBullets = isExpanded || !hasLongDescription
    ? description
    : description.slice(0, 3);

  return (
    <div className="relative group">
      {/* Timeline Node */}
      <div
        className={`absolute -left-[20px] sm:-left-[26px] top-1.5 w-3.5 h-3.5 rounded-full border-2 transition-colors ${
          is_current ? "border-[#055B65] bg-[#1BD488]" : "border-[#B2C9C5] bg-white"
        }`}
        aria-hidden="true"
      />

      {/* Row container: clean section without heavy card & shadow */}
      <div className="space-y-1.5">
        <div className="flex flex-col sm:flex-row sm:items-baseline sm:justify-between gap-1">
          <div className="flex flex-wrap items-center gap-2">
            <ProvenanceTooltip evidence={roleEvidence} fieldName="Job Title">
              <h4 className="text-sm font-semibold text-slate-900 hover:text-[#055B65] transition-colors">
                {job_title || "Untitled Role"}
              </h4>
            </ProvenanceTooltip>

            {is_current && (
              <span className="inline-flex items-center px-1.5 py-0.2 rounded text-[10px] font-semibold bg-[#1BD488]/15 text-[#033c43] border border-[#1BD488]/40">
                Current
              </span>
            )}
          </div>

          {dateFormatted && (
            <ProvenanceTooltip evidence={dateEvidence} fieldName="Tenure">
              <span className="inline-flex items-center gap-1 text-xs text-[#45828B] tabular-nums font-mono">
                <Calendar className="w-3 h-3 text-[#45828B]" />
                <span>{dateFormatted}</span>
              </span>
            </ProvenanceTooltip>
          )}
        </div>

        {company && (
          <ProvenanceTooltip evidence={companyEvidence} fieldName="Company">
            <p className="text-xs font-semibold text-[#055B65]">
              {company}
            </p>
          </ProvenanceTooltip>
        )}

        {description && description.length > 0 && (
          <div className="pt-1 space-y-1.5">
            <ul className="space-y-1 pl-4 list-disc marker:text-[#B2C9C5] text-xs text-slate-600 leading-relaxed">
              {visibleBullets.map((bullet, bIdx) => (
                <li key={bIdx}>{bullet}</li>
              ))}
            </ul>

            {hasLongDescription && (
              <button
                type="button"
                onClick={() => setIsExpanded(!isExpanded)}
                aria-expanded={isExpanded}
                className="inline-flex items-center gap-1 min-h-[32px] py-1 text-[11px] font-semibold text-[#055B65] hover:text-[#033c43] transition-colors cursor-pointer rounded focus:outline-none focus-visible:ring-2 focus-visible:ring-[#055B65]"
              >
                {isExpanded ? (
                  <>
                    <ChevronUp className="w-3 h-3 text-[#055B65]" />
                    <span>Show less</span>
                  </>
                ) : (
                  <>
                    <ChevronDown className="w-3 h-3 text-[#055B65]" />
                    <span>Show {description.length - 3} more bullets</span>
                  </>
                )}
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
