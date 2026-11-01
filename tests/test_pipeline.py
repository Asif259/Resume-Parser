import pytest
from pathlib import Path
from app.services.pipeline import parse_resume
from app.services.file_handler import validate_and_save_file
from app.schemas.resume import ParsedResume

def test_parse_resume_from_pdf(tmp_path, sample_pdf_bytes):
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(sample_pdf_bytes)

    resume = parse_resume(pdf_path, file_type="pdf")

    assert isinstance(resume, ParsedResume)
    assert resume.personal_info.name is not None
    assert "john.smith@email.com" in (resume.personal_info.email or "")
    assert len(resume.skills) > 0
    assert any("React" in s for s in resume.skills)
    assert len(resume.experience) >= 1
    assert len(resume.education) >= 1

def test_parse_resume_from_docx(tmp_path, sample_docx_bytes):
    docx_path = tmp_path / "sample.docx"
    docx_path.write_bytes(sample_docx_bytes)

    resume = parse_resume(docx_path, file_type="docx")

    assert isinstance(resume, ParsedResume)
    assert resume.personal_info.name is not None
    assert resume.personal_info.email == "john.smith@email.com"
    assert len(resume.skills) > 0
    assert len(resume.experience) >= 1

def test_validate_and_save_file(tmp_path, sample_pdf_bytes, monkeypatch):
    from app.config import settings
    monkeypatch.setattr(settings, "UPLOAD_DIR", tmp_path)

    saved_path, ext, doc_id = validate_and_save_file(
        filename="my_resume.pdf",
        content=sample_pdf_bytes
    )

    assert saved_path.exists()
    assert ext == "pdf"
    assert len(doc_id) > 0

def test_validate_disallowed_extension():
    with pytest.raises(ValueError, match="Extension not allowed"):
        validate_and_save_file(
            filename="malicious.exe",
            content=b"evil bytes"
        )

def test_validate_file_too_large(tmp_path, monkeypatch):
    from app.config import settings
    monkeypatch.setattr(settings, "MAX_FILE_SIZE", 50)
    with pytest.raises(ValueError, match="exceeds maximum allowed"):
        validate_and_save_file(
            filename="large.pdf",
            content=b"x" * 100
        )
