"use client";

import { useEffect, useState } from "react";
import { checkHealth, HealthResponse } from "@/lib/api";
import {
  CheckCircle2,
  AlertCircle,
  Cpu,
  FileText,
  ShieldAlert,
  Server,
  RotateCcw,
} from "lucide-react";

export default function SettingsPage() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let isMounted = true;
    checkHealth()
      .then((res) => {
        if (isMounted) {
          setHealth(res);
          setLoading(false);
          setError(null);
        }
      })
      .catch((err) => {
        if (isMounted) {
          setError(err.message || "Failed to connect to backend service.");
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [reloadKey]);

  const handleVerify = () => {
    setLoading(true);
    setError(null);
    setReloadKey((prev) => prev + 1);
  };

  return (
    <main className="py-8 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="space-y-1 pb-4 border-b border-[#E0E5E9]">
        <h1 className="text-2xl font-bold text-[#055B65] tracking-tight">
          System Information & Settings
        </h1>
        <p className="text-xs sm:text-sm text-[#45828B]">
          Inspection parameters, backend connection health, and machine learning pipeline specifications.
        </p>
      </div>

      {/* Backend Connection Status */}
      <section className="bg-white rounded-xl border border-[#E0E5E9] p-5 space-y-4 shadow-2xs">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Server className="w-4 h-4 text-[#055B65]" />
            <h2 className="text-sm font-semibold text-[#055B65]">
              Backend Service Health
            </h2>
          </div>

          <button
            onClick={handleVerify}
            type="button"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 min-h-[36px] text-xs font-semibold text-[#055B65] hover:text-[#033c43] hover:bg-[#FBFCFC] rounded-lg border border-[#E0E5E9] transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#055B65]"
          >
            <RotateCcw className="w-3.5 h-3.5 text-[#055B65]" />
            <span>Check Health</span>
          </button>
        </div>

        <div className="p-4 rounded-lg bg-[#FBFCFC] border border-[#E0E5E9] flex items-center justify-between">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span
                className={`w-2 h-2 rounded-full ${
                  health?.status === "ok" ? "bg-[#1BD488]" : "bg-rose-500"
                }`}
              />
              <span className="text-xs font-semibold text-slate-900">
                {loading
                  ? "Pinging /health endpoint..."
                  : health?.status === "ok"
                  ? "FastAPI Service Operational"
                  : "Service Unreachable"}
              </span>
            </div>
            <p className="text-[11px] text-[#45828B] font-mono">
              Target: {process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}
            </p>
          </div>

          <div className="text-right">
            {health?.status === "ok" ? (
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded text-xs font-semibold bg-[#1BD488]/15 text-[#033c43] border border-[#1BD488]/40">
                <CheckCircle2 className="w-3 h-3 text-[#055B65]" />
                <span>Healthy</span>
              </span>
            ) : error ? (
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded text-xs font-medium bg-rose-50 text-rose-700 border border-rose-200">
                <AlertCircle className="w-3 h-3 text-rose-600" />
                <span>Error</span>
              </span>
            ) : null}
          </div>
        </div>
      </section>

      {/* NLP Pipeline & Models */}
      <section className="bg-white rounded-xl border border-[#E0E5E9] p-5 space-y-4 shadow-2xs">
        <div className="flex items-center gap-2">
          <Cpu className="w-4 h-4 text-[#055B65]" />
          <h2 className="text-sm font-semibold text-[#055B65]">
            Extraction Architecture
          </h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div className="p-3.5 rounded-lg border border-[#E0E5E9] bg-[#FBFCFC] space-y-1.5">
            <span className="font-semibold text-[#055B65] block">
              Custom DistilBERT NER
            </span>
            <p className="text-slate-600 leading-relaxed text-[11px]">
              Fine-tuned Hugging Face transformer token classifier trained on labeled resume datasets for roles, candidates, and institutions.
            </p>
          </div>

          <div className="p-3.5 rounded-lg border border-[#E0E5E9] bg-[#FBFCFC] space-y-1.5">
            <span className="font-semibold text-[#055B65] block">
              Sentence Transformers
            </span>
            <p className="text-slate-600 leading-relaxed text-[11px]">
              <code className="font-mono text-[#055B65]">all-MiniLM-L6-v2</code> embeddings for dense semantic skill matching and category taxonomy normalization.
            </p>
          </div>

          <div className="p-3.5 rounded-lg border border-[#E0E5E9] bg-[#FBFCFC] space-y-1.5">
            <span className="font-semibold text-[#055B65] block">
              Text Extraction Engine
            </span>
            <p className="text-slate-600 leading-relaxed text-[11px]">
              PyMuPDF (fitz) for PDF documents, python-docx for Word files, and Tesseract OCR with automatic fallback for low-density scans.
            </p>
          </div>

          <div className="p-3.5 rounded-lg border border-[#E0E5E9] bg-[#FBFCFC] space-y-1.5">
            <span className="font-semibold text-[#055B65] block">
              Database Persistence
            </span>
            <p className="text-slate-600 leading-relaxed text-[11px]">
              SQLAlchemy ORM with local SQLite storage (<code className="font-mono text-[#055B65]">resumes.db</code>) storing full JSON dossiers and raw text.
            </p>
          </div>
        </div>
      </section>

      {/* Constraints & Ingestion Specs */}
      <section className="bg-white rounded-xl border border-[#E0E5E9] p-5 space-y-3 shadow-2xs">
        <div className="flex items-center gap-2">
          <FileText className="w-4 h-4 text-[#055B65]" />
          <h2 className="text-sm font-semibold text-[#055B65]">
            Ingestion Specifications
          </h2>
        </div>

        <dl className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-1 text-xs">
          <div className="p-3 rounded-lg border border-[#E0E5E9] bg-[#FBFCFC]">
            <dt className="text-[#45828B] font-medium">Supported Formats</dt>
            <dd className="font-semibold text-[#055B65] mt-1 font-mono">
              .pdf, .docx, .doc, .png, .jpg
            </dd>
          </div>

          <div className="p-3 rounded-lg border border-[#E0E5E9] bg-[#FBFCFC]">
            <dt className="text-[#45828B] font-medium">Maximum Upload Size</dt>
            <dd className="font-semibold text-[#055B65] mt-1 font-mono">
              10 MB per file
            </dd>
          </div>

          <div className="p-3 rounded-lg border border-[#E0E5E9] bg-[#FBFCFC]">
            <dt className="text-[#45828B] font-medium">Confidence Calibration</dt>
            <dd className="font-semibold text-[#055B65] mt-1 font-mono">
              Platt scaling & heuristic weighting
            </dd>
          </div>
        </dl>
      </section>

      {/* Note on Persistent Database Editing */}
      <div className="rounded-lg bg-amber-50/80 border border-amber-200/90 p-4 flex items-start gap-3 text-xs text-amber-900">
        <ShieldAlert className="w-4 h-4 text-amber-700 shrink-0 mt-0.5" />
        <div className="space-y-1">
          <p className="font-semibold text-amber-900">
            Database Update Capability Note
          </p>
          <p className="text-amber-800 leading-relaxed">
            The current FastAPI backend exposes <code className="font-mono bg-amber-100/60 px-1 py-0.2 rounded">POST /api/parse</code> and <code className="font-mono bg-amber-100/60 px-1 py-0.2 rounded">GET /api/resumes</code> endpoints. In accordance with architectural constraints, the candidate review interface operates as a local review mode and allows exporting audited JSON without simulating non-existent database mutation endpoints.
          </p>
        </div>
      </div>
    </main>
  );
}
