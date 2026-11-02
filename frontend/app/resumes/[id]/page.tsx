"use client";

import { useEffect, useState, Suspense } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { getResumeById } from "@/lib/api";
import { ParseResponse } from "@/types/resume";
import { ParsedResumeView } from "@/components/parsed-resume";
import { ResumeProfileSkeleton } from "@/components/skeleton-loader";
import { ArrowLeft, Download, AlertCircle, RotateCcw } from "lucide-react";

function ResumeDetailContent() {
  const params = useParams();
  const docId = params?.id as string;

  const [data, setData] = useState<ParseResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    if (!docId) return;

    let isMounted = true;
    getResumeById(docId)
      .then((res) => {
        if (isMounted) {
          setData(res);
          setLoading(false);
          setError(null);
        }
      })
      .catch((err) => {
        if (isMounted) {
          setError(
            err.message ||
              "We could not retrieve this candidate record. Please verify your connection."
          );
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [docId, reloadKey]);

  const handleRetry = () => {
    setLoading(true);
    setError(null);
    setReloadKey((prev) => prev + 1);
  };

  const downloadJSON = () => {
    if (!data) return;
    const jsonStr = JSON.stringify(data.parsed_resume, null, 2);
    const blob = new Blob([jsonStr], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    const safeName = (data.parsed_resume.personal_info?.name || "resume")
      .toLowerCase()
      .replace(/[^a-z0-9]/g, "_");
    a.download = `${safeName}_parsed.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <main className="py-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <ResumeProfileSkeleton />
      </main>
    );
  }

  if (error || !data) {
    return (
      <main className="py-12 px-4 sm:px-6 lg:px-8 max-w-md mx-auto">
        <div className="bg-white rounded-xl border border-[#E0E5E9] p-6 space-y-4 shadow-2xs">
          <div className="flex items-center gap-3 text-rose-600">
            <div className="p-2 rounded-lg bg-rose-50 border border-rose-100">
              <AlertCircle className="w-5 h-5" />
            </div>
            <h2 className="text-base font-semibold text-slate-900">
              Candidate Dossier Not Found
            </h2>
          </div>

          <p className="text-xs text-[#45828B] leading-relaxed">
            {error || "The requested resume document could not be located in the database."}
          </p>

          <div className="flex items-center gap-2 pt-2 border-t border-[#E0E5E9]">
            <button
              onClick={handleRetry}
              type="button"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#055B65] hover:bg-[#033c43] text-white text-xs font-semibold transition-colors cursor-pointer"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Retry</span>
            </button>
            <Link
              href="/resumes"
              className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-600 hover:text-[#055B65] transition-colors"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back to Library</span>
            </Link>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="py-6 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-5">
      {/* Navigation Header */}
      <header className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[#E0E5E9]">
        <div className="flex items-center gap-2 text-xs text-[#45828B]">
          <Link
            href="/resumes"
            className="hover:text-[#055B65] transition-colors inline-flex items-center gap-1 font-medium"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>All Resumes</span>
          </Link>
          <span className="text-[#B2C9C5]">/</span>
          <span className="font-semibold text-[#055B65] truncate max-w-[200px] sm:max-w-xs">
            {data.parsed_resume?.personal_info?.name || data.filename}
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={downloadJSON}
            type="button"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white border border-[#E0E5E9] text-xs font-semibold text-[#055B65] hover:bg-[#FBFCFC] hover:border-[#B2C9C5] transition-colors shadow-2xs cursor-pointer min-h-[36px]"
          >
            <Download className="w-3.5 h-3.5 text-[#055B65]" />
            <span>Download JSON</span>
          </button>
        </div>
      </header>

      {/* Structured Candidate Profile Review View */}
      <ParsedResumeView
        resume={data.parsed_resume}
        filename={data.filename}
      />
    </main>
  );
}

export default function ResumeDetailPage() {
  return (
    <Suspense
      fallback={
        <main className="py-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
          <ResumeProfileSkeleton />
        </main>
      }
    >
      <ResumeDetailContent />
    </Suspense>
  );
}

