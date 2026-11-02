"use client";

import { useEffect, Suspense } from "react";
import { useParams, useRouter } from "next/navigation";
import { ResumeProfileSkeleton } from "@/components/skeleton-loader";

function RedirectHandler() {
  const params = useParams();
  const router = useRouter();
  const id = params?.id as string;

  useEffect(() => {
    if (id) {
      router.replace(`/resumes/${id}`);
    }
  }, [id, router]);

  return <ResumeProfileSkeleton />;
}

export default function ResultsPage() {
  return (
    <Suspense fallback={<ResumeProfileSkeleton />}>
      <RedirectHandler />
    </Suspense>
  );
}
