import re
from dataclasses import dataclass, field
from typing import Optional
from app.services.entity_extractor import ExtractedEntities

DATE_PATTERN = re.compile(
    r'(?:(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|'
    r'Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)'
    r'\.?\s*\d{4}|\d{4})'
    r'\s*[-–—]\s*'
    r'(?:(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|'
    r'Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)'
    r'\.?\s*\d{4}|\d{4}|[Pp]resent|[Cc]urrent)',
    re.IGNORECASE,
)

YEAR_ONLY_PATTERN = re.compile(r'\b((?:19|20)\d{2})\b')

# Common job title keywords for heuristic detection
JOB_TITLE_KEYWORDS = [
    "engineer", "developer", "manager", "director", "analyst", "designer",
    "architect", "consultant", "specialist", "coordinator", "administrator",
    "lead", "senior", "junior", "intern", "associate", "principal",
    "head", "chief", "officer", "president", "founder", "co-founder",
    "technician", "scientist", "researcher", "professor", "instructor",
]

DEGREE_KEYWORDS = [
    "bachelor", "master", "phd", "ph.d", "doctorate", "associate",
    "diploma", "certificate", "b.s.", "b.a.", "m.s.", "m.a.", "mba",
    "b.sc", "m.sc", "b.tech", "m.tech", "bsc", "msc",
]


@dataclass
class GroupedInfo:
    experience: list[dict] = field(default_factory=list)
    education: list[dict] = field(default_factory=list)


def _is_date_line(line: str) -> bool:
    return bool(DATE_PATTERN.search(line))


def _has_year(line: str) -> bool:
    return bool(YEAR_ONLY_PATTERN.search(line))


def _looks_like_job_title(line: str) -> bool:
    lower = line.lower()
    return any(kw in lower for kw in JOB_TITLE_KEYWORDS)


def _looks_like_degree(line: str) -> bool:
    lower = line.lower()
    return any(kw in lower for kw in DEGREE_KEYWORDS)


def _split_into_blocks(text: str) -> list[list[str]]:
    """Split section text into blocks separated by blank lines or date-line transitions."""
    raw_lines = text.split("\n")
    initial_blocks: list[list[str]] = []
    current_block: list[str] = []

    for line in raw_lines:
        stripped = line.strip()
        if not stripped:
            if current_block:
                initial_blocks.append(current_block)
                current_block = []
        else:
            current_block.append(stripped)

    if current_block:
        initial_blocks.append(current_block)

    # Sub-split blocks if multiple date lines are detected in a single block (compact formatting)
    final_blocks: list[list[str]] = []
    bullet_prefixes = ("-", "•", "*", "–", "—", "▪", "▫", "·")

    for block in initial_blocks:
        date_indices = [i for i, line in enumerate(block) if _is_date_line(line)]
        if len(date_indices) <= 1:
            final_blocks.append(block)
            continue

        # Split at boundaries between records
        split_points = [0]
        for d_idx in date_indices[1:]:
            # Scan backwards from d_idx to find non-bullet header lines (up to 2 lines)
            boundary = d_idx
            while boundary > split_points[-1]:
                prev_line = block[boundary - 1]
                if any(prev_line.startswith(p) for p in bullet_prefixes):
                    break
                boundary -= 1
                if d_idx - boundary >= 2:
                    break
            if boundary > split_points[-1]:
                split_points.append(boundary)

        split_points.append(len(block))
        for start, end in zip(split_points[:-1], split_points[1:]):
            sub_block = block[start:end]
            if sub_block:
                final_blocks.append(sub_block)

    return final_blocks

def _split_title_company(line: str) -> tuple[Optional[str], Optional[str]]:
    """Splits a single line into (title, company) using delimiters: pipe, bullet, 'at', or comma."""
    # 1. Pipe or bullet delimiter: "Title | Company"
    if re.search(r'\s*[|•·]\s*', line):
        parts = re.split(r'\s*[|•·]\s*', line, maxsplit=1)
        p0, p1 = parts[0].strip(), parts[1].strip()
        if _looks_like_job_title(p0):
            return p0, p1
        elif _looks_like_job_title(p1):
            return p1, p0
        return p0, p1

    # 2. "Title at Company"
    if re.search(r'\s+at\s+', line, re.IGNORECASE):
        parts = re.split(r'\s+at\s+', line, maxsplit=1, flags=re.IGNORECASE)
        return parts[0].strip(), parts[1].strip()

    # 3. "Title, Company"
    if re.search(r',\s+', line):
        parts = re.split(r',\s+', line, maxsplit=1)
        p0, p1 = parts[0].strip(), parts[1].strip()
        if _looks_like_job_title(p0):
            return p0, p1
        elif _looks_like_job_title(p1):
            return p1, p0
        return p0, p1

    return None, None


