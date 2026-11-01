from pathlib import Path

from app.schemas.resume import ParsedResume
from app.services.pdf_extractor import extract_pdf
from app.services.docx_extractor import extract_docx
from app.services.ocr_extractor import extract_image, extract_pdf_ocr
from app.services.preprocessor import preprocess
from app.services.section_detector import detect_sections
from app.services.entity_extractor import extract_entities
from app.services.skill_extractor import extract_skills
from app.services.information_grouper import group_information
from app.services.normalizer import normalize

def parse_resume(file_path: Path, file_type: str) -> ParsedResume:
    """End-to-end orchestration pipeline:
    Document Extraction -> Preprocessing -> Section Detection ->
    Entity Extraction -> Skill Normalization -> Information Grouping ->
    Normalization & Validation.
    """
    file_type = file_type.lower().lstrip(".")

    # 1. Document Extraction
    if file_type == "pdf":
        extracted = extract_pdf(file_path)
        if extracted.method == "ocr_needed":
            extracted = extract_pdf_ocr(file_path)
    elif file_type in ("docx", "doc"):
        extracted = extract_docx(file_path)
    elif file_type in ("jpg", "jpeg", "png"):
        extracted = extract_image(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_type}")

    raw_text = extracted.text

    # 2. Text Preprocessing
    preprocessed = preprocess(raw_text)
    cleaned_text = preprocessed.cleaned

    # 3. Section Detection
    sections = detect_sections(cleaned_text)

    # 4. Entity Extraction (Regex + spaCy)
    entities = extract_entities(sections)

    # 5. Skill Extraction & Normalization
    skills = extract_skills(sections)

    # 6. Information Grouping (Experience & Education)
    grouped = group_information(sections, entities)

    # 7. Normalization and Pydantic Validation
    parsed_resume = normalize(
        sections=sections,
        entities=entities,
        grouped=grouped,
        skills=skills,
        raw_text=raw_text,
    )

    return parsed_resume

