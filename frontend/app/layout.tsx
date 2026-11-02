import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { AppShell } from "@/components/layout/app-shell";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
  display: "swap",
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000"),
  title: {
    default: "ResumeParser — AI-Powered Resume Intelligence",
    template: "%s | ResumeParser",
  },
  description:
    "Enterprise-grade resume extraction with hybrid NLP, custom NER, semantic skill matching, and calibrated provenance verification.",
  keywords: [
    "resume parser",
    "NLP resume parser",
    "DistilBERT NER",
    "resume intelligence",
    "skills extraction",
    "source provenance",
  ],
  authors: [{ name: "ResumeParser Engineering Team" }],
  openGraph: {
    title: "ResumeParser — AI-Powered Resume Intelligence",
    description:
      "Enterprise-grade resume extraction with hybrid NLP, custom NER, semantic skill matching, and calibrated provenance verification.",
    type: "website",
    locale: "en_US",
    siteName: "ResumeParser",
  },
  twitter: {
    card: "summary",
    title: "ResumeParser — AI-Powered Resume Intelligence",
    description:
      "Enterprise-grade resume extraction with hybrid NLP, custom NER, semantic skill matching, and calibrated provenance verification.",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col font-sans bg-[#FBFCFC] text-[#0a1b1e] selection:bg-[#1BD488]/30 selection:text-[#033c43]">
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
