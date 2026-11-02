"use client";

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { uploadAndParseResume } from "@/lib/api";
import {
  UploadCloud,
  FileText,
  AlertCircle,
  Loader2,
  X,
  ArrowRight,
} from "lucide-react";

const ALLOWED_EXTENSIONS = ["pdf", "docx", "doc", "jpg", "jpeg", "png", "webp"];
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

export function UploadZone() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const validateFile = (file: File): string | null => {
    const ext = file.name.split(".").pop()?.toLowerCase();
    if (!ext || !ALLOWED_EXTENSIONS.includes(ext)) {
      return `File type .${ext || "unknown"} is not supported. Please upload a PDF, DOCX, or image.`;
    }
    if (file.size > MAX_FILE_SIZE) {
      const sizeMB = (file.size / (1024 * 1024)).toFixed(1);
      return `File size (${sizeMB} MB) exceeds the 10 MB limit.`;
    }
    return null;
  };

  const handleFileSelect = (file: File) => {
    setErrorMessage(null);
    const validationError = validateFile(file);
    if (validationError) {
      setErrorMessage(validationError);
      setSelectedFile(null);
      return;
    }
    setSelectedFile(file);
  };

  const handleSubmit = async () => {
    if (!selectedFile) return;
    setIsUploading(true);
    setErrorMessage(null);

    try {
      const result = await uploadAndParseResume(selectedFile);
      router.push(`/resumes/${result.id}`);
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Unable to parse resume. Check your network connection and try again.";
      setErrorMessage(message);
      setIsUploading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if ((e.key === "Enter" || e.key === " ") && !isUploading && !selectedFile) {
      e.preventDefault();
      fileInputRef.current?.click();
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="w-full space-y-4">
      {/* Drop area */}
      <div
        role={selectedFile ? "region" : "button"}
        tabIndex={isUploading || selectedFile ? -1 : 0}
        onKeyDown={handleKeyDown}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => !isUploading && !selectedFile && fileInputRef.current?.click()}
        aria-label={selectedFile ? "Selected file preview" : "Upload document dropzone. Press Enter or Space to browse."}
        className={`rounded-xl border-2 border-dashed p-6 sm:p-8 text-center transition-colors focus-visible:ring-2 focus-visible:ring-[#055B65] focus-visible:outline-none ${
          isDragging
            ? "border-[#055B65] bg-[#055B65]/5"
            : selectedFile
            ? "border-[#E0E5E9] bg-white"
            : "border-[#E0E5E9] hover:border-[#B2C9C5] bg-white cursor-pointer"
        }`}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={(e) => {
            if (e.target.files && e.target.files.length > 0) {
              handleFileSelect(e.target.files[0]);
            }
          }}
          accept=".pdf,.docx,.doc,.jpg,.jpeg,.png,.webp"
          className="hidden"
          disabled={isUploading}
        />

        {selectedFile ? (
          /* File Selected Card */
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3.5 rounded-lg bg-[#FBFCFC] border border-[#E0E5E9] max-w-md mx-auto text-left">
              <div className="flex items-center gap-3 min-w-0">
                <div className="p-2.5 rounded bg-white border border-[#E0E5E9] text-[#055B65] shrink-0">
                  <FileText className="w-5 h-5 text-[#055B65]" />
                </div>
                <div className="min-w-0">
                  <p className="text-sm font-semibold text-slate-900 truncate">
                    {selectedFile.name}
                  </p>
                  <p className="text-xs text-[#45828B] tabular-nums font-mono">
                    {formatFileSize(selectedFile.size)}
                  </p>
                </div>
              </div>

              {!isUploading && (
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedFile(null);
                    setErrorMessage(null);
                  }}
                  className="p-2 min-h-[36px] min-w-[36px] flex items-center justify-center rounded-lg text-slate-400 hover:text-slate-700 hover:bg-[#E0E5E9]/60 transition-colors cursor-pointer"
                  aria-label="Remove selected file"
                  title="Remove file"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>

            {/* Action buttons with clear hierarchy (Hick's & Fitts's law) */}
            <div className="flex flex-wrap items-center justify-center gap-3 pt-1">
              <button
                type="button"
                onClick={handleSubmit}
                disabled={isUploading}
                className="inline-flex items-center gap-2 px-5 py-2.5 min-h-[42px] rounded-lg bg-[#055B65] hover:bg-[#033c43] text-white text-sm font-semibold transition-colors disabled:opacity-60 cursor-pointer shadow-xs focus-visible:ring-2 focus-visible:ring-[#1BD488]"
              >
                {isUploading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin text-[#1BD488]" />
                    <span>Parsing resume...</span>
                  </>
                ) : (
                  <>
                    <span>Parse Resume</span>
                    <ArrowRight className="w-4 h-4 text-[#1BD488]" />
                  </>
                )}
              </button>

              {!isUploading && (
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="px-3.5 py-2 min-h-[40px] text-sm font-medium text-[#45828B] hover:text-[#055B65] transition-colors cursor-pointer"
                >
                  Choose another file
                </button>
              )}
            </div>

            {isUploading && (
              <div className="max-w-xs mx-auto pt-2" aria-live="polite">
                <div className="h-1.5 w-full bg-[#E0E5E9] rounded-full overflow-hidden">
                  <div className="h-full bg-[#1BD488] animate-pulse w-full" />
                </div>
                <p className="text-xs text-[#45828B] mt-2">
                  Extracting text and identifying entities...
                </p>
              </div>
            )}
          </div>
        ) : (
          /* Empty / Drop state */
          <div className="flex flex-col items-center justify-center space-y-3">
            <div className="p-3.5 rounded-full bg-[#055B65]/10 text-[#055B65]">
              <UploadCloud className="w-6 h-6 text-[#055B65]" />
            </div>

            <div className="space-y-1">
              <p className="text-sm font-medium text-slate-900">
                Drag and drop a resume, or{" "}
                <span className="text-[#055B65] font-semibold hover:underline">
                  browse files
                </span>
              </p>
              <p className="text-xs text-[#45828B]">
                Supports PDF, DOCX, and image formats up to 10 MB
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Error state with safe recovery (Error Prevention rule) */}
      {errorMessage && (
        <div
          role="alert"
          className="flex items-start justify-between gap-3 p-3.5 rounded-lg bg-rose-50 border border-rose-200 text-xs text-rose-800"
        >
          <div className="flex items-start gap-2 min-w-0">
            <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
            <p className="leading-relaxed">{errorMessage}</p>
          </div>
          <button
            onClick={() => setErrorMessage(null)}
            type="button"
            className="p-1 min-h-[32px] min-w-[32px] flex items-center justify-center text-rose-500 hover:text-rose-700 rounded"
            aria-label="Dismiss error"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      )}
    </div>
  );
}
