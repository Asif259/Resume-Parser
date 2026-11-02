"use client";

import { useEffect, useState, useMemo } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { listResumes } from "@/lib/api";
import { ParseResponse } from "@/types/resume";
import { UploadZone } from "@/components/upload-zone";
import { ConfidenceBadge } from "@/components/confidence-badge";
import {
  UploadCloud,
  FileText,
  CheckCircle2,
  AlertTriangle,
  Search,
  ArrowRight,
  Download,
  Cpu,
  Layers,
  BookOpen,
  ShieldCheck,
  Clock,
  X,
} from "lucide-react";

export default function DashboardPage() {
  const router = useRouter();
  const [resumes, setResumes] = useState<ParseResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    let mounted = true;
    listResumes(0, 100)
      .then((data) => {
        if (mounted) {
          setResumes(data || []);
          setLoading(false);
        }
      })
      .catch(() => {
        if (mounted) {
          setResumes([]);
          setLoading(false);
        }
      });

    return () => {
      mounted = false;
    };
  }, []);

  // Compute statistics from actual backend records
  const stats = useMemo(() => {
    const total = resumes.length;
    if (total === 0) {
      return { total: 0, highConfidencePct: 0, avgSkills: 0, needsReviewCount: 0 };
    }

    let highConfidenceCount = 0;
    let needsReviewCount = 0;
    let totalSkills = 0;

    resumes.forEach((r) => {
      const score = r.parsed_resume?.confidence_score;
      if (score !== undefined && score !== null) {
        if (score >= 0.8) highConfidenceCount++;
        if (score < 0.6) needsReviewCount++;
      } else if (
        r.parsed_resume?.low_confidence_fields &&
        r.parsed_resume.low_confidence_fields.length > 0
      ) {
        needsReviewCount++;
      }
      totalSkills += r.parsed_resume?.skills?.length || 0;
    });

    return {
      total,
      highConfidencePct: Math.round((highConfidenceCount / total) * 100),
      avgSkills: Math.round(totalSkills / total),
      needsReviewCount,
    };
  }, [resumes]);

  // Filtered recent resumes
  const filteredResumes = useMemo(() => {
    if (!searchQuery.trim()) return resumes.slice(0, 8);
    const q = searchQuery.toLowerCase().trim();
    return resumes
      .filter((r) => {
        const name = r.parsed_resume?.personal_info?.name?.toLowerCase() || "";
        const email = r.parsed_resume?.personal_info?.email?.toLowerCase() || "";
        const filename = r.filename?.toLowerCase() || "";
        const skills = (r.parsed_resume?.skills || []).map((s) => s.toLowerCase());
        return (
          name.includes(q) ||
          email.includes(q) ||
          filename.includes(q) ||
          skills.some((s) => s.includes(q))
        );
      })
      .slice(0, 8);
  }, [resumes, searchQuery]);

  const formatDate = (dateStr: string): string => {
    try {
      const date = new Date(dateStr);
      return new Intl.DateTimeFormat("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
      }).format(date);
    } catch {
      return dateStr;
    }
  };

  const downloadJSON = (resume: ParseResponse, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    const jsonStr = JSON.stringify(resume.parsed_resume, null, 2);
    const blob = new Blob([jsonStr], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    const safeName = (resume.parsed_resume?.personal_info?.name || "resume")
      .toLowerCase()
      .replace(/[^a-z0-9]/g, "_");
    a.download = `${safeName}_parsed.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <main className="py-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-8">
      {/* Section 1: Welcome Hero Card (Sequence Style: Enamelled Jewel with Retro Lime) */}
      <section className="rounded-2xl bg-[#055B65] text-white p-6 sm:p-8 shadow-sm border border-[#044b53] relative overflow-hidden">
        {/* Subtle decorative radial gradient glow */}
        <div
          className="absolute -right-24 -top-24 w-96 h-96 rounded-full bg-[#1BD488]/10 blur-3xl pointer-events-none"
          aria-hidden="true"
        />
        <div
          className="absolute right-48 -bottom-32 w-64 h-64 rounded-full bg-[#45828B]/20 blur-2xl pointer-events-none"
          aria-hidden="true"
        />

        <div className="relative z-10 flex flex-col sm:flex-row sm:items-center justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <div className="flex items-center gap-2">
              <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-[#1BD488]/20 text-[#1BD488] border border-[#1BD488]/30">
                <span className="w-1.5 h-1.5 rounded-full bg-[#1BD488] animate-pulse" />
                <span>Production NLP Pipeline</span>
              </span>
              <span className="text-xs text-[#B2C9C5] font-mono hidden sm:inline">
                DistilBERT • Sentence-Transformers • OCR
              </span>
            </div>

            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">
              Resume Intelligence Dashboard
            </h1>
            <p className="text-xs sm:text-sm text-[#B2C9C5] leading-relaxed">
              Extract, verify, and explore candidate records with verbatim source provenance, calibrated confidence scoring, and structured semantic skill normalization.
            </p>
          </div>

          <div className="flex flex-wrap sm:flex-col lg:flex-row items-stretch sm:items-end gap-3 shrink-0">
            <Link
              href="/upload"
              className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-[#1BD488] hover:bg-[#16bc78] text-[#033c43] text-xs font-bold tracking-wide uppercase transition-all shadow-sm cursor-pointer min-h-[40px]"
            >
              <UploadCloud className="w-4 h-4 text-[#033c43]" />
              <span>Upload Resume</span>
            </Link>

            <Link
              href="/resumes"
              className="inline-flex items-center justify-center gap-1.5 px-4 py-2.5 rounded-lg bg-white/10 hover:bg-white/15 text-white text-xs font-semibold transition-colors border border-white/15 cursor-pointer min-h-[40px]"
            >
              <span>Explore Library</span>
              <ArrowRight className="w-3.5 h-3.5 text-[#B2C9C5]" />
            </Link>
          </div>
        </div>
      </section>

      {/* Section 2: Statistics Cards */}
      <section aria-label="System Metrics" className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Parsed */}
        <div className="rounded-xl border border-[#E0E5E9] bg-white p-5 space-y-2 hover:border-[#B2C9C5] transition-colors shadow-2xs">
          <div className="flex items-center justify-between text-[#45828B] text-xs font-medium">
            <span>Total Resumes Parsed</span>
            <div className="p-1.5 rounded-lg bg-[#055B65]/10 text-[#055B65]">
              <FileText className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-[#055B65] tabular-nums">
            {loading ? "—" : stats.total}
          </div>
          <p className="text-[11px] text-[#45828B]">
            Stored in local document repository
          </p>
        </div>

        {/* High Confidence Rate */}
        <div className="rounded-xl border border-[#E0E5E9] bg-white p-5 space-y-2 hover:border-[#B2C9C5] transition-colors shadow-2xs">
          <div className="flex items-center justify-between text-[#45828B] text-xs font-medium">
            <span>High Confidence Rate</span>
            <div className="p-1.5 rounded-lg bg-[#1BD488]/15 text-[#055B65]">
              <CheckCircle2 className="w-4 h-4 text-[#055B65]" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-[#055B65] tabular-nums">
              {loading ? "—" : `${stats.highConfidencePct}%`}
            </span>
            <span className="inline-flex items-center px-1.5 py-0.2 rounded text-[10px] font-semibold bg-[#1BD488]/20 text-[#033c43]">
              Target ≥ 80%
            </span>
          </div>
          <p className="text-[11px] text-[#45828B]">
            Verified candidate documents
          </p>
        </div>

        {/* Average Skills Extracted */}
        <div className="rounded-xl border border-[#E0E5E9] bg-white p-5 space-y-2 hover:border-[#B2C9C5] transition-colors shadow-2xs">
          <div className="flex items-center justify-between text-[#45828B] text-xs font-medium">
            <span>Avg. Skills Extracted</span>
            <div className="p-1.5 rounded-lg bg-[#055B65]/10 text-[#055B65]">
              <Layers className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-[#055B65] tabular-nums">
            {loading ? "—" : stats.avgSkills}
          </div>
          <p className="text-[11px] text-[#45828B]">
            Across technical & domain categories
          </p>
        </div>

        {/* Resumes Requiring Review */}
        <div className="rounded-xl border border-[#E0E5E9] bg-white p-5 space-y-2 hover:border-[#B2C9C5] transition-colors shadow-2xs">
          <div className="flex items-center justify-between text-[#45828B] text-xs font-medium">
            <span>Requires Review</span>
            <div className="p-1.5 rounded-lg bg-amber-50 text-amber-700 border border-amber-200">
              <AlertTriangle className="w-4 h-4 text-amber-700" />
            </div>
          </div>
          <div className="text-2xl font-bold text-[#055B65] tabular-nums">
            {loading ? "—" : stats.needsReviewCount}
          </div>
          <p className="text-[11px] text-[#45828B]">
            Documents with flagged fields
          </p>
        </div>
      </section>

      {/* 2-Column Section: Upload Quick Action & AI Pipeline */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Section 3: Resume Upload Quick Action */}
        <div className="lg:col-span-5 space-y-3">
          <div className="flex items-center justify-between pb-1">
            <h2 className="text-sm font-semibold text-[#055B65]">
              Quick Document Upload
            </h2>
            <span className="text-[11px] text-[#45828B]">PDF, DOCX, Images</span>
          </div>
          <UploadZone />
        </div>

        {/* Section 5: AI Processing Overview */}
        <div className="lg:col-span-7 space-y-3">
          <div className="flex items-center justify-between pb-1">
            <h2 className="text-sm font-semibold text-[#055B65]">
              NLP Architecture & Pipeline
            </h2>
            <Link
              href="/settings"
              className="text-xs text-[#055B65] hover:text-[#033c43] font-semibold"
            >
              View System Specs →
            </Link>
          </div>

          <div className="rounded-xl border border-[#E0E5E9] bg-white p-5 space-y-4 shadow-2xs">
            <p className="text-xs text-slate-600 leading-relaxed">
              Resumes are parsed using a multi-stage hybrid extraction pipeline combining pre-trained transformer embeddings, custom entity recognizers, and rule-based heuristics.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
              <div className="p-3 rounded-lg border border-[#E0E5E9] bg-[#FBFCFC] space-y-1">
                <div className="flex items-center gap-1.5 text-xs font-semibold text-[#055B65]">
                  <Cpu className="w-3.5 h-3.5 text-[#055B65]" />
                  <span>Custom DistilBERT NER</span>
                </div>
                <p className="text-[11px] text-[#45828B] leading-normal">
                  Identifies candidate names, job titles, and employers with calibrated token classification.
                </p>
              </div>

              <div className="p-3 rounded-lg border border-[#E0E5E9] bg-[#FBFCFC] space-y-1">
                <div className="flex items-center gap-1.5 text-xs font-semibold text-[#055B65]">
                  <Layers className="w-3.5 h-3.5 text-[#055B65]" />
                  <span>Semantic Skill Embeddings</span>
                </div>
                <p className="text-[11px] text-[#45828B] leading-normal">
                  Uses Sentence-Transformers to map variations to normalized skill taxonomies.
                </p>
              </div>

              <div className="p-3 rounded-lg border border-[#E0E5E9] bg-[#FBFCFC] space-y-1">
                <div className="flex items-center gap-1.5 text-xs font-semibold text-[#055B65]">
                  <BookOpen className="w-3.5 h-3.5 text-[#055B65]" />
                  <span>Rule & Heuristic Engine</span>
                </div>
                <p className="text-[11px] text-[#45828B] leading-normal">
                  Extracts structured contact info (email, phone, URLs), dates, and section boundaries.
                </p>
              </div>

              <div className="p-3 rounded-lg border border-[#E0E5E9] bg-[#FBFCFC] space-y-1">
                <div className="flex items-center gap-1.5 text-xs font-semibold text-[#055B65]">
                  <ShieldCheck className="w-3.5 h-3.5 text-[#055B65]" />
                  <span>Provenance Verification</span>
                </div>
                <p className="text-[11px] text-[#45828B] leading-normal">
                  Tracks source section, page offset, and verbatim text matches for every extracted field.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Section 4: Recently Parsed Resumes */}
      <section className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <h2 className="text-base font-semibold text-[#055B65]">
              Recently Parsed Candidates
            </h2>
            <span className="text-xs text-[#45828B] tabular-nums font-mono">
              ({resumes.length})
            </span>
          </div>

          <div className="flex items-center gap-3">
            <div className="relative w-full sm:w-60">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
              <input
                type="text"
                placeholder="Search candidates, skills..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                aria-label="Filter recent candidates"
                className="w-full pl-8 pr-7 py-1.5 text-xs rounded-lg border border-[#E0E5E9] bg-white placeholder:text-slate-400 focus:outline-none focus:ring-1 focus:ring-[#055B65] focus:border-[#055B65]"
              />
              {searchQuery && (
                <button
                  type="button"
                  onClick={() => setSearchQuery("")}
                  className="absolute right-2 top-1/2 -translate-y-1/2 p-0.5 rounded text-slate-400 hover:text-slate-600"
                  aria-label="Clear recent candidates search"
                >
                  <X className="w-3 h-3" />
                </button>
              )}
            </div>

            <Link
              href="/resumes"
              className="text-xs font-semibold text-[#055B65] hover:text-[#033c43] whitespace-nowrap min-h-[32px] inline-flex items-center"
            >
              View all →
            </Link>
          </div>
        </div>

        {/* Resumes Data Table */}
        <div className="rounded-xl border border-[#E0E5E9] bg-white overflow-hidden shadow-2xs">
          {loading ? (
            <div className="p-8 text-center text-[#45828B] text-xs animate-pulse">
              Loading recent candidates...
            </div>
          ) : filteredResumes.length === 0 ? (
            <div className="p-10 text-center space-y-3">
              <FileText className="w-8 h-8 text-[#B2C9C5] mx-auto" />
              <p className="text-sm font-medium text-slate-700">No resumes found</p>
              <p className="text-xs text-[#45828B] max-w-sm mx-auto">
                {searchQuery
                  ? `No parsed candidates matching "${searchQuery}".`
                  : "Upload your first resume above to begin extracting candidate data."}
              </p>
              {searchQuery ? (
                <button
                  type="button"
                  onClick={() => setSearchQuery("")}
                  className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-[#E0E5E9]/50 hover:bg-[#E0E5E9] text-[#055B65] text-xs font-medium cursor-pointer"
                >
                  <X className="w-3.5 h-3.5" />
                  <span>Clear search</span>
                </button>
              ) : (
                <Link
                  href="/upload"
                  className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-[#055B65] hover:bg-[#033c43] text-white text-xs font-medium"
                >
                  <UploadCloud className="w-3.5 h-3.5 text-[#1BD488]" />
                  <span>Upload Resume</span>
                </Link>
              )}
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs divide-y divide-[#E0E5E9]">
                <thead className="bg-[#FBFCFC] text-[#45828B] font-semibold uppercase tracking-wider text-[11px] border-b border-[#E0E5E9]">
                  <tr>
                    <th scope="col" className="py-3 px-4">Candidate</th>
                    <th scope="col" className="py-3 px-4">Email</th>
                    <th scope="col" className="py-3 px-4">Primary Skills</th>
                    <th scope="col" className="py-3 px-4">Upload Date</th>
                    <th scope="col" className="py-3 px-4">Confidence</th>
                    <th scope="col" className="py-3 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#E0E5E9]">
                  {filteredResumes.map((item) => {
                    const candidateName =
                      item.parsed_resume?.personal_info?.name || "Unnamed Candidate";
                    const email = item.parsed_resume?.personal_info?.email;
                    const skills = item.parsed_resume?.skills || [];
                    const topSkills = skills.slice(0, 3);
                    const remainingSkillsCount = skills.length - 3;
                    const confidence = item.parsed_resume?.confidence_score;

                    return (
                      <tr
                        key={item.id}
                        className="hover:bg-[#055B65]/5 transition-colors group cursor-pointer"
                        onClick={() => {
                          router.push(`/resumes/${item.id}`);
                        }}
                      >
                        {/* Candidate Name & File */}
                        <td className="py-3 px-4 min-w-[180px]">
                          <Link
                            href={`/resumes/${item.id}`}
                            onClick={(e) => e.stopPropagation()}
                            className="font-semibold text-slate-900 group-hover:text-[#055B65] transition-colors hover:underline block"
                          >
                            {candidateName}
                          </Link>
                          <div className="text-[11px] text-[#45828B] font-mono truncate max-w-[160px]">
                            {item.filename}
                          </div>
                        </td>

                        {/* Email */}
                        <td className="py-3 px-4 text-slate-600 font-mono min-w-[140px]">
                          {email || <span className="text-slate-400 italic">None</span>}
                        </td>

                        {/* Primary Skills */}
                        <td className="py-3 px-4 min-w-[200px]">
                          <div className="flex flex-wrap items-center gap-1">
                            {topSkills.map((s, idx) => (
                              <span
                                key={idx}
                                className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-[#E0E5E9]/50 text-[#055B65] border border-[#B2C9C5]/40"
                              >
                                {s}
                              </span>
                            ))}
                            {remainingSkillsCount > 0 && (
                              <span className="text-[10px] text-[#45828B] font-mono">
                                +{remainingSkillsCount}
                              </span>
                            )}
                          </div>
                        </td>

                        {/* Upload Date */}
                        <td className="py-3 px-4 text-[#45828B] tabular-nums whitespace-nowrap">
                          {item.created_at ? (
                            <span className="inline-flex items-center gap-1">
                              <Clock className="w-3 h-3 text-[#45828B]" />
                              <span>{formatDate(item.created_at)}</span>
                            </span>
                          ) : (
                            "—"
                          )}
                        </td>

                        {/* Confidence Score */}
                        <td className="py-3 px-4 whitespace-nowrap">
                          <ConfidenceBadge score={confidence} size="sm" />
                        </td>

                        {/* Actions with touch target compliance */}
                        <td className="py-3 px-4 text-right whitespace-nowrap">
                          <div className="inline-flex items-center gap-1">
                            <button
                              type="button"
                              onClick={(e) => downloadJSON(item, e)}
                              className="p-2 min-h-[36px] min-w-[36px] flex items-center justify-center rounded-lg text-[#45828B] hover:text-[#055B65] hover:bg-[#E0E5E9]/50 cursor-pointer"
                              title="Download parsed JSON"
                              aria-label={`Download JSON for ${candidateName}`}
                            >
                              <Download className="w-3.5 h-3.5" />
                            </button>
                            <Link
                              href={`/resumes/${item.id}`}
                              onClick={(e) => e.stopPropagation()}
                              className="inline-flex items-center gap-1 px-2.5 py-1.5 min-h-[36px] text-xs font-semibold text-[#055B65] hover:text-[#033c43] rounded-lg hover:bg-[#055B65]/10"
                            >
                              <span>View</span>
                              <ArrowRight className="w-3.5 h-3.5" />
                            </Link>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </section>
    </main>
  );
}
