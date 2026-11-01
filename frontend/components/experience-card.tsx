"use client";

import { Experience } from "@/types/resume";
import { Briefcase, Calendar } from "lucide-react";

interface ExperienceCardProps {
  experience: Experience;
}

export function ExperienceCard({ experience }: ExperienceCardProps) {
  const { job_title, company, start_date, end_date, description } = experience;

  const dateDisplay =
    start_date || end_date
      ? `${start_date || "Unknown"} — ${end_date || "Present"}`
      : null;

  return (
    <div className="border border-gray-100 rounded-xl p-4 bg-gray-50/50 hover:bg-white hover:shadow-md transition">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1 mb-2">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-blue-100/60 text-blue-700">
            <Briefcase className="w-4 h-4" />
          </div>
          <div>
            <h4 className="font-semibold text-gray-900 text-base">
              {job_title || "Untitled Role"}
            </h4>
            {company && <p className="text-sm font-medium text-gray-600">{company}</p>}
          </div>
        </div>

        {dateDisplay && (
          <div className="flex items-center gap-1.5 text-xs text-gray-500 font-medium">
            <Calendar className="w-3.5 h-3.5" />
            <span>{dateDisplay}</span>
          </div>
        )}
      </div>

      {description && description.length > 0 && (
        <ul className="mt-3 space-y-1.5 pl-4 list-disc text-sm text-gray-600">
          {description.map((item, idx) => (
            <li key={idx} className="leading-relaxed">
              {item}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
