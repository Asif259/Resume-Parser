export interface PersonalInfo {
  name: string | null;
  email: string | null;
  phone: string | null;
  location: string | null;
  linkedin: string | null;
  github: string | null;
}

export interface Experience {
  job_title: string | null;
  company: string | null;
  start_date: string | null;
  end_date: string | null;
  is_current: boolean | null;
  description: string[];
}

export interface Education {
  degree: string | null;
  institution: string | null;
  graduation_year: number | null;
  field_of_study: string | null;
}

export interface Certification {
  name: string | null;
  issuer: string | null;
  date: string | null;
}

export interface Project {
  name: string | null;
  description: string | null;
  technologies: string[];
}

export type ExtractionMethod = "rules" | "ml" | "semantic" | "hybrid" | string;

export interface FieldEvidence {
  value: string;
  normalized_value: string | null;
  source_section: string;
  source_text: string;
  confidence: number;
  page: number | null;
  extraction_method?: ExtractionMethod | null;
  calibrated_confidence?: number | null;
}

export interface ParsedResume {
  personal_info: PersonalInfo;
  professional_summary: string | null;
  skills: string[];
  experience: Experience[];
  education: Education[];
  certifications: Certification[];
  projects: Project[];
  languages: string[];
  raw_text: string | null;
  evidence?: Record<string, FieldEvidence> | null;
  confidence_score?: number | null;
  low_confidence_fields?: string[];
}

export interface ParseResponse {
  id: string;
  filename: string;
  parsed_resume: ParsedResume;
  created_at: string;
}
