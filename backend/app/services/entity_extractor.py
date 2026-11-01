import re
from dataclasses import dataclass, field
from typing import Optional
import spacy

# Load spaCy model once
_nlp = spacy.load("en_core_web_sm")

# ---- Regex Patterns ----

EMAIL_PATTERN = re.compile(r'[\w.+-]+@[\w-]+\.[\w.-]+')

PHONE_PATTERN = re.compile(
    r'[\+]?[(]?\d{1,4}[)]?[-\s./]?\d{1,5}[-\s./]?\d{1,5}[-\s./]?\d{0,5}'
)
# Stricter: must have at least 7 digits total
PHONE_MIN_DIGITS = 7

DATE_RANGE_PATTERN = re.compile(
    r'(?:(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|'
    r'Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)'
    r'\.?\s*\d{4}|(?:\d{4}))'
    r'\s*[-–—]\s*'
    r'(?:(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|'
    r'Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)'
    r'\.?\s*\d{4}|(?:\d{4})|[Pp]resent|[Cc]urrent)',
    re.IGNORECASE,
)

LINKEDIN_PATTERN = re.compile(r'(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+/?', re.IGNORECASE)
GITHUB_PATTERN = re.compile(r'(?:https?://)?(?:www\.)?github\.com/[\w-]+/?', re.IGNORECASE)


@dataclass
class ExtractedEntities:
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    job_titles: list[str] = field(default_factory=list)
    companies: list[str] = field(default_factory=list)
    dates: list[str] = field(default_factory=list)
    degrees: list[str] = field(default_factory=list)
    institutions: list[str] = field(default_factory=list)


def _extract_email(text: str) -> Optional[str]:
    match = EMAIL_PATTERN.search(text)
    return match.group(0) if match else None


def _extract_phone(text: str) -> Optional[str]:
    for match in PHONE_PATTERN.finditer(text):
        candidate = match.group(0).strip()
        digits_only = re.sub(r'\D', '', candidate)
        if len(digits_only) >= PHONE_MIN_DIGITS:
            return candidate
    return None


def _extract_name(text: str, email: Optional[str], phone: Optional[str]) -> Optional[str]:
    """Extract name from personal_info section using spaCy PERSON entities,
    falling back to the first non-contact line."""
    doc = _nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text.strip()

    # Fallback: first line that is not email/phone/url
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        if email and email in stripped:
            continue
        if phone and phone in stripped:
            continue
        if re.search(r'https?://|www\.|@|linkedin|github', stripped, re.IGNORECASE):
            continue
        if re.search(r'^\+?\d[\d\s\-().]{5,}$', stripped):
            continue
        # Likely a name line
        return stripped
    return None


def _extract_location(text: str, email: Optional[str], phone: Optional[str], name: Optional[str]) -> Optional[str]:
    doc = _nlp(text)
    for ent in doc.ents:
        if ent.label_ in ("GPE", "LOC"):
            return ent.text.strip()

    # Fallback: look for "City, Country" or "City, State" pattern in personal_info
    location_pattern = re.compile(r'[A-Z][a-zA-Z\s]+,\s*[A-Z][a-zA-Z\s]+')
    for line in text.split("\n"):
        stripped = line.strip()
        if email and email in stripped:
            # Check after pipe/bar separators
            parts = re.split(r'[|•·]', stripped)
            for part in parts:
                part = part.strip()
                if email in part or (phone and phone in part):
                    continue
                m = location_pattern.search(part)
                if m:
                    return m.group(0).strip()
        else:
            m = location_pattern.search(stripped)
            if m:
                return m.group(0).strip()
    return None


def extract_entities(sections: dict[str, str]) -> ExtractedEntities:
    """Extract named entities from resume sections using regex + spaCy."""
    entities = ExtractedEntities()
    all_text = "\n".join(sections.values())
    personal = sections.get("personal_info", "")

    # Contact info from personal_info section (fallback to all text)
    entities.email = _extract_email(personal) or _extract_email(all_text)
    entities.phone = _extract_phone(personal) or _extract_phone(all_text)
    entities.name = _extract_name(personal, entities.email, entities.phone)
    entities.location = _extract_location(personal, entities.email, entities.phone, entities.name)

    # LinkedIn / GitHub
    linkedin_match = LINKEDIN_PATTERN.search(all_text)
    github_match = GITHUB_PATTERN.search(all_text)
    entities.linkedin = linkedin_match.group(0) if linkedin_match else None
    entities.github = github_match.group(0) if github_match else None

    # Dates from experience and education sections
    for section_key in ("experience", "education"):
        section_text = sections.get(section_key, "")
        entities.dates.extend(DATE_RANGE_PATTERN.findall(section_text))

    # ORG entities from experience -> companies
    experience_text = sections.get("experience", "")
    if experience_text:
        doc = _nlp(experience_text)
        for ent in doc.ents:
            if ent.label_ == "ORG" and ent.text.strip() not in entities.companies:
                entities.companies.append(ent.text.strip())

    return entities
