"use client";

import { UploadZone } from "@/components/upload-zone";
import {
  FileCheck2,
  ShieldCheck,
  Cpu,
  Info,
} from "lucide-react";

export default function UploadPage() {
  return (
    <main className="py-8 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="space-y-1 pb-4 border-b border-[#E0E5E9]">
        <h1 className="text-2xl font-bold text-[#055B65] tracking-tight">
          Upload Resume
        </h1>
        <p className="text-xs sm:text-sm text-[#45828B]">
          Upload resumes in PDF, Word, or image formats for automatic structured data extraction and provenance verification.
        </p>
      </div>

      {/* Workflow Step Indicator (Goal-Gradient Effect) */}
      <nav aria-label="Parsing workflow steps">
        <ol className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <li className="flex items-center gap-3 p-3 rounded-lg border border-[#055B65]/30 bg-[#055B65]/5 shadow-2xs" aria-current="step">
            <span className="flex items-center justify-center w-6 h-6 rounded-full bg-[#055B65] text-[#1BD488] text-xs font-bold shrink-0">
              1
            </span>
            <div className="min-w-0">
              <p className="text-xs font-semibold text-[#055B65] truncate">Select Resume</p>
              <p className="text-[11px] text-[#45828B] truncate">PDF, DOCX, or Image</p>
            </div>
          </li>
          <li className="flex items-center gap-3 p-3 rounded-lg border border-[#E0E5E9] bg-white">
            <span className="flex items-center justify-center w-6 h-6 rounded-full bg-[#E0E5E9] text-[#45828B] text-xs font-semibold shrink-0">
              2
            </span>
            <div className="min-w-0">
              <p className="text-xs font-semibold text-slate-700 truncate">NLP Extraction</p>
              <p className="text-[11px] text-[#45828B] truncate">DistilBERT & NER</p>
            </div>
          </li>
          <li className="flex items-center gap-3 p-3 rounded-lg border border-[#E0E5E9] bg-white">
            <span className="flex items-center justify-center w-6 h-6 rounded-full bg-[#E0E5E9] text-[#45828B] text-xs font-semibold shrink-0">
              3
            </span>
            <div className="min-w-0">
              <p className="text-xs font-semibold text-slate-700 truncate">Review & Audit</p>
              <p className="text-[11px] text-[#45828B] truncate">Confidence & Provenance</p>
            </div>
          </li>
        </ol>
      </nav>

      {/* Main Upload Zone */}
      <div className="bg-white rounded-xl border border-[#E0E5E9] p-6 sm:p-8 shadow-2xs">
        <UploadZone />
      </div>

      {/* Parsing Guarantees & Guidelines */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="rounded-xl border border-[#E0E5E9] bg-white p-4 space-y-2">
          <div className="flex items-center gap-2 text-[#055B65]">
            <FileCheck2 className="w-4 h-4 text-[#055B65]" />
            <h2 className="text-xs font-semibold text-[#055B65]">
              Format Support
            </h2>
          </div>
          <p className="text-xs text-[#45828B] leading-relaxed">
            Native support for PDF and DOCX documents. Scanned resumes and images automatically run through Tesseract OCR.
          </p>
        </div>

        <div className="rounded-xl border border-[#E0E5E9] bg-white p-4 space-y-2">
          <div className="flex items-center gap-2 text-[#055B65]">
            <Cpu className="w-4 h-4 text-[#055B65]" />
            <h2 className="text-xs font-semibold text-[#055B65]">
              Entity Extraction
            </h2>
          </div>
          <p className="text-xs text-[#45828B] leading-relaxed">
            Fine-tuned DistilBERT models extract candidate names, job titles, companies, skills, and chronological timelines.
          </p>
        </div>

        <div className="rounded-xl border border-[#E0E5E9] bg-white p-4 space-y-2">
          <div className="flex items-center gap-2 text-[#055B65]">
            <ShieldCheck className="w-4 h-4 text-[#055B65]" />
            <h2 className="text-xs font-semibold text-[#055B65]">
              Source Provenance
            </h2>
          </div>
          <p className="text-xs text-[#45828B] leading-relaxed">
            Every extracted entity is verified with source text excerpts, section origins, page numbers, and confidence metrics.
          </p>
        </div>
      </div>

      {/* Document Tips */}
      <div className="rounded-lg bg-[#055B65]/5 border border-[#B2C9C5]/50 p-4 flex items-start gap-3 text-xs text-[#055B65]">
        <Info className="w-4 h-4 text-[#45828B] shrink-0 mt-0.5" />
        <div className="space-y-1">
          <p className="font-semibold text-[#055B65]">
            Recommendations for optimal extraction accuracy:
          </p>
          <ul className="list-disc pl-4 space-y-0.5 text-slate-600">
            <li>Standard section headers (e.g., &quot;Experience&quot;, &quot;Education&quot;, &quot;Skills&quot;) improve section categorization.</li>
            <li>Digital text-based PDFs produce higher confidence than photographed paper resumes.</li>
            <li>Files must not exceed 10 MB in size.</li>
          </ul>
        </div>
      </div>
    </main>
  );
}
