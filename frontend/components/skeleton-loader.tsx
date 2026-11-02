"use client";

export function ResumeProfileSkeleton() {
  return (
    <div className="space-y-6 animate-pulse" aria-busy="true" aria-label="Loading resume details">
      {/* Top Header & Actions Skeleton */}
      <div className="flex items-center justify-between pb-2">
        <div className="h-4 w-40 bg-slate-200 rounded" />
        <div className="h-8 w-28 bg-slate-200 rounded-lg" />
      </div>

      {/* Main Profile Canvas Skeleton */}
      <div className="rounded-xl border border-slate-200 bg-white p-6 sm:p-8 space-y-6">
        {/* Candidate Meta Header */}
        <div className="space-y-3 pb-6 border-b border-slate-100">
          <div className="flex items-center justify-between">
            <div className="h-7 w-64 bg-slate-200 rounded" />
            <div className="h-6 w-24 bg-slate-100 rounded-full" />
          </div>
          <div className="flex flex-wrap gap-3 pt-1">
            <div className="h-4 w-36 bg-slate-100 rounded" />
            <div className="h-4 w-28 bg-slate-100 rounded" />
            <div className="h-4 w-32 bg-slate-100 rounded" />
          </div>
        </div>

        {/* 2-Column Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Main Column */}
          <div className="lg:col-span-8 space-y-8">
            {/* Summary */}
            <div className="space-y-2">
              <div className="h-4 w-28 bg-slate-200 rounded" />
              <div className="space-y-1.5 pt-1">
                <div className="h-3.5 w-full bg-slate-100 rounded" />
                <div className="h-3.5 w-11/12 bg-slate-100 rounded" />
                <div className="h-3.5 w-4/5 bg-slate-100 rounded" />
              </div>
            </div>

            {/* Experience Timeline */}
            <div className="space-y-4">
              <div className="h-4 w-36 bg-slate-200 rounded" />
              <div className="pl-6 space-y-6">
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <div className="h-4 w-48 bg-slate-200 rounded" />
                    <div className="h-3.5 w-28 bg-slate-100 rounded" />
                  </div>
                  <div className="h-3 w-32 bg-slate-100 rounded" />
                  <div className="space-y-1 pt-1">
                    <div className="h-3 w-full bg-slate-100 rounded" />
                    <div className="h-3 w-5/6 bg-slate-100 rounded" />
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <div className="h-4 w-40 bg-slate-200 rounded" />
                    <div className="h-3.5 w-24 bg-slate-100 rounded" />
                  </div>
                  <div className="h-3 w-28 bg-slate-100 rounded" />
                  <div className="space-y-1 pt-1">
                    <div className="h-3 w-full bg-slate-100 rounded" />
                  </div>
                </div>
              </div>
            </div>

            {/* Education */}
            <div className="space-y-3">
              <div className="h-4 w-24 bg-slate-200 rounded" />
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="h-20 bg-slate-50 border border-slate-100 rounded-lg p-3 space-y-2">
                  <div className="h-3.5 w-3/4 bg-slate-200 rounded" />
                  <div className="h-3 w-1/2 bg-slate-100 rounded" />
                </div>
                <div className="h-20 bg-slate-50 border border-slate-100 rounded-lg p-3 space-y-2">
                  <div className="h-3.5 w-3/4 bg-slate-200 rounded" />
                  <div className="h-3 w-1/2 bg-slate-100 rounded" />
                </div>
              </div>
            </div>
          </div>

          {/* Sidebar Column */}
          <div className="lg:col-span-4 space-y-6">
            <div className="p-4 rounded-lg bg-slate-50 border border-slate-200/80 space-y-3">
              <div className="h-4 w-28 bg-slate-200 rounded" />
              <div className="h-3 w-full bg-slate-100 rounded" />
              <div className="h-8 w-full bg-slate-200 rounded" />
            </div>

            <div className="space-y-3">
              <div className="h-4 w-20 bg-slate-200 rounded" />
              <div className="flex flex-wrap gap-1.5">
                {Array.from({ length: 8 }).map((_, i) => (
                  <div key={i} className="h-6 w-16 bg-slate-100 rounded-md" />
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

