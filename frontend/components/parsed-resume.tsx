"use client";

import { useState, useRef } from "react";
import { ParsedResume } from "@/types/resume";
import { SkillBadges } from "@/components/skill-badges";
import { ExperienceTimeline } from "@/components/experience-timeline";
import { ProvenanceTooltip } from "@/components/provenance-tooltip";
import { ConfidenceBadge } from "@/components/confidence-badge";
import { LowConfidenceRibbon } from "@/components/low-confidence-ribbon";
import {
  Mail,
  Phone,
  MapPin,
  Award,
  Globe,
  FileText,
  ChevronDown,
  ChevronUp,
  Copy,
  Check,
  FolderGit2,
  ExternalLink,
  Edit3,
  RotateCcw,
  Cpu,
  Layers,
  BookOpen,
  Download,
} from "lucide-react";

interface ParsedResumeViewProps {
  resume: ParsedResume;
  filename?: string;
}

export function ParsedResumeView({ resume, filename }: ParsedResumeViewProps) {
  const [copied, setCopied] = useState(false);
  const [showRawText, setShowRawText] = useState(false);
  const [focusedField, setFocusedField] = useState<string | null>(null);

  // Local Review & Draft Mode State
  const [isReviewMode, setIsReviewMode] = useState(false);
  const [draftResume, setDraftResume] = useState<ParsedResume>(resume);
  const [draftSavedMessage, setDraftSavedMessage] = useState(false);

  const fieldRefs = useRef<Record<string, HTMLElement | null>>({});

  const {
    personal_info,
    professional_summary,
    skills,
    experience,
    education,
    certifications,
    projects,
    languages,
    evidence,
    confidence_score,
    low_confidence_fields,
    raw_text,
  } = draftResume;

  // Single-click scroll and accessible focus
  const handleFocusField = (fieldName: string) => {
    setFocusedField(fieldName);
    const targetElement = fieldRefs.current[fieldName];
    if (targetElement) {
      targetElement.scrollIntoView({ behavior: "smooth", block: "center" });
      // Shift keyboard focus to the target element or its first focusable child
      if (typeof targetElement.focus === "function") {
        targetElement.focus();
      } else {
        const focusable = targetElement.querySelector<HTMLElement>(
          "input, textarea, button, a, [tabindex]"
        );
        if (focusable) focusable.focus();
      }
    }
    setTimeout(() => {
      setFocusedField((curr) => (curr === fieldName ? null : curr));
    }, 2500);
  };

  const handleCopyJson = () => {
    navigator.clipboard.writeText(JSON.stringify(draftResume, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadDraftJson = () => {
    const jsonStr = JSON.stringify(draftResume, null, 2);
    const blob = new Blob([jsonStr], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    const safeName = (draftResume.personal_info?.name || "resume")
      .toLowerCase()
      .replace(/[^a-z0-9]/g, "_");
    a.download = `${safeName}_audited.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    setDraftSavedMessage(true);
    setTimeout(() => setDraftSavedMessage(false), 3000);
  };

  const handleResetDraft = () => {
    setDraftResume(resume);
  };

  // Inspect extraction method distribution
  const methodCounts = { ml: 0, rules: 0, semantic: 0 };
  if (evidence) {
    Object.values(evidence).forEach((ev) => {
      const m = ev.extraction_method?.toLowerCase();
      if (m === "ml" || m === "ner") methodCounts.ml++;
      else if (m === "semantic") methodCounts.semantic++;
      else methodCounts.rules++;
    });
  }

  const nameEvidence = evidence?.["personal_info.name"] || evidence?.["name"];
  const emailEvidence = evidence?.["personal_info.email"] || evidence?.["email"];
  const phoneEvidence = evidence?.["personal_info.phone"] || evidence?.["phone"];
  const locationEvidence = evidence?.["personal_info.location"] || evidence?.["location"];
  const linkedinEvidence = evidence?.["personal_info.linkedin"] || evidence?.["linkedin"];
  const githubEvidence = evidence?.["personal_info.github"] || evidence?.["github"];
  const summaryEvidence = evidence?.["professional_summary"] || evidence?.["summary"];

  return (
    <div className="space-y-6">
      {/* Low Confidence Warning Ribbon */}
      {low_confidence_fields && low_confidence_fields.length > 0 && (
        <LowConfidenceRibbon
          fields={low_confidence_fields}
          overallScore={confidence_score}
          onFocusField={handleFocusField}
        />
      )}

      {/* AI Extraction Confidence Overview Panel */}
      <section
        aria-label="Extraction Confidence and Provenance"
        className="rounded-xl border border-[#E0E5E9] bg-white p-5 space-y-4 shadow-2xs"
      >
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[#E0E5E9]">
          <div className="space-y-0.5">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-[#055B65]">
              Extraction Confidence & Provenance Overview
            </h2>
            <p className="text-xs text-[#45828B]">
              Calibrated model probability across detected entities and source document text.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setIsReviewMode(!isReviewMode)}
              className={`inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold border transition-colors cursor-pointer min-h-[36px] ${
                isReviewMode
                  ? "bg-[#055B65] text-white border-[#055B65] hover:bg-[#033c43]"
                  : "bg-white text-[#055B65] border-[#E0E5E9] hover:bg-[#FBFCFC]"
              }`}
            >
              <Edit3 className="w-3.5 h-3.5" />
              <span>{isReviewMode ? "Finish Review" : "Local Review Mode"}</span>
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
          {/* Overall Confidence Index */}
          <div className="p-3.5 rounded-lg border border-[#E0E5E9] bg-[#FBFCFC] space-y-1.5">
            <span className="text-[#45828B] text-[11px] font-medium">Confidence Score</span>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold font-mono tabular-nums text-[#055B65]">
                {confidence_score !== null && confidence_score !== undefined
                  ? `${Math.round(confidence_score * 100)}%`
                  : "Unrated"}
              </span>
              <ConfidenceBadge score={confidence_score} size="sm" />
            </div>
            <div className="w-full bg-[#E0E5E9] h-1.5 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full ${
                  (confidence_score ?? 0) >= 0.8
                    ? "bg-[#1BD488]"
                    : (confidence_score ?? 0) >= 0.6
                    ? "bg-[#45828B]"
                    : "bg-amber-500"
                }`}
                style={{
                  width: `${Math.min(100, Math.round((confidence_score ?? 0) * 100))}%`,
                }}
              />
            </div>
          </div>

          {/* Provenance Links Tracked */}
          <div className="p-3.5 rounded-lg border border-[#E0E5E9] bg-[#FBFCFC] space-y-1">
            <span className="text-[#45828B] text-[11px] font-medium">Verified Fields</span>
            <div className="text-2xl font-bold font-mono tabular-nums text-[#055B65]">
              {evidence ? Object.keys(evidence).length : 0}
            </div>
            <p className="text-[11px] text-[#45828B]">
              With exact source document excerpts
            </p>
          </div>

          {/* Extraction Methods Used */}
          <div className="p-3.5 rounded-lg border border-[#E0E5E9] bg-[#FBFCFC] space-y-1">
            <span className="text-[#45828B] text-[11px] font-medium">Extraction Methods</span>
            <div className="flex flex-wrap gap-1.5 pt-0.5">
              {methodCounts.ml > 0 && (
                <span className="inline-flex items-center gap-1 text-[10px] font-mono px-1.5 py-0.5 rounded bg-[#055B65]/10 text-[#055B65] border border-[#B2C9C5]/50">
                  <Cpu className="w-2.5 h-2.5" />
                  NER: {methodCounts.ml}
                </span>
              )}
              {methodCounts.rules > 0 && (
                <span className="inline-flex items-center gap-1 text-[10px] font-mono px-1.5 py-0.5 rounded bg-[#E0E5E9]/50 text-[#055B65] border border-[#E0E5E9]">
                  <BookOpen className="w-2.5 h-2.5" />
                  Rules: {methodCounts.rules}
                </span>
              )}
              {methodCounts.semantic > 0 && (
                <span className="inline-flex items-center gap-1 text-[10px] font-mono px-1.5 py-0.5 rounded bg-[#1BD488]/15 text-[#033c43] border border-[#1BD488]/40">
                  <Layers className="w-2.5 h-2.5" />
                  Semantic: {methodCounts.semantic}
                </span>
              )}
            </div>
          </div>

          {/* Flagged Review Fields */}
          <div className="p-3.5 rounded-lg border border-[#E0E5E9] bg-[#FBFCFC] space-y-1">
            <span className="text-[#45828B] text-[11px] font-medium">Review Status</span>
            <div className="flex items-center gap-2">
              <span
                className={`text-2xl font-bold font-mono tabular-nums ${
                  (low_confidence_fields?.length ?? 0) > 0 ? "text-amber-800" : "text-[#055B65]"
                }`}
              >
                {low_confidence_fields?.length ?? 0}
              </span>
              <span className="text-xs text-[#45828B]">
                {(low_confidence_fields?.length ?? 0) === 1 ? "flagged item" : "flagged items"}
              </span>
            </div>
            <p className="text-[11px] text-[#45828B]">
              {(low_confidence_fields?.length ?? 0) === 0
                ? "All extractions meet confidence criteria"
                : "Manual verification recommended"}
            </p>
          </div>
        </div>
      </section>

      {/* Local Review Mode Dedicated Form Card (Forms / Inputs UX rules) */}
      {isReviewMode && (
        <section
          aria-label="Local Review and Edit Form"
          className="rounded-xl border border-[#B2C9C5] bg-[#055B65]/5 p-5 space-y-4"
        >
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[#B2C9C5]/50">
            <div>
              <h3 className="text-sm font-semibold text-[#055B65] flex items-center gap-2">
                <Edit3 className="w-4 h-4 text-[#055B65]" />
                <span>Local Candidate Field Editor</span>
              </h3>
              <p className="text-xs text-[#45828B] mt-0.5">
                Edit extracted fields locally. Export the audited data as JSON when complete.
              </p>
            </div>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={handleResetDraft}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white border border-[#E0E5E9] text-[#055B65] hover:bg-[#FBFCFC] text-xs font-semibold cursor-pointer min-h-[36px]"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Reset Fields</span>
              </button>
              <button
                type="button"
                onClick={handleDownloadDraftJson}
                className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-[#055B65] hover:bg-[#033c43] text-white text-xs font-semibold cursor-pointer shadow-xs min-h-[36px]"
              >
                <Download className="w-3.5 h-3.5 text-[#1BD488]" />
                <span>Export Audited JSON</span>
              </button>
            </div>
          </div>

          {draftSavedMessage && (
            <div className="p-2.5 rounded bg-[#1BD488]/15 border border-[#1BD488]/40 text-xs font-medium text-[#033c43] flex items-center gap-1.5">
              <Check className="w-4 h-4 text-[#055B65]" />
              <span>Audited JSON file generated and downloaded successfully.</span>
            </div>
          )}

          {/* Form Fields Grid with persistent labels */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            {/* Full Name */}
            <div className="space-y-1">
              <label
                htmlFor="review-name"
                className="font-semibold text-slate-800 flex items-center justify-between"
              >
                <span>Full Name</span>
                <span className="text-[10px] text-[#45828B] font-normal">Candidate Identity</span>
              </label>
              <input
                id="review-name"
                type="text"
                value={personal_info?.name || ""}
                onChange={(e) =>
                  setDraftResume((prev) => ({
                    ...prev,
                    personal_info: { ...prev.personal_info, name: e.target.value },
                  }))
                }
                className="w-full px-3 py-2 rounded-lg border border-[#E0E5E9] bg-white text-slate-900 text-xs focus:outline-none focus:ring-2 focus:ring-[#055B65] focus:border-[#055B65]"
                placeholder="e.g. Jane Doe"
              />
            </div>

            {/* Email Address */}
            <div className="space-y-1">
              <label
                htmlFor="review-email"
                className="font-semibold text-slate-800 flex items-center justify-between"
              >
                <span>Email Address</span>
                <span className="text-[10px] text-[#45828B] font-normal">Primary contact</span>
              </label>
              <input
                id="review-email"
                type="email"
                value={personal_info?.email || ""}
                onChange={(e) =>
                  setDraftResume((prev) => ({
                    ...prev,
                    personal_info: { ...prev.personal_info, email: e.target.value },
                  }))
                }
                className="w-full px-3 py-2 rounded-lg border border-[#E0E5E9] bg-white text-slate-900 text-xs font-mono focus:outline-none focus:ring-2 focus:ring-[#055B65] focus:border-[#055B65]"
                placeholder="candidate@example.com"
              />
            </div>

            {/* Phone Number */}
            <div className="space-y-1">
              <label
                htmlFor="review-phone"
                className="font-semibold text-slate-800 flex items-center justify-between"
              >
                <span>Phone Number</span>
                <span className="text-[10px] text-[#45828B] font-normal">Optional</span>
              </label>
              <input
                id="review-phone"
                type="tel"
                value={personal_info?.phone || ""}
                onChange={(e) =>
                  setDraftResume((prev) => ({
                    ...prev,
                    personal_info: { ...prev.personal_info, phone: e.target.value },
                  }))
                }
                className="w-full px-3 py-2 rounded-lg border border-[#E0E5E9] bg-white text-slate-900 text-xs font-mono focus:outline-none focus:ring-2 focus:ring-[#055B65] focus:border-[#055B65]"
                placeholder="+1 (555) 000-0000"
              />
            </div>

            {/* Location */}
            <div className="space-y-1">
              <label
                htmlFor="review-location"
                className="font-semibold text-slate-800 flex items-center justify-between"
              >
                <span>Location</span>
                <span className="text-[10px] text-[#45828B] font-normal">City, Region</span>
              </label>
              <input
                id="review-location"
                type="text"
                value={personal_info?.location || ""}
                onChange={(e) =>
                  setDraftResume((prev) => ({
                    ...prev,
                    personal_info: { ...prev.personal_info, location: e.target.value },
                  }))
                }
                className="w-full px-3 py-2 rounded-lg border border-[#E0E5E9] bg-white text-slate-900 text-xs focus:outline-none focus:ring-2 focus:ring-[#055B65] focus:border-[#055B65]"
                placeholder="San Francisco, CA"
              />
            </div>

            {/* Summary (Full Width) */}
            <div className="space-y-1 sm:col-span-2">
              <label
                htmlFor="review-summary"
                className="font-semibold text-slate-800 flex items-center justify-between"
              >
                <span>Professional Summary</span>
                <span className="text-[10px] text-[#45828B] font-normal">Candidate Overview</span>
              </label>
              <textarea
                id="review-summary"
                rows={3}
                value={professional_summary || ""}
                onChange={(e) =>
                  setDraftResume((prev) => ({
                    ...prev,
                    professional_summary: e.target.value,
                  }))
                }
                className="w-full px-3 py-2 rounded-lg border border-[#E0E5E9] bg-white text-slate-900 text-xs leading-relaxed focus:outline-none focus:ring-2 focus:ring-[#055B65] focus:border-[#055B65]"
                placeholder="Brief professional background and career highlights..."
              />
            </div>
          </div>
        </section>
      )}

      {/* Candidate Profile Document Canvas */}
      <div className="rounded-xl border border-[#E0E5E9] bg-white overflow-hidden shadow-2xs">
        {/* Candidate Profile Header */}
        <div
          ref={(el) => {
            fieldRefs.current["name"] = el;
            fieldRefs.current["personal_info.name"] = el;
          }}
          tabIndex={-1}
          className={`p-6 sm:p-8 border-b border-[#E0E5E9] transition-colors ${
            focusedField === "name" || focusedField === "personal_info.name"
              ? "bg-amber-50/40 ring-2 ring-inset ring-amber-300"
              : ""
          }`}
        >
          <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
            <div className="space-y-1 flex-1 max-w-xl">
              <div className="flex items-center gap-2 text-xs text-[#45828B]">
                <span className="font-semibold text-[#055B65]">Candidate Profile</span>
                {filename && (
                  <>
                    <span className="text-[#B2C9C5]">•</span>
                    <span className="font-mono text-[11px] truncate max-w-[200px] text-[#45828B]">
                      {filename}
                    </span>
                  </>
                )}
              </div>

              <ProvenanceTooltip evidence={nameEvidence} fieldName="Candidate Name">
                <h1 className="text-2xl sm:text-3xl font-bold text-[#055B65] tracking-tight">
                  {personal_info?.name || "Unnamed Candidate"}
                </h1>
              </ProvenanceTooltip>
            </div>

            {/* Actions: Copy JSON */}
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={handleCopyJson}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg border border-[#E0E5E9] text-[#055B65] hover:bg-[#055B65]/5 transition-colors cursor-pointer min-h-[36px]"
              >
                {copied ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-[#055B65]" />
                    <span className="text-[#055B65]">Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5 text-[#45828B]" />
                    <span>Copy JSON</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Contact Details Row */}
          <div className="mt-4 pt-4 border-t border-[#E0E5E9] flex flex-wrap items-center gap-y-2 gap-x-4 text-xs text-slate-600">
            {/* Email */}
            {personal_info?.email && (
              <div
                ref={(el) => {
                  fieldRefs.current["email"] = el;
                  fieldRefs.current["personal_info.email"] = el;
                }}
                tabIndex={-1}
                className={`transition-colors rounded ${
                  focusedField?.includes("email") ? "bg-amber-100/60 p-0.5" : ""
                }`}
              >
                <ProvenanceTooltip evidence={emailEvidence} fieldName="Email">
                  <a
                    href={`mailto:${personal_info.email}`}
                    className="inline-flex items-center gap-1.5 hover:text-[#055B65] transition-colors"
                  >
                    <Mail className="w-3.5 h-3.5 text-[#45828B]" />
                    <span className="font-mono text-[11px] text-slate-700">{personal_info.email}</span>
                  </a>
                </ProvenanceTooltip>
              </div>
            )}

            {/* Phone */}
            {personal_info?.phone && (
              <div
                ref={(el) => {
                  fieldRefs.current["phone"] = el;
                  fieldRefs.current["personal_info.phone"] = el;
                }}
                tabIndex={-1}
                className={`transition-colors rounded ${
                  focusedField?.includes("phone") ? "bg-amber-100/60 p-0.5" : ""
                }`}
              >
                <ProvenanceTooltip evidence={phoneEvidence} fieldName="Phone">
                  <a
                    href={`tel:${personal_info.phone}`}
                    className="inline-flex items-center gap-1.5 hover:text-[#055B65] transition-colors"
                  >
                    <Phone className="w-3.5 h-3.5 text-[#45828B]" />
                    <span className="font-mono text-[11px] tabular-nums text-slate-700">{personal_info.phone}</span>
                  </a>
                </ProvenanceTooltip>
              </div>
            )}

            {/* Location */}
            {personal_info?.location && (
              <div
                ref={(el) => {
                  fieldRefs.current["location"] = el;
                  fieldRefs.current["personal_info.location"] = el;
                }}
                tabIndex={-1}
                className={`transition-colors rounded ${
                  focusedField?.includes("location") ? "bg-amber-100/60 p-0.5" : ""
                }`}
              >
                <ProvenanceTooltip evidence={locationEvidence} fieldName="Location">
                  <div className="inline-flex items-center gap-1.5">
                    <MapPin className="w-3.5 h-3.5 text-[#45828B]" />
                    <span className="text-slate-700">{personal_info.location}</span>
                  </div>
                </ProvenanceTooltip>
              </div>
            )}

            {/* LinkedIn */}
            {personal_info?.linkedin && (
              <div
                ref={(el) => {
                  fieldRefs.current["linkedin"] = el;
                  fieldRefs.current["personal_info.linkedin"] = el;
                }}
              >
                <ProvenanceTooltip evidence={linkedinEvidence} fieldName="LinkedIn">
                  <a
                    href={
                      personal_info.linkedin.startsWith("http")
                        ? personal_info.linkedin
                        : `https://${personal_info.linkedin}`
                    }
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 font-semibold text-[#055B65] hover:text-[#033c43] transition-colors"
                  >
                    <span>LinkedIn</span>
                    <ExternalLink className="w-2.5 h-2.5" />
                  </a>
                </ProvenanceTooltip>
              </div>
            )}

            {/* GitHub */}
            {personal_info?.github && (
              <div
                ref={(el) => {
                  fieldRefs.current["github"] = el;
                  fieldRefs.current["personal_info.github"] = el;
                }}
              >
                <ProvenanceTooltip evidence={githubEvidence} fieldName="GitHub">
                  <a
                    href={
                      personal_info.github.startsWith("http")
                        ? personal_info.github
                        : `https://${personal_info.github}`
                    }
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 font-semibold text-[#055B65] hover:text-[#033c43] transition-colors"
                  >
                    <FolderGit2 className="w-3 h-3 text-[#055B65]" />
                    <span>GitHub</span>
                    <ExternalLink className="w-2.5 h-2.5" />
                  </a>
                </ProvenanceTooltip>
              </div>
            )}
          </div>
        </div>

        {/* 2-Column Work Area */}
        <div className="p-6 sm:p-8 grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Main Column */}
          <div className="lg:col-span-8 space-y-8">
            {/* Professional Summary */}
            <section
              ref={(el) => {
                fieldRefs.current["professional_summary"] = el;
                fieldRefs.current["summary"] = el;
              }}
              tabIndex={-1}
              className={`space-y-2 transition-colors rounded ${
                focusedField === "professional_summary" || focusedField === "summary"
                  ? "bg-amber-50/60 p-2 ring-2 ring-inset ring-amber-300"
                  : ""
              }`}
            >
              <div className="flex items-center justify-between">
                <h2 className="text-xs font-semibold uppercase tracking-wider text-[#055B65]">
                  Professional Summary
                </h2>
              </div>

              {professional_summary ? (
                <ProvenanceTooltip evidence={summaryEvidence} fieldName="Summary">
                  <p className="text-sm text-slate-700 leading-relaxed">
                    {professional_summary}
                  </p>
                </ProvenanceTooltip>
              ) : (
                <p className="text-xs text-[#45828B] italic">
                  No professional summary detected in document.
                </p>
              )}
            </section>

            {/* Work History */}
            <section
              ref={(el) => {
                fieldRefs.current["experience"] = el;
              }}
              tabIndex={-1}
              className={`space-y-4 transition-colors rounded ${
                focusedField === "experience"
                  ? "bg-amber-50/60 p-2 ring-2 ring-inset ring-amber-300"
                  : ""
              }`}
            >
              <div className="flex items-center justify-between pb-2 border-b border-[#E0E5E9]">
                <h2 className="text-sm font-semibold text-[#055B65]">
                  Work History
                </h2>
                <span className="text-xs text-[#45828B] tabular-nums font-mono">
                  {experience?.length || 0} {experience?.length === 1 ? "role" : "roles"}
                </span>
              </div>

              {experience && experience.length > 0 ? (
                <ExperienceTimeline experience={experience} evidence={evidence} />
              ) : (
                <p className="text-xs text-[#45828B] italic">
                  No employment records extracted.
                </p>
              )}
            </section>

            {/* Education */}
            <section
              ref={(el) => {
                fieldRefs.current["education"] = el;
              }}
              tabIndex={-1}
              className={`space-y-4 transition-colors rounded ${
                focusedField === "education"
                  ? "bg-amber-50/60 p-2 ring-2 ring-inset ring-amber-300"
                  : ""
              }`}
            >
              <div className="flex items-center justify-between pb-2 border-b border-[#E0E5E9]">
                <h2 className="text-sm font-semibold text-[#055B65]">
                  Education
                </h2>
                <span className="text-xs text-[#45828B] tabular-nums font-mono">
                  {education?.length || 0}
                </span>
              </div>

              {education && education.length > 0 ? (
                <div className="grid gap-3 sm:grid-cols-2">
                  {education.map((edu, i) => {
                    const eduEvidence =
                      evidence?.[`education[${i}].institution`] ||
                      evidence?.[`education[${i}].degree`] ||
                      evidence?.["education"];

                    return (
                      <div
                        key={i}
                        className="rounded-lg border border-[#E0E5E9] p-3.5 space-y-1 bg-[#FBFCFC]"
                      >
                        <div className="flex items-start justify-between gap-2">
                          <ProvenanceTooltip
                            evidence={eduEvidence}
                            fieldName={edu.degree || "Degree"}
                          >
                            <h3 className="text-xs font-semibold text-slate-900">
                              {edu.degree || "Degree"}
                            </h3>
                          </ProvenanceTooltip>

                          {edu.graduation_year && (
                            <span className="text-xs text-[#45828B] tabular-nums font-mono shrink-0">
                              {edu.graduation_year}
                            </span>
                          )}
                        </div>

                        {edu.field_of_study && (
                          <p className="text-xs text-[#055B65] font-semibold">
                            {edu.field_of_study}
                          </p>
                        )}

                        {edu.institution && (
                          <p className="text-xs text-slate-600">
                            {edu.institution}
                          </p>
                        )}
                      </div>
                    );
                  })}
                </div>
              ) : (
                <p className="text-xs text-[#45828B] italic">
                  No education records extracted.
                </p>
              )}
            </section>

            {/* Key Projects */}
            {projects && projects.length > 0 && (
              <section className="space-y-4">
                <div className="flex items-center justify-between pb-2 border-b border-[#E0E5E9]">
                  <h2 className="text-sm font-semibold text-[#055B65]">
                    Key Projects
                  </h2>
                  <span className="text-xs text-[#45828B] tabular-nums font-mono">
                    {projects.length}
                  </span>
                </div>

                <div className="space-y-3">
                  {projects.map((proj, i) => (
                    <div
                      key={i}
                      className="rounded-lg border border-[#E0E5E9] p-3.5 space-y-1.5 bg-[#FBFCFC]"
                    >
                      <h3 className="text-xs font-semibold text-[#055B65]">
                        {proj.name}
                      </h3>
                      {proj.description && (
                        <p className="text-xs text-slate-600 leading-relaxed">
                          {proj.description}
                        </p>
                      )}
                      {proj.technologies && proj.technologies.length > 0 && (
                        <div className="flex flex-wrap gap-1 pt-1">
                          {proj.technologies.map((tech, tidx) => (
                            <span
                              key={tidx}
                              className="px-1.5 py-0.2 rounded text-[10px] font-mono bg-[#E0E5E9]/50 text-[#055B65] border border-[#B2C9C5]/40"
                            >
                              {tech}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </section>
            )}
          </div>

          {/* Sidebar Column */}
          <div className="lg:col-span-4 space-y-6">
            {/* Categorized Skills */}
            <section
              ref={(el) => {
                fieldRefs.current["skills"] = el;
              }}
              tabIndex={-1}
              className={`space-y-3 transition-colors rounded ${
                focusedField === "skills"
                  ? "bg-amber-50/60 p-2 ring-2 ring-inset ring-amber-300"
                  : ""
              }`}
            >
              <div className="flex items-center justify-between pb-2 border-b border-[#E0E5E9]">
                <h2 className="text-sm font-semibold text-[#055B65]">
                  Skills Taxonomy
                </h2>
                <span className="text-xs text-[#45828B] tabular-nums font-mono">
                  {skills?.length || 0}
                </span>
              </div>

              <SkillBadges skills={skills || []} evidence={evidence} />
            </section>

            {/* Certifications */}
            {certifications && certifications.length > 0 && (
              <section className="space-y-3 pt-4 border-t border-[#E0E5E9]">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-semibold uppercase tracking-wider text-[#055B65] flex items-center gap-1.5">
                    <Award className="w-3.5 h-3.5 text-[#055B65]" />
                    <span>Certifications</span>
                  </h3>
                  <span className="text-xs text-[#45828B] tabular-nums font-mono">
                    {certifications.length}
                  </span>
                </div>

                <ul className="space-y-2 text-xs divide-y divide-[#E0E5E9]">
                  {certifications.map((cert, i) => (
                    <li key={i} className="pt-2 first:pt-0">
                      <p className="font-semibold text-slate-800">{cert.name}</p>
                      <div className="flex justify-between text-[#45828B] text-[11px] mt-0.5">
                        <span>{cert.issuer || "Verified Issuer"}</span>
                        {cert.date && <span className="tabular-nums font-mono">{cert.date}</span>}
                      </div>
                    </li>
                  ))}
                </ul>
              </section>
            )}

            {/* Languages */}
            {languages && languages.length > 0 && (
              <section className="space-y-3 pt-4 border-t border-[#E0E5E9]">
                <h3 className="text-xs font-semibold uppercase tracking-wider text-[#055B65] flex items-center gap-1.5">
                  <Globe className="w-3.5 h-3.5 text-[#055B65]" />
                  <span>Languages</span>
                </h3>

                <div className="flex flex-wrap gap-1.5">
                  {languages.map((lang, i) => (
                    <span
                      key={i}
                      className="px-2 py-0.5 rounded text-xs bg-[#E0E5E9]/50 text-[#055B65] border border-[#B2C9C5]/40"
                    >
                      {lang}
                    </span>
                  ))}
                </div>
              </section>
            )}

            {/* Document Details Card */}
            <div className="rounded-lg bg-[#FBFCFC] p-3.5 border border-[#E0E5E9] space-y-2 text-xs text-[#45828B]">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-[#055B65] block">
                Document Details
              </span>
              <div className="space-y-1 text-[11px]">
                <div className="flex justify-between">
                  <span className="text-[#45828B]">Filename:</span>
                  <span className="font-mono text-slate-700 truncate max-w-[140px]">
                    {filename || "Uploaded file"}
                  </span>
                </div>
                {evidence && (
                  <div className="flex justify-between">
                    <span className="text-[#45828B]">Tracked fields:</span>
                    <span className="font-mono text-[#055B65] font-semibold">
                      {Object.keys(evidence).length}
                    </span>
                  </div>
                )}
                {confidence_score !== null && confidence_score !== undefined && (
                  <div className="flex justify-between">
                    <span className="text-[#45828B]">Confidence index:</span>
                    <span className="font-mono text-[#055B65] font-semibold">
                      {(confidence_score * 100).toFixed(0)}%
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Raw Extracted Text Stream */}
            {raw_text && (
              <div className="pt-2">
                <button
                  type="button"
                  onClick={() => setShowRawText(!showRawText)}
                  className="w-full flex items-center justify-between text-xs font-semibold text-[#055B65] hover:text-[#033c43] py-1.5 cursor-pointer min-h-[36px]"
                >
                  <span className="flex items-center gap-1.5">
                    <FileText className="w-3.5 h-3.5 text-[#055B65]" />
                    <span>Raw extracted document text</span>
                  </span>
                  {showRawText ? (
                    <ChevronUp className="w-3.5 h-3.5 text-[#055B65]" />
                  ) : (
                    <ChevronDown className="w-3.5 h-3.5 text-[#055B65]" />
                  )}
                </button>

                {showRawText && (
                  <div className="mt-2">
                    <pre className="p-3 rounded-lg bg-[#033c43] text-[#FBFCFC] text-[11px] font-mono overflow-x-auto whitespace-pre-wrap max-h-72 leading-relaxed border border-[#055B65]">
                      {raw_text}
                    </pre>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
