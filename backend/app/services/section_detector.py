import re

SECTION_HEADINGS: dict[str, list[str]] = {
    "summary": [
        "summary", "professional summary", "objective", "profile",
        "about", "about me", "career objective", "personal statement",
    ],
    "experience": [
        "experience", "work experience", "employment", "work history",
        "professional experience", "career history", "employment history",
    ],
    "education": [
        "education", "academic", "qualification", "qualifications",
        "academic background", "educational background",
    ],
    "skills": [
        "skills", "technical skills", "core competencies", "technologies",
        "tech stack", "competencies", "areas of expertise", "technical proficiencies",
    ],
    "certifications": [
        "certifications", "certificates", "licenses", "credentials",
        "professional certifications", "accreditations",
    ],
    "projects": [
        "projects", "personal projects", "portfolio", "key projects",
        "selected projects", "notable projects",
    ],
    "languages": [
        "languages", "language skills", "language proficiency",
    ],
}

# Flatten for fast lookup: normalized heading text -> section key
_HEADING_LOOKUP: dict[str, str] = {}
for section_key, headings in SECTION_HEADINGS.items():
    for h in headings:
        _HEADING_LOOKUP[h] = section_key


def _normalize_heading(line: str) -> str | None:
    """Check if a line is a section heading. Return the section key or None."""
    # Strip trailing colons, dashes, pipes, and whitespace
    candidate = re.sub(r'[\s:|\-–—]+$', '', line).strip().lower()
    # Remove leading bullet/number markers
    candidate = re.sub(r'^[\d.)\-•●○▪]+\s*', '', candidate).strip()
    return _HEADING_LOOKUP.get(candidate)


def detect_sections(text: str) -> dict[str, str]:
    """Split resume text into labeled sections based on heading detection.

    Text before the first recognized heading goes into 'personal_info'.
    Unrecognized headings are appended to the preceding section.
    """
    lines = text.split("\n")

    sections: dict[str, list[str]] = {
        "personal_info": [],
        "summary": [],
        "experience": [],
        "education": [],
        "skills": [],
        "certifications": [],
        "projects": [],
        "languages": [],
        "other": [],
    }

    current_section = "personal_info"

    for line in lines:
        stripped = line.strip()
        if not stripped:
            sections[current_section].append("")
            continue

        detected = _normalize_heading(stripped)
        if detected is not None:
            current_section = detected
            continue

        sections[current_section].append(line)

    # Join and strip each section
    result: dict[str, str] = {}
    for key, content_lines in sections.items():
        joined = "\n".join(content_lines).strip()
        if joined:
            result[key] = joined

    return result
