"use client";

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { uploadAndParseResume } from "@/lib/api";
import { UploadCloud, FileText, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";

const ALLOWED_EXTENSIONS = ["pdf", "docx", "doc", "jpg", "jpeg", "png"];
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
      return `Invalid format .${ext}. Allowed formats: ${ALLOWED_EXTENSIONS.join(", ").toUpperCase()}`;
    }
    if (file.size > MAX_FILE_SIZE) {
      return `File exceeds maximum allowed size of 10 MB (${(file.size / (1024 * 1024)).toFixed(1)} MB)`;
    }
    return null;
  };

  const handleFile = async (file: File) => {
    setErrorMessage(null);
    const error = validateFile(file);
    if (error) {
      setErrorMessage(error);
      setSelectedFile(null);
      return;
    }

    setSelectedFile(file);
    setIsUploading(true);

    try {
      const result = await uploadAndParseResume(file);
      router.push(`/results/${result.id}`);
    } catch (err: any) {
      setErrorMessage(err.message || "An unexpected error occurred during parsing");
      setIsUploading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFile(e.dataTransfer.files[0]);
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

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => !isUploading && fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-3xl p-8 sm:p-12 text-center cursor-pointer transition-all ${
          isDragging
            ? "border-blue-500 bg-blue-50/60 scale-[1.01]"
            : "border-gray-300 hover:border-gray-400 bg-white"
        } ${isUploading ? "pointer-events-none opacity-80" : ""}`}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={(e) => {
            if (e.target.files && e.target.files.length > 0) {
              handleFile(e.target.files[0]);
            }
          }}
          accept=".pdf,.docx,.doc,.jpg,.jpeg,.png"
          className="hidden"
        />

        <div className="flex flex-col items-center justify-center space-y-4">
          <div className="w-16 h-16 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center">
            {isUploading ? (
              <Loader2 className="w-8 h-8 animate-spin" />
            ) : (
              <UploadCloud className="w-8 h-8" />
            )}
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              {isUploading
                ? "Analyzing & extracting structured resume data..."
                : selectedFile
                ? selectedFile.name
                : "Upload your resume"}
            </h3>
            <p className="text-sm text-gray-500 mt-1">
              Drag and drop your document here, or{" "}
              <span className="text-blue-600 font-medium hover:underline">
                browse files
              </span>
            </p>
          </div>

          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-gray-50 border border-gray-200/80 text-xs text-gray-500 font-medium">
            <span>PDF, DOCX, JPG or PNG</span>
            <span>•</span>
            <span>Max 10 MB</span>
          </div>
        </div>
      </div>

      {errorMessage && (
        <div className="mt-4 flex items-center gap-2 p-4 rounded-xl bg-red-50 text-red-700 text-sm border border-red-200">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}
    </div>
  );
}
