"use client";

import { Experience, FieldEvidence } from "@/types/resume";
import { ExperienceTimelineCard } from "@/components/experience-timeline";

interface ExperienceCardProps {
  experience: Experience;
  evidence?: Record<string, FieldEvidence> | null;
  index?: number;
}

export function ExperienceCard({ experience, evidence, index = 0 }: ExperienceCardProps) {
  return (
    <ExperienceTimelineCard
      experience={experience}
      index={index}
      evidence={evidence}
    />
  );
}
