"use client";

import { useEffect, useState, useMemo } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { listResumes } from "@/lib/api";
import { ParseResponse } from "@/types/resume";
import { ConfidenceBadge } from "@/components/confidence-badge";
import {
  Search,
  ArrowRight,
  Download,
  Filter,
  FileText,
  Clock,
  RotateCcw,
  AlertCircle,
  ChevronLeft,
  ChevronRight,
  UploadCloud,
  X,
} from "lucide-react";

type ConfidenceFilter = "all" | "high" | "review";
type SortOption = "date_desc" | "confidence_desc" | "skills_desc";

const ITEMS_PER_PAGE = 10;

export function ResumesLibraryContent() {
  const router = useRouter();
  const [resumes, setResumes] = useState<ParseResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  const [searchQuery, setSearchQuery] = useState("");
  const [confidenceFilter, setConfidenceFilter] = useState<ConfidenceFilter>("all");
  const [sortBy, setSortBy] = useState<SortOption>("date_desc");
  const [currentPage, setCurrentPage] = useState(1);

  useEffect(() => {
    let isMounted = true;
    listResumes(0, 200)
      .then((data) => {
        if (isMounted) {
          setResumes(data || []);
          setLoading(false);
          setError(null);
        }
      })
      .catch((err) => {
        if (isMounted) {
          setError(err.message || "Failed to load parsed resumes.");
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [reloadKey]);

  const handleRetry = () => {
    setLoading(true);
    setError(null);
    setReloadKey((prev) => prev + 1);
  };

  const handleClearFilters = () => {
    setSearchQuery("");
    setConfidenceFilter("all");
    setSortBy("date_desc");
    setCurrentPage(1);
  };

  // Filter and sort resumes
  const processedResumes = useMemo(() => {
    return resumes
      .filter((r) => {
        // Search filter
        if (searchQuery.trim()) {
          const q = searchQuery.toLowerCase().trim();
          const name = r.parsed_resume?.personal_info?.name?.toLowerCase() || "";
          const email = r.parsed_resume?.personal_info?.email?.toLowerCase() || "";
          const filename = r.filename?.toLowerCase() || "";
          const skills = (r.parsed_resume?.skills || []).map((s) => s.toLowerCase());

          const matches =
            name.includes(q) ||
            email.includes(q) ||
            filename.includes(q) ||
            skills.some((s) => s.includes(q));

          if (!matches) return false;
        }

        // Confidence filter
        const score = r.parsed_resume?.confidence_score ?? 0;
        if (confidenceFilter === "high" && score < 0.8) return false;
        if (confidenceFilter === "review" && score >= 0.6) {
          const lowFields = r.parsed_resume?.low_confidence_fields || [];
          if (lowFields.length === 0) return false;
        }

        return true;
      })
      .sort((a, b) => {
        if (sortBy === "confidence_desc") {
          return (
            (b.parsed_resume?.confidence_score ?? 0) -
            (a.parsed_resume?.confidence_score ?? 0)
          );
        }
        if (sortBy === "skills_desc") {
          return (
            (b.parsed_resume?.skills?.length ?? 0) -
            (a.parsed_resume?.skills?.length ?? 0)
          );
        }
        // Default: date_desc
        const dateA = new Date(a.created_at || 0).getTime();
        const dateB = new Date(b.created_at || 0).getTime();
        return dateB - dateA;
      });
  }, [resumes, searchQuery, confidenceFilter, sortBy]);

  // Client-side pagination
  const totalPages = Math.ceil(processedResumes.length / ITEMS_PER_PAGE) || 1;
  const paginatedResumes = useMemo(() => {
    const start = (currentPage - 1) * ITEMS_PER_PAGE;
    return processedResumes.slice(start, start + ITEMS_PER_PAGE);
  }, [processedResumes, currentPage]);

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
    <main className="py-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#E0E5E9]">
        <div>
          <h1 className="text-2xl font-bold text-[#055B65] tracking-tight">
            Resume Library
          </h1>
          <p className="text-xs sm:text-sm text-[#45828B] mt-1">
            Browse, search, and inspect all parsed candidate profiles in the database.
          </p>
        </div>

        <Link
          href="/upload"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-[#055B65] hover:bg-[#033c43] text-white text-xs font-semibold uppercase tracking-wider transition-colors shadow-2xs self-start sm:self-auto cursor-pointer min-h-[38px]"
        >
          <UploadCloud className="w-4 h-4 text-[#1BD488]" />
          <span>Upload Resume</span>
        </Link>
      </div>

      {/* Search and Filters Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 bg-white p-3.5 rounded-xl border border-[#E0E5E9] shadow-2xs">
        {/* Search Input with Clear Button */}
        <div className="relative flex-1 max-w-md">
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            type="text"
            placeholder="Search by name, email, skill, or filename..."
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setCurrentPage(1);
            }}
            aria-label="Search candidate profiles"
            className="w-full pl-9 pr-8 py-2 text-xs rounded-lg border border-[#E0E5E9] bg-[#FBFCFC] placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#055B65] focus:border-[#055B65]"
          />
          {searchQuery && (
            <button
              type="button"
              onClick={() => {
                setSearchQuery("");
                setCurrentPage(1);
              }}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 p-1 rounded text-slate-400 hover:text-slate-600"
              aria-label="Clear search input"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {/* Filters and Sorters */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Status Filter */}
          <div className="inline-flex rounded-lg border border-[#E0E5E9] p-0.5 bg-[#FBFCFC]" role="group" aria-label="Filter by extraction confidence">
            <button
              type="button"
              onClick={() => {
                setConfidenceFilter("all");
                setCurrentPage(1);
              }}
              className={`px-2.5 py-1.5 text-xs font-semibold rounded-md transition-colors cursor-pointer min-h-[32px] ${
                confidenceFilter === "all"
                  ? "bg-[#055B65] text-white shadow-2xs"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              All ({resumes.length})
            </button>
            <button
              type="button"
              onClick={() => {
                setConfidenceFilter("high");
                setCurrentPage(1);
              }}
              className={`px-2.5 py-1.5 text-xs font-semibold rounded-md transition-colors cursor-pointer min-h-[32px] ${
                confidenceFilter === "high"
                  ? "bg-[#1BD488] text-[#033c43] shadow-2xs font-bold"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              High (≥ 80%)
            </button>
            <button
              type="button"
              onClick={() => {
                setConfidenceFilter("review");
                setCurrentPage(1);
              }}
              className={`px-2.5 py-1.5 text-xs font-semibold rounded-md transition-colors cursor-pointer min-h-[32px] ${
                confidenceFilter === "review"
                  ? "bg-amber-100 text-amber-900 shadow-2xs"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              Needs Review
            </button>
          </div>

          {/* Sort Dropdown with clear accessible label */}
          <div className="flex items-center gap-1.5 text-xs text-[#45828B]">
            <Filter className="w-3.5 h-3.5 text-[#45828B]" />
            <label htmlFor="sort-resumes" className="sr-only">
              Sort candidates by
            </label>
            <select
              id="sort-resumes"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as SortOption)}
              className="py-1.5 px-2.5 rounded-lg border border-[#E0E5E9] bg-white text-xs text-[#055B65] font-medium focus:outline-none focus:ring-2 focus:ring-[#055B65] min-h-[32px]"
            >
              <option value="date_desc">Newest First</option>
              <option value="confidence_desc">Highest Confidence</option>
              <option value="skills_desc">Most Skills</option>
            </select>
          </div>
        </div>
      </div>

      {/* Data Table / Content Area */}
      {loading ? (
        <div className="rounded-xl border border-slate-200 bg-white p-8 space-y-4 animate-pulse">
          <div className="h-4 w-48 bg-slate-200 rounded" />
          <div className="space-y-3">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="h-12 bg-slate-100 rounded" />
            ))}
          </div>
        </div>
      ) : error ? (
        <div className="rounded-xl border border-rose-200 bg-white p-8 text-center space-y-3">
          <AlertCircle className="w-8 h-8 text-rose-500 mx-auto" />
          <p className="text-sm font-semibold text-slate-900">
            Unable to load candidate library
          </p>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">{error}</p>
          <button
            onClick={handleRetry}
            type="button"
            className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-[#055B65] text-white text-xs font-semibold hover:bg-[#033c43] cursor-pointer min-h-[36px]"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Retry</span>
          </button>
        </div>
      ) : paginatedResumes.length === 0 ? (
        <div className="rounded-xl border border-[#E0E5E9] bg-white p-12 text-center space-y-3">
          <FileText className="w-10 h-10 text-[#B2C9C5] mx-auto" />
          <p className="text-sm font-semibold text-slate-800">
            {resumes.length === 0 ? "No resumes parsed yet" : "No candidates matching filters"}
          </p>
          <p className="text-xs text-[#45828B] max-w-sm mx-auto">
            {resumes.length === 0
              ? "Upload your first resume document to extract structured candidate profiles."
              : `No profiles matched "${searchQuery || confidenceFilter}". Reset your filters to see all candidates.`}
          </p>
          <div className="pt-2">
            {resumes.length === 0 ? (
              <Link
                href="/upload"
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-[#055B65] text-white text-xs font-semibold uppercase tracking-wider hover:bg-[#033c43]"
              >
                <UploadCloud className="w-4 h-4 text-[#1BD488]" />
                <span>Upload First Resume</span>
              </Link>
            ) : (
              <button
                type="button"
                onClick={handleClearFilters}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-medium cursor-pointer"
              >
                <X className="w-3.5 h-3.5" />
                <span>Reset all filters</span>
              </button>
            )}
          </div>
        </div>
      ) : (
        <div className="rounded-xl border border-[#E0E5E9] bg-white overflow-hidden shadow-2xs">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs divide-y divide-[#E0E5E9]">
              <thead className="bg-[#FBFCFC] text-[#45828B] font-semibold uppercase tracking-wider text-[11px] border-b border-[#E0E5E9]">
                <tr>
                  <th scope="col" className="py-3 px-4">Candidate</th>
                  <th scope="col" className="py-3 px-4">Email</th>
                  <th scope="col" className="py-3 px-4">Key Skills</th>
                  <th scope="col" className="py-3 px-4">Experience</th>
                  <th scope="col" className="py-3 px-4">Upload Date</th>
                  <th scope="col" className="py-3 px-4">Confidence</th>
                  <th scope="col" className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E0E5E9]">
                {paginatedResumes.map((item) => {
                  const candidateName =
                    item.parsed_resume?.personal_info?.name || "Unnamed Candidate";
                  const email = item.parsed_resume?.personal_info?.email;
                  const skills = item.parsed_resume?.skills || [];
                  const expCount = item.parsed_resume?.experience?.length || 0;
                  const primaryRole =
                    item.parsed_resume?.experience?.[0]?.job_title || null;
                  const confidence = item.parsed_resume?.confidence_score;

                  return (
                    <tr
                      key={item.id}
                      className="hover:bg-[#055B65]/5 transition-colors group cursor-pointer"
                      onClick={() => {
                        router.push(`/resumes/${item.id}`);
                      }}
                    >
                      {/* Candidate Name & Filename */}
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

                      {/* Key Skills */}
                      <td className="py-3 px-4 min-w-[200px]">
                        <div className="flex flex-wrap items-center gap-1">
                          {skills.slice(0, 3).map((s, idx) => (
                            <span
                              key={idx}
                              className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-[#E0E5E9]/50 text-[#055B65] border border-[#B2C9C5]/40"
                            >
                              {s}
                            </span>
                          ))}
                          {skills.length > 3 && (
                            <span className="text-[10px] text-[#45828B] font-mono">
                              +{skills.length - 3}
                            </span>
                          )}
                        </div>
                      </td>

                      {/* Experience */}
                      <td className="py-3 px-4 min-w-[150px] text-slate-700">
                        {primaryRole ? (
                          <div className="truncate max-w-[160px]">
                            <span className="font-semibold text-slate-800">{primaryRole}</span>
                            <span className="text-[#45828B] block text-[11px]">
                              {expCount} {expCount === 1 ? "role" : "roles"}
                            </span>
                          </div>
                        ) : (
                          <span className="text-slate-400 italic">No experience</span>
                        )}
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

                      {/* Confidence Badge */}
                      <td className="py-3 px-4 whitespace-nowrap">
                        <ConfidenceBadge score={confidence} size="sm" />
                      </td>

                      {/* Actions with touch-friendly touch target (Fitts's Law) */}
                      <td className="py-3 px-4 text-right whitespace-nowrap">
                        <div className="inline-flex items-center gap-1">
                          <button
                            type="button"
                            onClick={(e) => downloadJSON(item, e)}
                            className="p-2 min-h-[36px] min-w-[36px] flex items-center justify-center rounded-lg text-[#45828B] hover:text-[#055B65] hover:bg-[#E0E5E9]/50 cursor-pointer"
                            title="Download JSON"
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

          {/* Pagination Controls */}
          {totalPages > 1 && (
            <div className="p-3 border-t border-[#E0E5E9] bg-[#FBFCFC] flex items-center justify-between text-xs text-[#45828B]">
              <div>
                Showing {(currentPage - 1) * ITEMS_PER_PAGE + 1} to{" "}
                {Math.min(currentPage * ITEMS_PER_PAGE, processedResumes.length)} of{" "}
                {processedResumes.length} candidates
              </div>

              <div className="flex items-center gap-1">
                <button
                  type="button"
                  onClick={() => setCurrentPage((p) => Math.max(p - 1, 1))}
                  disabled={currentPage === 1}
                  className="p-1.5 min-h-[36px] min-w-[36px] flex items-center justify-center rounded border border-[#E0E5E9] bg-white disabled:opacity-40 hover:bg-[#E0E5E9]/50 transition-colors cursor-pointer"
                  aria-label="Previous page"
                >
                  <ChevronLeft className="w-4 h-4 text-[#055B65]" />
                </button>
                <span className="px-2 font-mono tabular-nums text-[#055B65] font-semibold">
                  Page {currentPage} of {totalPages}
                </span>
                <button
                  type="button"
                  onClick={() => setCurrentPage((p) => Math.min(p + 1, totalPages))}
                  disabled={currentPage === totalPages}
                  className="p-1.5 min-h-[36px] min-w-[36px] flex items-center justify-center rounded border border-[#E0E5E9] bg-white disabled:opacity-40 hover:bg-[#E0E5E9]/50 transition-colors cursor-pointer"
                  aria-label="Next page"
                >
                  <ChevronRight className="w-4 h-4 text-[#055B65]" />
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </main>
  );
}

export default function ResumesLibraryPage() {
  return <ResumesLibraryContent />;
}
