"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  UploadCloud,
  Files,
  Settings,
  FileSearch,
  Activity,
  X,
} from "lucide-react";

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
  className?: string;
}

const NAV_ITEMS = [
  {
    name: "Dashboard",
    href: "/",
    icon: LayoutDashboard,
  },
  {
    name: "Upload Resume",
    href: "/upload",
    icon: UploadCloud,
  },
  {
    name: "All Resumes",
    href: "/resumes",
    icon: Files,
  },
  {
    name: "Settings",
    href: "/settings",
    icon: Settings,
  },
];

export function Sidebar({ isOpen, onClose, className = "" }: SidebarProps) {
  const pathname = usePathname();

  const isActive = (href: string) => {
    if (href === "/") {
      return pathname === "/";
    }
    return pathname.startsWith(href);
  };

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-slate-900/40 z-40 lg:hidden backdrop-blur-2xs"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 w-64 bg-white border-r border-slate-200 flex flex-col transition-transform duration-200 ease-in-out lg:translate-x-0 ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        } ${className}`}
      >
        {/* Brand Header */}
        <div className="h-16 flex items-center justify-between px-5 border-b border-[#E0E5E9] shrink-0">
          <Link
            href="/"
            onClick={onClose}
            className="flex items-center gap-2.5 font-bold text-slate-900 tracking-tight"
          >
            <div className="w-8 h-8 rounded-lg bg-[#055B65] text-[#1BD488] flex items-center justify-center shrink-0 shadow-2xs">
              <FileSearch className="w-4 h-4" />
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-semibold leading-tight text-[#055B65]">
                ResumeParser
              </span>
              <span className="text-[10px] font-medium text-[#45828B] uppercase tracking-wider">
                NLP Intelligence
              </span>
            </div>
          </Link>

          {/* Mobile close button */}
          {onClose && (
            <button
              onClick={onClose}
              type="button"
              className="lg:hidden p-2 min-h-[40px] min-w-[40px] flex items-center justify-center rounded-md text-slate-500 hover:text-slate-700 hover:bg-slate-100 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#055B65]"
              aria-label="Close navigation"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>

        {/* Navigation Items */}
        <div className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
          <div className="px-2 pb-2">
            <span className="text-[10px] font-semibold uppercase tracking-wider text-[#45828B]">
              Navigation
            </span>
          </div>

          {NAV_ITEMS.map((item) => {
            const active = isActive(item.href);
            const Icon = item.icon;

            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={onClose}
                className={`flex items-center gap-3 px-3 py-2.5 min-h-[38px] rounded-lg text-xs font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#055B65] ${
                  active
                    ? "bg-[#055B65]/10 text-[#055B65] font-semibold"
                    : "text-slate-600 hover:text-[#055B65] hover:bg-[#E0E5E9]/30"
                }`}
              >
                <Icon
                  className={`w-4 h-4 shrink-0 transition-colors ${
                    active ? "text-[#055B65]" : "text-slate-400"
                  }`}
                />
                <span>{item.name}</span>
              </Link>
            );
          })}
        </div>

        {/* Footer / System status pill */}
        <div className="p-3.5 border-t border-[#E0E5E9] shrink-0">
          <div className="p-2.5 rounded-lg bg-[#055B65]/5 border border-[#B2C9C5]/50 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-[#1BD488] animate-pulse" />
              <div className="flex flex-col">
                <span className="text-[11px] font-medium text-[#055B65] leading-tight">
                  Pipeline Active
                </span>
                <span className="text-[10px] text-[#45828B] font-mono">
                  DistilBERT + Rules
                </span>
              </div>
            </div>
            <Link
              href="/settings"
              onClick={onClose}
              className="text-[#45828B] hover:text-[#055B65] p-1 rounded transition-colors"
              title="System details"
            >
              <Activity className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </aside>
    </>
  );
}

