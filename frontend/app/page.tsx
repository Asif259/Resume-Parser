import { UploadZone } from "@/components/upload-zone";
import { RecentResumes } from "@/components/recent-resumes";
import { Sparkles } from "lucide-react";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-50 via-white to-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto space-y-12">
        {/* Header Hero */}
        <div className="text-center space-y-3">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-50 text-blue-700 text-xs font-semibold tracking-wide uppercase border border-blue-100">
            <Sparkles className="w-3.5 h-3.5" />
            <span>NLP Resume Intelligence</span>
          </div>
          <h1 className="text-4xl sm:text-5xl font-extrabold text-gray-900 tracking-tight">
            Resume Parser & Extractor
          </h1>
          <p className="text-base sm:text-lg text-gray-600 max-w-xl mx-auto">
            Convert unstructured resumes into validated, structured candidate data with
            hybrid NLP, custom NER, and intelligent entity grouping.
          </p>
        </div>

        {/* Upload Zone */}
        <UploadZone />

        {/* Recent Resumes */}
        <RecentResumes />
      </div>
    </main>
  );
}
