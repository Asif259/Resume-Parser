"use client";

import { useState, useMemo } from "react";
import { Search, X } from "lucide-react";
import { ProvenanceTooltip } from "@/components/provenance-tooltip";
import { FieldEvidence } from "@/types/resume";

interface SkillBadgesProps {
  skills: string[];
  evidence?: Record<string, FieldEvidence> | null;
  className?: string;
}

type SkillCategory = "All" | "Languages" | "Frameworks" | "Cloud" | "Data" | "Tools";

const CATEGORY_DEFINITIONS: Record<Exclude<SkillCategory, "All">, RegExp> = {
  Languages: /^(python|javascript|typescript|js|ts|java|c\+\+|c#|c|golang|go|rust|ruby|php|swift|kotlin|scala|r|dart|perl|html|css|sql|bash|shell)$/i,
  Frameworks: /^(react|next\.?js|vue|angular|svelte|node\.?js|express|django|fastapi|flask|spring|rails|laravel|tailwind|bootstrap|pytorch|tensorflow|keras|scikit-learn|pandas|numpy)$/i,
  Cloud: /^(aws|azure|gcp|google cloud|docker|kubernetes|k8s|terraform|ci\/cd|github actions|gitlab ci|jenkins|ansible|linux|nginx|vercel|devops|serverless)$/i,
  Data: /^(postgresql|postgres|mysql|sqlite|mongodb|redis|elasticsearch|snowflake|bigquery|kafka|spark|hadoop|dynamodb|graphql|etl|data pipeline|data modeling)$/i,
  Tools: /^(git|jira|confluence|figma|postman|rest|restful|microservices|agile|scrum|system design|ci|cd|unit testing|pytest|jest)$/i,
};

export function SkillBadges({ skills, evidence, className = "" }: SkillBadgesProps) {
  const [activeCategory, setActiveCategory] = useState<SkillCategory>("All");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedSkills, setSelectedSkills] = useState<Set<string>>(new Set());

  const categorizedSkills = useMemo(() => {
    const groups: Record<Exclude<SkillCategory, "All">, string[]> = {
      Languages: [],
      Frameworks: [],
      Cloud: [],
      Data: [],
      Tools: [],
    };

    const uniqueSkills = Array.from(new Set(skills.map((s) => s.trim()).filter(Boolean)));

    uniqueSkills.forEach((skill) => {
      let matched = false;
      for (const [category, regex] of Object.entries(CATEGORY_DEFINITIONS) as [
        Exclude<SkillCategory, "All">,
        RegExp
      ][]) {
        if (regex.test(skill)) {
          groups[category].push(skill);
          matched = true;
          break;
        }
      }
      if (!matched) {
        const lower = skill.toLowerCase();
        if (lower.includes("sql") || lower.includes("db") || lower.includes("data")) {
          groups.Data.push(skill);
        } else if (lower.includes("cloud") || lower.includes("ops") || lower.includes("infra")) {
          groups.Cloud.push(skill);
        } else if (lower.includes("react") || lower.includes("framework") || lower.includes("api")) {
          groups.Frameworks.push(skill);
        } else {
          groups.Tools.push(skill);
        }
      }
    });

    return groups;
  }, [skills]);

  const filteredSkills = useMemo(() => {
    const list =
      activeCategory === "All"
        ? Array.from(new Set(skills.map((s) => s.trim()).filter(Boolean)))
        : categorizedSkills[activeCategory];

    if (!searchQuery.trim()) return list;
    return list.filter((s) =>
      s.toLowerCase().includes(searchQuery.toLowerCase().trim())
    );
  }, [skills, categorizedSkills, activeCategory, searchQuery]);

  const toggleSelectSkill = (skill: string) => {
    setSelectedSkills((prev) => {
      const next = new Set(prev);
      if (next.has(skill)) {
        next.delete(skill);
      } else {
        next.add(skill);
      }
      return next;
    });
  };

  const categories: { label: SkillCategory; count: number }[] = [
    { label: "All", count: skills.length },
    { label: "Languages", count: categorizedSkills.Languages.length },
    { label: "Frameworks", count: categorizedSkills.Frameworks.length },
    { label: "Cloud", count: categorizedSkills.Cloud.length },
    { label: "Data", count: categorizedSkills.Data.length },
    { label: "Tools", count: categorizedSkills.Tools.length },
  ];

  if (!skills || skills.length === 0) {
    return (
      <p className="text-xs text-slate-500 italic py-2">
        No skills identified in document.
      </p>
    );
  }

  return (
    <div className={`space-y-3 ${className}`}>
      {/* Category Tabs and Filter Input */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div className="flex flex-wrap items-center gap-1" role="tablist" aria-label="Skill categories">
          {categories.map(({ label, count }) => {
            if (label !== "All" && count === 0) return null;
            const isActive = activeCategory === label;
            return (
              <button
                key={label}
                role="tab"
                aria-selected={isActive}
                onClick={() => setActiveCategory(label)}
                className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded text-xs font-medium transition-colors cursor-pointer min-h-[30px] ${
                  isActive
                    ? "bg-[#055B65] text-white shadow-2xs"
                    : "bg-[#E0E5E9]/50 text-[#055B65] hover:bg-[#E0E5E9]"
                }`}
              >
                <span>{label}</span>
                <span
                  className={`text-[10px] tabular-nums font-mono px-1 rounded ${
                    isActive
                      ? "bg-[#1BD488] text-[#033c43] font-bold"
                      : "bg-[#B2C9C5]/30 text-[#055B65]"
                  }`}
                >
                  {count}
                </span>
              </button>
            );
          })}
        </div>

        {/* Search bar with clear button */}
        <div className="relative w-full sm:w-48">
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            type="text"
            placeholder="Filter skills..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            aria-label="Filter skills by keyword"
            className="w-full pl-8 pr-7 py-1 text-xs rounded border border-[#E0E5E9] bg-white placeholder:text-slate-400 focus:outline-none focus:ring-1 focus:ring-[#055B65] focus:border-[#055B65]"
          />
          {searchQuery && (
            <button
              type="button"
              onClick={() => setSearchQuery("")}
              className="absolute right-1.5 top-1/2 -translate-y-1/2 p-0.5 rounded text-slate-400 hover:text-slate-600"
              aria-label="Clear skill search"
            >
              <X className="w-3 h-3" />
            </button>
          )}
        </div>
      </div>

      {/* Skill Pills */}
      <div className="flex flex-wrap gap-1.5 pt-1">
        {filteredSkills.map((skill, index) => {
          const isSelected = selectedSkills.has(skill);
          const skillEvidence =
            evidence?.[`skills.${skill}`] ||
            evidence?.[`skill_${skill}`] ||
            evidence?.["skills"];

          return (
            <ProvenanceTooltip
              key={`${skill}-${index}`}
              evidence={skillEvidence}
              fieldName={skill}
            >
              <button
                type="button"
                onClick={() => toggleSelectSkill(skill)}
                className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded text-xs font-medium border transition-colors cursor-pointer min-h-[28px] ${
                  isSelected
                    ? "bg-[#055B65]/10 border-[#055B65] text-[#055B65] font-semibold"
                    : "bg-white border-[#E0E5E9] text-slate-800 hover:bg-[#FBFCFC] hover:border-[#B2C9C5] hover:text-[#055B65]"
                }`}
              >
                <span>{skill}</span>
              </button>
            </ProvenanceTooltip>
          );
        })}
      </div>

      {filteredSkills.length === 0 && (
        <div className="flex items-center justify-between text-xs text-[#45828B] py-2">
          <p className="italic">
            No skills found matching &ldquo;{searchQuery}&rdquo;.
          </p>
          <button
            type="button"
            onClick={() => setSearchQuery("")}
            className="text-[#055B65] hover:underline font-semibold ml-2 cursor-pointer"
          >
            Clear filter
          </button>
        </div>
      )}
    </div>
  );
}
