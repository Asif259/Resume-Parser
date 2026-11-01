import re
from pathlib import Path
from typing import List, Tuple, Union
from tests.evaluation.ground_truth import GroundTruth

def convert_to_bio(text: str, ground_truth: GroundTruth) -> List[Tuple[str, str]]:
    """Converts raw text and expected GroundTruth resume entities into BIO-tagged token sequence."""
    if not text:
        return []

    # 1. Collect entity values and target tags
    entities_to_find: List[Tuple[str, str]] = []
    exp = ground_truth.expected

    if exp.personal_info.name:
        entities_to_find.append((exp.personal_info.name, "PERSON_NAME"))
    if exp.personal_info.email:
        entities_to_find.append((str(exp.personal_info.email), "EMAIL"))
    if exp.personal_info.phone:
        entities_to_find.append((exp.personal_info.phone, "PHONE"))
    if exp.personal_info.location:
        entities_to_find.append((exp.personal_info.location, "LOCATION"))

    for item in exp.experience:
        if item.job_title:
            entities_to_find.append((item.job_title, "JOB_TITLE"))
        if item.company:
            entities_to_find.append((item.company, "COMPANY"))

    for item in exp.education:
        if item.degree:
            entities_to_find.append((item.degree, "DEGREE"))
        if item.institution:
            entities_to_find.append((item.institution, "INSTITUTION"))

    for skill in exp.skills:
        if skill:
            entities_to_find.append((skill, "SKILL"))

    for cert in exp.certifications:
        if cert.name:
            entities_to_find.append((cert.name, "CERT_NAME"))

    # Sort target entities by length descending to match longer multi-word phrases first
    entities_to_find.sort(key=lambda x: len(x[0]), reverse=True)

    # 2. Tokenize text into (token_str, start_char, end_char)
    token_matches = list(re.finditer(r'\S+', text))
    tags: List[str] = ["O"] * len(token_matches)
    occupied = [False] * len(token_matches)

    # 3. Label matching spans
    for target_val, entity_tag in entities_to_find:
        escaped_val = re.escape(target_val)
        for span_match in re.finditer(escaped_val, text, flags=re.IGNORECASE):
            s_start, s_end = span_match.start(), span_match.end()

            # Find matching tokens
            matched_indices = [
                idx for idx, tm in enumerate(token_matches)
                if tm.start() >= s_start and tm.end() <= s_end
            ]

            if matched_indices and not any(occupied[idx] for idx in matched_indices):
                for order, idx in enumerate(matched_indices):
                    occupied[idx] = True
                    prefix = "B-" if order == 0 else "I-"
                    tags[idx] = f"{prefix}{entity_tag}"

    return [(tm.group(0), tags[i]) for i, tm in enumerate(token_matches)]

def save_bio_file(bio_data: List[Tuple[str, str]], output_path: Union[str, Path]) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for token, tag in bio_data:
            f.write(f"{token}\t{tag}\n")

def load_bio_file(path: Union[str, Path]) -> List[Tuple[str, str]]:
    path = Path(path)
    results: List[Tuple[str, str]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) >= 2:
                results.append((parts[0], parts[1]))
    return results
