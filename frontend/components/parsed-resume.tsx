"use client";

import { useState } from "react";
import { ParsedResume } from "@/types/resume";
import { SkillBadges } from "@/components/skill-badges";
import { ExperienceCard } from "@/components/experience-card";
import {
  Mail,
  Phone,
  MapPin,
  GraduationCap,
  Award,
  Code,
  Globe,
  FileText,
  ChevronDown,
  ChevronUp,
} from "lucide-react";

interface ParsedResumeViewProps {
  resume: ParsedResume;
  filename?: string;
}

export function ParsedResumeView({ resume, filename }: ParsedResumeViewProps) {
  const [showRaw, setShowRaw] = useState(false);
  const { personal_info, professional_summary, skills, experience, education, certifications, projects, languages } = resume;

  return (
    <div className="space-y-6">
      {/* Header Profile Card */}
      <div className="bg-white rounded-2xl border border-gray-200/80 p-6 sm:p-8 shadow-sm">
        <div className="border-b border-gray-100 pb-6 mb-6">
          <span className="text-xs font-semibold tracking-wider uppercase text-blue-600 bg-blue-50 px-2.5 py-1 rounded-full">
            Candidate Profile
          </span>
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 mt-2">
            {personal_info.name || "Unnamed Candidate"}
          </h1>
          <div className="flex items-center gap-3 mt-1">
            {filename && (
              <p className="text-xs text-gray-400">Parsed from: {filename}</p>
            )}
            {resume.evidence && (
              <span className="text-[11px] font-medium text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-100">
                Provenance tracked ({Object.keys(resume.evidence).length} fields)
              </span>
            )}
          </div>

          {/* Contact Details */}
          <div className="flex flex-wrap items-center gap-y-2 gap-x-6 mt-4 text-sm text-gray-600">
            {personal_info.email && (
              <a
                href={`mailto:${personal_info.email}`}
                className="flex items-center gap-1.5 hover:text-blue-600 transition"
              >
                <Mail className="w-4 h-4 text-gray-400" />
                <span>{personal_info.email}</span>
              </a>
            )}
            {personal_info.phone && (
              <div className="flex items-center gap-1.5">
                <Phone className="w-4 h-4 text-gray-400" />
                <span>{personal_info.phone}</span>
              </div>
            )}
            {personal_info.location && (
              <div className="flex items-center gap-1.5">
                <MapPin className="w-4 h-4 text-gray-400" />
                <span>{personal_info.location}</span>
              </div>
            )}
            {personal_info.linkedin && (
              <a
                href={personal_info.linkedin.startsWith("http") ? personal_info.linkedin : `https://${personal_info.linkedin}`}
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-1.5 text-blue-600 hover:underline"
              >
                <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24">
                  <path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.28 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.75M6.46 10.9v8.37H9.2V10.9H6.46M7.83 6.45c-.88 0-1.6.72-1.6 1.6 0 .88.72 1.6 1.6 1.6.88 0 1.6-.72 1.6-1.6 0-.88-.72-1.6-1.6-1.6Z"/>
                </svg>
                <span>LinkedIn</span>
              </a>
            )}
            {personal_info.github && (
              <a
                href={personal_info.github.startsWith("http") ? personal_info.github : `https://${personal_info.github}`}
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-1.5 text-gray-800 hover:text-black"
              >
                <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24">
                  <path d="M12 2A10 10 0 0 0 2 12c0 4.42 2.87 8.17 6.84 9.5.5.08.66-.23.66-.5v-1.69c-2.77.6-3.36-1.34-3.36-1.34-.46-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.6.07-.6 1 .07 1.53 1.03 1.53 1.03.87 1.52 2.34 1.07 2.91.83.1-.65.35-1.09.63-1.34-2.22-.25-4.55-1.11-4.55-4.92 0-1.11.38-2 1.03-2.71-.1-.25-.45-1.29.1-2.64 0 0 .84-.27 2.75 1.02.79-.22 1.65-.33 2.5-.33.85 0 1.71.11 2.5.33 1.91-1.29 2.75-1.02 2.75-1.02.55 1.35.2 2.39.1 2.64.65.71 1.03 1.6 1.03 2.71 0 3.82-2.34 4.66-4.57 4.91.36.31.69.92.69 1.85V21c0 .27.16.59.67.5C19.14 20.16 22 16.42 22 12A10 10 0 0 0 12 2Z"/>
                </svg>
                <span>GitHub</span>
              </a>
            )}
          </div>
        </div>

        {/* Summary */}
        {professional_summary && (
          <div>
            <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-500 mb-2">
              Professional Summary
            </h3>
            <p className="text-gray-700 leading-relaxed text-sm sm:text-base">
              {professional_summary}
            </p>
          </div>
        )}
      </div>

      {/* Skills Section */}
      <div className="bg-white rounded-2xl border border-gray-200/80 p-6 sm:p-8 shadow-sm">
        <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <Code className="w-5 h-5 text-blue-600" />
          Extracted Skills ({skills.length})
        </h3>
        <SkillBadges skills={skills} />
      </div>

      {/* Work Experience */}
      {experience.length > 0 && (
        <div className="bg-white rounded-2xl border border-gray-200/80 p-6 sm:p-8 shadow-sm">
          <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
            <FileText className="w-5 h-5 text-blue-600" />
            Work Experience ({experience.length})
          </h3>
          <div className="space-y-4">
            {experience.map((exp, i) => (
              <ExperienceCard key={i} experience={exp} />
            ))}
          </div>
        </div>
      )}

      {/* Education */}
      {education.length > 0 && (
        <div className="bg-white rounded-2xl border border-gray-200/80 p-6 sm:p-8 shadow-sm">
          <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
            <GraduationCap className="w-5 h-5 text-blue-600" />
            Education ({education.length})
          </h3>
          <div className="grid gap-4 sm:grid-cols-2">
            {education.map((edu, i) => (
              <div
                key={i}
                className="border border-gray-100 rounded-xl p-4 bg-gray-50/50"
              >
                <h4 className="font-semibold text-gray-900 text-sm">
                  {edu.degree || "Degree"}
                </h4>
                {edu.institution && (
                  <p className="text-xs font-medium text-gray-600 mt-0.5">
                    {edu.institution}
                  </p>
                )}
                {edu.graduation_year && (
                  <p className="text-xs text-gray-500 mt-2">
                    Class of {edu.graduation_year}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Additional Details (Projects, Certifications, Languages) */}
      <div className="grid gap-6 md:grid-cols-3">
        {certifications.length > 0 && (
          <div className="bg-white rounded-2xl border border-gray-200/80 p-5 shadow-sm">
            <h4 className="font-bold text-gray-900 text-sm flex items-center gap-2 mb-3">
              <Award className="w-4 h-4 text-amber-500" />
              Certifications
            </h4>
            <ul className="space-y-2 text-xs text-gray-700">
              {certifications.map((c, i) => (
                <li key={i} className="border-b border-gray-50 pb-1.5 last:border-0">
                  <span className="font-medium">{c.name}</span>
                  {c.issuer && <span className="text-gray-500"> ({c.issuer})</span>}
                  {c.date && <span className="text-gray-400"> - {c.date}</span>}
                </li>
              ))}
            </ul>
          </div>
        )}

        {projects.length > 0 && (
          <div className="bg-white rounded-2xl border border-gray-200/80 p-5 shadow-sm">
            <h4 className="font-bold text-gray-900 text-sm flex items-center gap-2 mb-3">
              <Code className="w-4 h-4 text-emerald-500" />
              Projects
            </h4>
            <ul className="space-y-2 text-xs text-gray-700">
              {projects.map((p, i) => (
                <li key={i} className="border-b border-gray-50 pb-1.5 last:border-0">
                  <span className="font-medium text-gray-900">{p.name}</span>
                  {p.description && <p className="text-gray-600 mt-0.5">{p.description}</p>}
                </li>
              ))}
            </ul>
          </div>
        )}

        {languages.length > 0 && (
          <div className="bg-white rounded-2xl border border-gray-200/80 p-5 shadow-sm">
            <h4 className="font-bold text-gray-900 text-sm flex items-center gap-2 mb-3">
              <Globe className="w-4 h-4 text-purple-500" />
              Languages
            </h4>
            <div className="flex flex-wrap gap-1.5">
              {languages.map((l, i) => (
                <span
                  key={i}
                  className="px-2.5 py-0.5 rounded-full bg-purple-50 text-purple-700 text-xs font-medium border border-purple-100"
                >
                  {l}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Raw Extracted Text Accordion */}
      {resume.raw_text && (
        <div className="bg-white rounded-2xl border border-gray-200/80 p-6 shadow-sm">
          <button
            onClick={() => setShowRaw(!showRaw)}
            className="w-full flex items-center justify-between text-left text-sm font-semibold text-gray-700 hover:text-gray-900"
          >
            <span>Raw Extracted Source Text</span>
            {showRaw ? (
              <ChevronUp className="w-4 h-4 text-gray-500" />
            ) : (
              <ChevronDown className="w-4 h-4 text-gray-500" />
            )}
          </button>
          {showRaw && (
            <pre className="mt-4 p-4 rounded-xl bg-gray-50 text-xs text-gray-700 font-mono overflow-x-auto whitespace-pre-wrap max-h-96 border border-gray-200">
              {resume.raw_text}
            </pre>
          )}
        </div>
      )}
    </div>
  );
}
