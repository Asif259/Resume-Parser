import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Candidate Library",
  description:
    "Browse, filter, search, and audit all extracted resume dossiers, skill taxonomies, and calibrated confidence ratings.",
};

export default function ResumesLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}

