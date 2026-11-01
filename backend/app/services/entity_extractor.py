import re
from dataclasses import dataclass, field
from typing import Optional
import spacy
from app.schemas.evidence import FieldEvidence

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
    evidence: dict[str, FieldEvidence] = field(default_factory=dict)


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


DISALLOWED_NAME_WORDS = {
    "resume", "curriculum", "vitae", "cv", "profile", "summary",
    "experience", "education", "skills", "projects", "certifications",
    "languages", "contact", "email", "phone", "address", "page",
    "university", "college", "school", "institute", "technologies",
    "solutions", "inc", "llc", "corp", "corporation", "ltd", "limited",
    "engineer", "developer", "manager", "architect", "lead", "specialist",
    "analyst", "consultant", "director", "designer", "officer", "executive",
    "assistant", "intern", "associate", "senior", "junior", "principal",
    "work", "employment", "history", "professional",
}

def _validate_candidate_name(name: str) -> float:
    """Scores a candidate name string between 0.0 and 1.0. 0.0 means invalid."""
    if not name:
        return 0.0
    clean = name.strip()
    words = clean.split()
    if len(words) < 2 or len(words) > 4:
        return 0.0

    lower_words = [w.lower().rstrip(".,;:") for w in words]
    for w in lower_words:
        if w in DISALLOWED_NAME_WORDS:
            return 0.0
        if not w.isalpha() and "-" not in w:
            return 0.0

    title_words = sum(1 for w in words if w[0].isupper())
    score = 0.5 + (0.5 * (title_words / len(words)))
    if len(words) == 2:
        score += 0.1
    return min(1.0, score)

def _extract_name(text: str, email: Optional[str], phone: Optional[str]) -> Optional[str]:
    """Extract name from personal_info section using spaCy PERSON entities with validation,
    falling back to line-based heuristics."""
    if not text:
        return None

    # Step 1: Check spaCy PERSON entities
    doc = _nlp(text)
    best_candidate = None
    best_score = 0.0

    for ent in doc.ents:
        if ent.label_ == "PERSON":
            score = _validate_candidate_name(ent.text)
            if score > best_score:
                best_score = score
                best_candidate = ent.text.strip()

    if best_candidate and best_score >= 0.5:
        return best_candidate

    # Step 2: Line-based candidate search
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    for line in lines[:5]:
        if email and email in line:
            continue
        if phone and phone in line:
            continue
        if re.search(r'https?://|www\.|@|linkedin|github', line, re.IGNORECASE):
            continue
        if re.search(r'^\+?\d[\d\s\-().]{5,}$', line):
            continue

        # If line contains delimiters like '|', take the first segment
        candidate = re.split(r'[|•·,]', line)[0].strip()
        score = _validate_candidate_name(candidate)
        if score > 0.0:
            return candidate

    # Step 3: Fallback to first non-contact line
    for line in lines:
        if email and email in line:
            continue
        if phone and phone in line:
            continue
        if re.search(r'https?://|www\.|@|linkedin|github', line, re.IGNORECASE):
            continue
        if re.search(r'^\+?\d[\d\s\-().]{5,}$', line):
            continue
        # Avoid obvious section header words in fallback
        lower_line = line.lower()
        if any(h in lower_line for h in ["curriculum", "vitae", "resume", "experience", "education"]):
            continue
        return line

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

    # Record evidence
    if entities.name:
        entities.evidence["personal_info.name"] = FieldEvidence(
            value=entities.name,
            source_section="personal_info" if entities.name in personal else "all_text",
            source_text=personal[:300] if personal else entities.name,
            confidence=0.90,
        )
    if entities.email:
        entities.evidence["personal_info.email"] = FieldEvidence(
            value=entities.email,
            source_section="personal_info" if entities.email in personal else "all_text",
            source_text=entities.email,
            confidence=0.99,
        )
    if entities.phone:
        entities.evidence["personal_info.phone"] = FieldEvidence(
            value=entities.phone,
            source_section="personal_info" if entities.phone in personal else "all_text",
            source_text=entities.phone,
            confidence=0.90,
        )
    if entities.location:
        entities.evidence["personal_info.location"] = FieldEvidence(
            value=entities.location,
            source_section="personal_info" if entities.location in personal else "all_text",
            source_text=entities.location,
            confidence=0.85,
        )

    # LinkedIn / GitHub
    linkedin_match = LINKEDIN_PATTERN.search(all_text)
    github_match = GITHUB_PATTERN.search(all_text)
    entities.linkedin = linkedin_match.group(0) if linkedin_match else None
    entities.github = github_match.group(0) if github_match else None

    if entities.linkedin:
        entities.evidence["personal_info.linkedin"] = FieldEvidence(
            value=entities.linkedin,
            source_section="all_text",
            source_text=entities.linkedin,
            confidence=0.99,
        )
    if entities.github:
        entities.evidence["personal_info.github"] = FieldEvidence(
            value=entities.github,
            source_section="all_text",
            source_text=entities.github,
            confidence=0.99,
        )

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