def _parse_experience_block(block: list[str]) -> dict:
    """Parse a block of lines into an experience record."""
    record: dict = {
        "job_title": None,
        "company": None,
        "start_date": None,
        "end_date": None,
        "description": [],
    }

    date_line_idx = None
    title_line_idx = None

    # Find date line and title line
    for i, line in enumerate(block):
        if _is_date_line(line):
            date_line_idx = i
            # Extract date range
            match = DATE_PATTERN.search(line)
            if match:
                date_str = match.group(0)
                parts = re.split(r'\s*[-–—]\s*', date_str, maxsplit=1)
                record["start_date"] = parts[0].strip() if parts else None
                record["end_date"] = parts[1].strip() if len(parts) > 1 else None
            break

    for i, line in enumerate(block):
        if i == date_line_idx:
            continue
        if _looks_like_job_title(line):
            title_line_idx = i
            t, c = _split_title_company(line)
            if t:
                record["job_title"] = t
                if c:
                    record["company"] = c
            else:
                record["job_title"] = line.strip()
            break

    # If no title found via keyword, use first non-date line as title
    if record["job_title"] is None:
        for i, line in enumerate(block):
            if i != date_line_idx:
                title_line_idx = i
                t, c = _split_title_company(line)
                if t:
                    record["job_title"] = t
                    if c:
                        record["company"] = c
                else:
                    record["job_title"] = line.strip()
                break

    # Company: next line after title if not already set
    if record["company"] is None:
        for i, line in enumerate(block):
            if i != date_line_idx and i != title_line_idx:
                if not _is_date_line(line):
                    record["company"] = line.strip()
                    break

    # Remaining lines after title, company, and date are description
    used_indices = {date_line_idx, title_line_idx}
    if record["company"]:
        for i, line in enumerate(block):
            if line.strip() == record["company"] and i not in used_indices:
                used_indices.add(i)
                break

    for i, line in enumerate(block):
        if i not in used_indices and not _is_date_line(line):
            record["description"].append(line.strip())

    return record


def _parse_education_block(block: list[str]) -> dict:
    """Parse a block of lines into an education record."""
    record: dict = {
        "degree": None,
        "institution": None,
        "graduation_year": None,
    }

    for i, line in enumerate(block):
        if _looks_like_degree(line):
            # May contain "Degree, Institution, Year" on one line
            parts = re.split(r',\s+', line)
            record["degree"] = parts[0].strip()
            if len(parts) > 1:
                # Check remaining parts for institution and year
                for part in parts[1:]:
                    year_match = YEAR_ONLY_PATTERN.search(part)
                    if year_match and record["graduation_year"] is None:
                        record["graduation_year"] = int(year_match.group(1))
                    elif record["institution"] is None:
                        record["institution"] = part.strip().rstrip(".")
            break

    # Look for year in remaining lines
    for line in block:
        if record["graduation_year"] is None:
            year_match = YEAR_ONLY_PATTERN.search(line)
            if year_match:
                record["graduation_year"] = int(year_match.group(1))

    # Look for institution in remaining lines
    if record["institution"] is None:
        for line in block:
            stripped = line.strip().rstrip(".")
            if stripped == record.get("degree"):
                continue
            if not _looks_like_degree(stripped) and not YEAR_ONLY_PATTERN.fullmatch(stripped):
                record["institution"] = stripped
                break

    # Fallback: if no degree detected, use first line
    if record["degree"] is None and block:
        record["degree"] = block[0].strip()

    return record


def group_information(sections: dict[str, str], entities: ExtractedEntities) -> GroupedInfo:
    """Group extracted entities and section text into structured experience and education records."""
    grouped = GroupedInfo()

    # Group experience
    exp_text = sections.get("experience", "")
    if exp_text:
        blocks = _split_into_blocks(exp_text)
        for block in blocks:
            record = _parse_experience_block(block)
            if record["job_title"] or record["company"]:
                grouped.experience.append(record)

    # Group education
    edu_text = sections.get("education", "")
    if edu_text:
        blocks = _split_into_blocks(edu_text)
        for block in blocks:
            record = _parse_education_block(block)
            if record["degree"] or record["institution"]:
                grouped.education.append(record)

    return grouped

