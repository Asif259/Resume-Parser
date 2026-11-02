"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { listResumes } from "@/lib/api";
import { ParseResponse } from "@/types/resume";
import { ConfidenceBadge } from "@/components/confidence-badge";
import { FileText, ArrowRight, Clock } from "lucide-react";

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

  const formatDate = (dateStr: string): string => {
    try {
      const date = new Date(dateStr);
      return new Intl.DateTimeFormat("en-US", {
        month: "short",
        day: "numeric",
        hour: "numeric",
        minute: "numeric",
      }).format(date);
    } catch {
      return dateStr;
    }
  };

  if (loading) {
    return (
      <div className="pt-6 border-t border-slate-200 space-y-3">
        <div className="h-4 w-32 bg-slate-200 rounded animate-pulse" />
        <div className="divide-y divide-slate-100 border border-slate-200 rounded-lg bg-white overflow-hidden">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="p-3.5 flex items-center justify-between animate-pulse">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded bg-slate-100" />
                <div className="space-y-1.5">
                  <div className="h-3.5 w-36 bg-slate-200 rounded" />
                  <div className="h-3 w-24 bg-slate-100 rounded" />
                </div>
              </div>
              <div className="h-5 w-16 bg-slate-100 rounded" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (resumes.length === 0) {
    return null;
  }

  return (
    <div className="pt-8 border-t border-[#E0E5E9] space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h2 className="text-sm font-semibold text-[#055B65]">
            Recent Resumes
          </h2>
          <span className="text-xs text-[#45828B] tabular-nums font-mono">
            ({resumes.length})
          </span>
        </div>
      </div>

      <div className="divide-y divide-[#E0E5E9] border border-[#E0E5E9] rounded-lg bg-white overflow-hidden shadow-2xs">
        {resumes.map((item) => {
          const name = item.parsed_resume?.personal_info?.name;
          const confidence = item.parsed_resume?.confidence_score;
          const skillsCount = item.parsed_resume?.skills?.length || 0;
          const expCount = item.parsed_resume?.experience?.length || 0;

          return (
            <Link
              key={item.id}
              href={`/resumes/${item.id}`}
              className="flex items-center justify-between p-3.5 hover:bg-[#055B65]/5 transition-colors group"
            >
              <div className="flex items-center gap-3 min-w-0">
                <div className="p-2 rounded bg-[#E0E5E9]/50 text-slate-500 group-hover:text-[#055B65] group-hover:bg-[#055B65]/10 transition-colors shrink-0">
                  <FileText className="w-4 h-4" />
                </div>
                <div className="min-w-0">
                  <p className="text-sm font-semibold text-slate-900 truncate group-hover:text-[#055B65] transition-colors">
                    {name || item.filename}
                  </p>
                  <div className="flex items-center gap-2 text-xs text-[#45828B] mt-0.5">
                    <span className="truncate max-w-[150px] font-mono text-[11px]">
                      {item.filename}
                    </span>
                    <span className="text-[#B2C9C5]">•</span>
                    <span className="tabular-nums">
                      {skillsCount} skills
                    </span>
                    <span className="text-[#B2C9C5]">•</span>
                    <span className="tabular-nums">
                      {expCount} roles
                    </span>
                    {item.created_at && (
                      <>
                        <span className="hidden sm:inline text-[#B2C9C5]">•</span>
                        <span className="hidden sm:inline-flex items-center gap-1 text-[11px] text-[#45828B]">
                          <Clock className="w-3 h-3 text-[#45828B]" />
                          <span>{formatDate(item.created_at)}</span>
                        </span>
                      </>
                    )}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-3 shrink-0 ml-4">
                {confidence !== null && confidence !== undefined && (
                  <ConfidenceBadge score={confidence} size="sm" />
                )}
                <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-[#055B65] group-hover:translate-x-0.5 transition-all" />
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
