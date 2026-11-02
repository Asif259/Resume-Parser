import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Candidate Profile Dossier",
  description:
    "Candidate profile review dashboard displaying extracted name, contact channels, summary, skill pills, work experience, and provenance evidence.",
};

export default function ResumeDetailLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}

