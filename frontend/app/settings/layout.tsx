import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "System Specifications & Health",
  description:
    "Inspection parameters, backend connection health, and machine learning pipeline specifications.",
};

export default function SettingsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}

