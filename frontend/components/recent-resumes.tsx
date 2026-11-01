"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { listResumes } from "@/lib/api";
import { ParseResponse } from "@/types/resume";
import { FileText, ArrowRight, Database, Loader2 } from "lucide-react";

export function RecentResumes() {
  const [resumes, setResumes] = useState<ParseResponse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    listResumes()
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

  if (loading) {
    return (
      <div className="pt-8 border-t border-gray-100 flex items-center justify-center py-6 text-gray-400">
        <Loader2 className="w-5 h-5 animate-spin mr-2" />
        <span className="text-xs">Loading parsed documents...</span>
      </div>
    );
  }

  if (resumes.length === 0) {
    return null;
  }

  return (
    <div className="pt-8 border-t border-gray-100">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
          <Database className="w-5 h-5 text-gray-400" />
          Parsed Resumes ({resumes.length})
        </h2>
      </div>

      <div className="grid gap-3 sm:grid-cols-2">
        {resumes.map((item) => (
          <Link
            key={item.id}
            href={`/results/${item.id}`}
            className="flex items-center justify-between p-4 rounded-xl border border-gray-200/80 bg-white hover:border-blue-300 hover:shadow-sm transition group"
          >
            <div className="flex items-center gap-3 min-w-0">
              <div className="p-2 rounded-lg bg-gray-100 group-hover:bg-blue-50 text-gray-600 group-hover:text-blue-600 transition">
                <FileText className="w-4 h-4" />
              </div>
              <div className="min-w-0">
                <p className="text-sm font-semibold text-gray-900 truncate">
                  {item.parsed_resume.personal_info.name || item.filename}
                </p>
                <p className="text-xs text-gray-400 truncate">
                  {item.filename}
                </p>
              </div>
            </div>
            <ArrowRight className="w-4 h-4 text-gray-400 group-hover:text-blue-600 group-hover:translate-x-0.5 transition flex-shrink-0" />
          </Link>
        ))}
      </div>
    </div>
  );
}

