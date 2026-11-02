import Link from "next/link";
import { FileQuestion, LayoutDashboard, Files, UploadCloud } from "lucide-react";

export default function NotFound() {
  return (
    <main className="min-h-[70vh] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full bg-white rounded-2xl border border-[#E0E5E9] p-8 text-center space-y-6 shadow-2xs">
        <div className="w-14 h-14 mx-auto rounded-2xl bg-[#055B65]/10 text-[#055B65] flex items-center justify-center">
          <FileQuestion className="w-7 h-7" />
        </div>

        <div className="space-y-2">
          <span className="text-[11px] font-mono font-bold tracking-wider uppercase text-[#45828B]">
            404 — Page Not Found
          </span>
          <h1 className="text-xl font-bold text-[#055B65] tracking-tight">
            Document or Screen Not Located
          </h1>
          <p className="text-xs text-[#45828B] leading-relaxed">
            The requested resume dossier or application screen does not exist or has been relocated in the repository.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-2.5 pt-2">
          <Link
            href="/"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-[#055B65] hover:bg-[#033c43] text-white text-xs font-semibold transition-colors min-h-[40px]"
          >
            <LayoutDashboard className="w-3.5 h-3.5 text-[#1BD488]" />
            <span>Dashboard</span>
          </Link>

          <Link
            href="/resumes"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg border border-[#E0E5E9] bg-white hover:bg-[#FBFCFC] text-[#055B65] text-xs font-semibold transition-colors min-h-[40px]"
          >
            <Files className="w-3.5 h-3.5" />
            <span>Candidate Library</span>
          </Link>

          <Link
            href="/upload"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg border border-[#E0E5E9] bg-white hover:bg-[#FBFCFC] text-[#055B65] text-xs font-semibold transition-colors min-h-[40px]"
          >
            <UploadCloud className="w-3.5 h-3.5" />
            <span>Upload</span>
          </Link>
        </div>
      </div>
    </main>
  );
}

