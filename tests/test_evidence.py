import pytest
from pathlib import Path
from app.schemas.evidence import FieldEvidence
from app.schemas.resume import ParsedResume
from app.services.entity_extractor import extract_entities
from app.services.skill_extractor import extract_skills_with_evidence
from app.services.pipeline import parse_resume

def test_field_evidence_model():
    ev = FieldEvidence(
        value="John Doe",
        source_section="personal_info",
        source_text="John Doe\njohn@email.com",
        confidence=0.95,
    )
    assert ev.value == "John Doe"
    assert ev.confidence == 0.95
    assert ev.source_section == "personal_info"

def test_entity_extractor_returns_evidence():
    sections = {"personal_info": "Jane Smith\njane@test.com\n+1 555 0100\nNew York, USA"}
    entities = extract_entities(sections)
    assert hasattr(entities, "evidence")
    assert "personal_info.name" in entities.evidence or "name" in entities.evidence
    name_ev = entities.evidence.get("personal_info.name") or entities.evidence.get("name")
    assert name_ev.source_section == "personal_info"
    assert "Jane Smith" in name_ev.source_text

def test_skill_extractor_returns_evidence():
    sections = {"skills": "Python, Java, SQL"}
    skills, evidence = extract_skills_with_evidence(sections)
    assert "Python" in skills
    assert "Python" in evidence
    assert evidence["Python"].source_section == "skills"
    assert evidence["Python"].value == "Python"

def test_pipeline_parsed_resume_includes_evidence(sample_pdf_bytes, tmp_path: Path):
    pdf_path = tmp_path / "test_doc.pdf"
    pdf_path.write_bytes(sample_pdf_bytes)
    result = parse_resume(pdf_path, "pdf")
    assert isinstance(result, ParsedResume)
    assert result.evidence is not None
    assert len(result.evidence) > 0
    # Check that personal info or skills are recorded in evidence
    assert any("email" in k or "name" in k or "skills" in k for k in result.evidence.keys())

