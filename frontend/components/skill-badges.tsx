"use client";

interface SkillBadgesProps {
  skills: string[];
}

export function SkillBadges({ skills }: SkillBadgesProps) {
  if (!skills || skills.length === 0) {
    return <p className="text-sm text-gray-500 italic">No skills extracted</p>;
  }

  return (
    <div className="flex flex-wrap gap-2">
      {skills.map((skill, i) => (
        <span
          key={`${skill}-${i}`}
          className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-50 text-blue-700 border border-blue-200 shadow-sm transition hover:bg-blue-100"
        >
          {skill}
        </span>
      ))}
    </div>
  );
}
