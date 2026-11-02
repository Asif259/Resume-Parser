"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { checkHealth } from "@/lib/api";
import { Menu, UploadCloud, CheckCircle2, AlertCircle } from "lucide-react";

interface TopNavProps {
  onOpenMobileMenu: () => void;
}

export function TopNav({ onOpenMobileMenu }: TopNavProps) {
  const pathname = usePathname();
  const [backendHealthy, setBackendHealthy] = useState<boolean | null>(null);

  useEffect(() => {
    let mounted = true;
    checkHealth()
      .then((res) => {
        if (mounted) setBackendHealthy(res.status === "ok");
      })
      .catch(() => {
        if (mounted) setBackendHealthy(false);
      });

    return () => {
      mounted = false;
    };
  }, []);

  const getBreadcrumbTitle = () => {
    if (pathname === "/") return "Dashboard";
    if (pathname === "/upload") return "Upload Resume";
    if (pathname === "/resumes") return "All Resumes";
    if (pathname === "/settings") return "System Settings";
    if (pathname.startsWith("/resumes/") || pathname.startsWith("/results/")) {
      return "Candidate Profile";
    }
    return "Resume Parser";
  };

  return (
    <header className="h-16 bg-[#FBFCFC] border-b border-[#E0E5E9] sticky top-0 z-30 flex items-center justify-between px-4 sm:px-6 lg:px-8">
      {/* Left: Mobile Toggle & Page Title */}
      <div className="flex items-center gap-3">
        <button
          onClick={onOpenMobileMenu}
          type="button"
          className="lg:hidden p-2 min-h-[40px] min-w-[40px] flex items-center justify-center rounded-md text-slate-600 hover:text-slate-900 hover:bg-[#E0E5E9]/50 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#055B65]"
          aria-label="Open navigation menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2 text-xs text-slate-500">
          <span className="font-semibold text-[#055B65] text-sm">
            {getBreadcrumbTitle()}
          </span>
        </div>
      </div>

      {/* Right: Status Pill & Upload CTA */}
      <div className="flex items-center gap-3">
        {/* Live Backend Connection Indicator */}
        <div
          className={`hidden sm:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium border ${
            backendHealthy === true
              ? "bg-[#1BD488]/15 text-[#033c43] border-[#1BD488]/40"
              : backendHealthy === false
              ? "bg-rose-50 text-rose-700 border-rose-200"
              : "bg-[#E0E5E9]/50 text-slate-600 border-[#E0E5E9]"
          }`}
          title={
            backendHealthy === true
              ? "FastAPI NLP backend connected"
              : backendHealthy === false
              ? "FastAPI backend unreachable"
              : "Checking backend connection..."
          }
        >
          {backendHealthy === true ? (
            <CheckCircle2 className="w-3 h-3 text-[#055B65]" />
          ) : backendHealthy === false ? (
            <AlertCircle className="w-3 h-3 text-rose-600" />
          ) : (
            <span className="w-2 h-2 rounded-full bg-slate-400 animate-pulse" />
          )}
          <span>
            {backendHealthy === true
              ? "API Connected"
              : backendHealthy === false
              ? "Backend Offline"
              : "Connecting..."}
          </span>
        </div>

        {/* Global Upload CTA */}
        {pathname !== "/upload" && (
          <Link
            href="/upload"
            className="inline-flex items-center gap-1.5 px-3.5 py-2 min-h-[36px] rounded-lg bg-[#055B65] hover:bg-[#033c43] text-white text-xs font-medium transition-colors shadow-2xs focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#1BD488]"
          >
            <UploadCloud className="w-3.5 h-3.5 text-[#1BD488]" />
            <span>Upload Resume</span>
          </Link>
        )}
      </div>
    </header>
  );
}

