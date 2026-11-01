"use client";

import { useEffect, useState, Suspense } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { getResumeById } from "@/lib/api";
import { ParseResponse } from "@/types/resume";
import { ParsedResumeView } from "@/components/parsed-resume";
import { ArrowLeft, Download, Loader2, AlertCircle } from "lucide-react";

function ResultsContent() {
  const params = useParams();
  const docId = params?.id as string;

  const [data, setData] = useState<ParseResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!docId) return;

    let mounted = true;
    getResumeById(docId)
      .then((res) => {
        if (mounted) {
          setData(res);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (mounted) {
          setError(err.message || "Failed to load parsed resume");
          setLoading(false);
        }
      });

    return () => {
      mounted = false;
    };
  }, [docId]);

  const downloadJSON = () => {
    if (!data) return;
    const jsonStr = JSON.stringify(data.parsed_resume, null, 2);
    const blob = new Blob([jsonStr], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${data.parsed_resume.personal_info.name || "resume"}_parsed.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
          <p className="text-sm text-gray-500 font-medium">
            Loading parsed resume...
          </p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
        <div className="max-w-md w-full bg-white rounded-2xl border border-gray-200 p-6 text-center space-y-4">
          <div className="w-12 h-12 rounded-full bg-red-50 text-red-600 flex items-center justify-center mx-auto">
            <AlertCircle className="w-6 h-6" />
          </div>
          <h2 className="text-lg font-bold text-gray-900">Resume Not Found</h2>
          <p className="text-sm text-gray-500">{error || "Unable to retrieve document."}</p>
          <Link
            href="/"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 transition"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Return to Upload</span>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-gray-50 py-10 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Navigation Bar */}
        <div className="flex items-center justify-between">
          <Link
            href="/"
            className="inline-flex items-center gap-2 text-sm font-medium text-gray-600 hover:text-gray-900 transition"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Upload Another Resume</span>
          </Link>

          <button
            onClick={downloadJSON}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-white border border-gray-200/90 text-sm font-medium text-gray-700 hover:bg-gray-50 shadow-sm transition"
          >
            <Download className="w-4 h-4 text-gray-500" />
            <span>Download JSON</span>
          </button>
        </div>

        {/* Structured Results Display */}
        <ParsedResumeView
          resume={data.parsed_resume}
          filename={data.filename}
        />
      </div>
    </main>
  );
}

export default function ResultsPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        </div>
      }
    >
      <ResultsContent />
    </Suspense>
  );
}
