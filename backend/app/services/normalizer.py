import re
from typing import Optional

from app.schemas.resume import (
    PersonalInfo,
    Experience,
    Education,
    Certification,
    Project,
    ParsedResume,
)
from app.services.entity_extractor import ExtractedEntities
from app.services.information_grouper import GroupedInfo

MONTH_MAP = {
    "jan": "01", "january": "01",
    "feb": "02", "february": "02",
    "mar": "03", "march": "03",
    "apr": "04", "april": "04",
    "may": "05",
    "jun": "06", "june": "06",
    "jul": "07", "july": "07",
    "aug": "08", "august": "08",
    "sep": "09", "september": "09",
    "oct": "10", "october": "10",
    "nov": "11", "november": "11",
    "dec": "12", "december": "12",
}

MONTH_YEAR_REGEX = re.compile(
    r'\b([A-Za-z]+)\.?\s+((?:19|20)\d{2})\b'
)
YEAR_ONLY_REGEX = re.compile(
    r'^\s*((?:19|20)\d{2})\s*$'
)

def normalize_date(date_str: Optional[str]) -> Optional[str]:
    """Standardizes date strings to YYYY-MM or YYYY format.
    'Present' or 'Current' returns None.
    """
    if not date_str:
        return None

    clean = date_str.strip()
    if clean.lower() in ("present", "current", "now", "ongoing"):
        return None

    year_match = YEAR_ONLY_REGEX.match(clean)
    if year_match:
        return year_match.group(1)

    my_match = MONTH_YEAR_REGEX.search(clean)
    if my_match:
        month_name = my_match.group(1).lower()
        year = my_match.group(2)
        month_num = MONTH_MAP.get(month_name)
        if month_num:
            return f"{year}-{month_num}"

    return clean

def normalize_phone(phone_str: Optional[str]) -> Optional[str]:
    """Cleans excess whitespace and symbols from phone numbers."""
    if not phone_str:
        return None
    return re.sub(r'\s+', ' ', phone_str).strip()

def _parse_certifications(cert_text: str) -> list[Certification]:
    certs = []
    lines = [line.strip() for line in cert_text.split("\n") if line.strip()]
    for line in lines:
        # Check for 'Name (Issuer, Date)' or 'Name - Issuer'
        match = re.match(r'^(.+?)(?:\s*\(([^)]+)\)|\s*[-–—]\s*(.+))?$', line)
        if match:
            name = match.group(1).strip()
            details = match.group(2) or match.group(3)
            issuer = None
            date = None
            if details:
                parts = [p.strip() for p in details.split(",")]
                if len(parts) >= 2:
                    issuer = parts[0]
                    date = parts[1]
                else:
                    # Check if details is a year or an issuer
                    if re.match(r'^(?:19|20)\d{2}$', details.strip()):
                        date = details.strip()
                    else:
                        issuer = details.strip()
            certs.append(Certification(name=name, issuer=issuer, date=date))
        else:
            certs.append(Certification(name=line))
    return certs

def _parse_projects(proj_text: str) -> list[Project]:
    projects = []
    lines = [line.strip() for line in proj_text.split("\n") if line.strip()]
    for line in lines:
        if ":" in line:
            parts = line.split(":", 1)
            name = parts[0].strip()
            desc = parts[1].strip()
            projects.append(Project(name=name, description=desc))
        elif "-" in line:
            parts = line.split("-", 1)
            name = parts[0].strip()
            desc = parts[1].strip()
            projects.append(Project(name=name, description=desc))
        else:
            projects.append(Project(name=line))
    return projects

def _parse_languages(lang_text: str) -> list[str]:
    languages = []
    tokens = re.split(r'[,|;\n]+', lang_text)
    for tok in tokens:
        clean = tok.strip()
        if clean:
            languages.append(clean)
    return languages

def normalize(
    sections: dict[str, str],
    entities: ExtractedEntities,
    grouped: GroupedInfo,
    skills: list[str],
    raw_text: Optional[str] = None,
) -> ParsedResume:
    """Assembles all extracted, categorized, and grouped data into a validated ParsedResume."""

    # 1. Personal Info
    personal_info = PersonalInfo(
        name=entities.name,
        email=entities.email if entities.email else None,
        phone=normalize_phone(entities.phone),
        location=entities.location,
        linkedin=entities.linkedin,
        github=entities.github,
    )

    # 2. Summary
    summary = sections.get("summary")

    # 3. Work Experience
    experience_list: list[Experience] = []
    for exp in grouped.experience:
        experience_list.append(
            Experience(
                job_title=exp.get("job_title"),
                company=exp.get("company"),
                start_date=normalize_date(exp.get("start_date")),
                end_date=normalize_date(exp.get("end_date")),
                description=exp.get("description", []),
            )
        )

    # 4. Education
    education_list: list[Education] = []
    for edu in grouped.education:
        education_list.append(
            Education(
                degree=edu.get("degree"),
                institution=edu.get("institution"),
                graduation_year=edu.get("graduation_year"),
                field_of_study=edu.get("field_of_study"),
            )
        )

    # 5. Certifications
    cert_text = sections.get("certifications", "")
    certifications = _parse_certifications(cert_text) if cert_text else []

    # 6. Projects
    proj_text = sections.get("projects", "")
    projects = _parse_projects(proj_text) if proj_text else []

    # 7. Languages
    lang_text = sections.get("languages", "")
    languages = _parse_languages(lang_text) if lang_text else []

    return ParsedResume(
        personal_info=personal_info,
        professional_summary=summary,
        skills=skills,
        experience=experience_list,
        education=education_list,
        certifications=certifications,
        projects=projects,
        languages=languages,
        raw_text=raw_text,
    )
