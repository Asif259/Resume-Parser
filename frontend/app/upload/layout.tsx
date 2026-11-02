import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Upload Resume",
  description:
    "Upload resume documents in PDF, DOCX, or image formats for automatic structured data extraction and provenance verification.",
};

export default function UploadLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}

