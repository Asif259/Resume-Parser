from pathlib import Path

from app.schemas.resume import ParsedResume
from app.services.pdf_extractor import extract_pdf
from app.services.docx_extractor import extract_docx
from app.services.ocr_extractor import extract_image, extract_pdf_ocr
from app.services.preprocessor import preprocess
from app.services.section_detector import detect_sections
from app.services.entity_extractor import extract_entities
from app.services.skill_extractor import extract_skills_with_evidence
from app.services.information_grouper import group_information
from app.services.normalizer import normalize
from app.services.confidence import compute_overall_confidence, flag_low_confidence

def parse_resume(
    file_path: Path,
    file_type: str,
    use_ml: bool = False,
    use_semantic: bool = False,
) -> ParsedResume:
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

    # 4. Entity Extraction (Hybrid: Rules + ML)
    if use_ml:
        from app.services.hybrid_extractor import HybridExtractor
        hybrid = HybridExtractor(use_ml=True)
        entities = hybrid.extract(sections, raw_text=raw_text)
    else:
        entities = extract_entities(sections)

    # 5. Skill Extraction & Normalization
    skills, skill_evidence = extract_skills_with_evidence(
        sections,
        use_semantic=use_semantic,
    )

    # 6. Information Grouping (Experience & Education)
    grouped = group_information(sections, entities)

    # 7. Normalization and Pydantic Validation
    evidence_dict = {}
    for skill_name, ev in skill_evidence.items():
        evidence_dict[f"skills.{skill_name}"] = ev

    parsed_resume = normalize(
        sections=sections,
        entities=entities,
        grouped=grouped,
        skills=skills,
        raw_text=raw_text,
        evidence=evidence_dict,
    )

    if parsed_resume.evidence:
        parsed_resume.confidence_score = compute_overall_confidence(parsed_resume.evidence)
        parsed_resume.low_confidence_fields = flag_low_confidence(parsed_resume.evidence)

    return parsed_resume

