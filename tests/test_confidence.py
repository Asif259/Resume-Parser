import pytest
from pathlib import Path
from app.schemas.evidence import FieldEvidence
from app.schemas.resume import ParsedResume
from app.services.confidence import compute_overall_confidence, flag_low_confidence
from app.services.pipeline import parse_resume

def test_overall_confidence_high():
    evidence = {
        "personal_info.email": FieldEvidence(value="a@b.c", source_section="personal_info", source_text="a@b.c", confidence=0.99),
        "personal_info.name": FieldEvidence(value="John", source_section="personal_info", source_text="John", confidence=0.90),
    }
    score = compute_overall_confidence(evidence)
    assert 0.85 <= score <= 1.0

def test_flag_low_confidence():
    evidence = {
        "personal_info.name": FieldEvidence(value="Candidate", source_section="personal_info", source_text="Candidate", confidence=0.45),
        "personal_info.email": FieldEvidence(value="a@b.c", source_section="personal_info", source_text="a@b.c", confidence=0.99),
    }
    flagged = flag_low_confidence(evidence, threshold=0.6)
    assert "personal_info.name" in flagged
    assert "personal_info.email" not in flagged

def test_pipeline_parsed_resume_has_confidence(sample_pdf_bytes, tmp_path: Path):
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_bytes(sample_pdf_bytes)
    result = parse_resume(pdf_path, "pdf")
    assert result.confidence_score is not None
    assert 0.0 <= result.confidence_score <= 1.0
    assert isinstance(result.low_confidence_fields, list)

