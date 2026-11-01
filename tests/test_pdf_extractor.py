import fitz
import pytest
from pathlib import Path

from app.services.pdf_extractor import extract_pdf, ExtractedText

def test_extract_pdf_with_text(tmp_path, sample_pdf_bytes):
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(sample_pdf_bytes)

    result = extract_pdf(pdf_path)

    assert isinstance(result, ExtractedText)
    assert result.pages == 1
    assert result.method == "pdf_text"
    assert "John Smith" in result.text
    assert "Software Engineer" in result.text
    assert "john.smith@email.com" in result.text

def test_extract_pdf_empty_triggers_ocr_needed(tmp_path):
    # Create empty PDF
    pdf_path = tmp_path / "empty.pdf"
    doc = fitz.open()
    doc.new_page()
    doc.save(str(pdf_path))
    doc.close()

    result = extract_pdf(pdf_path)

    assert isinstance(result, ExtractedText)
    assert result.pages == 1
    assert result.method == "ocr_needed"
    assert len(result.text.strip()) < 50

def test_extract_pdf_two_column_reading_order(tmp_path):
    pdf_path = tmp_path / "two_column.pdf"
    doc = fitz.open()
    page = doc.new_page(width=600, height=800)
    # Left column at x=50, y=100
    page.insert_text((50, 100), "LEFT_COLUMN_HEADER\nLeft column content line 1\nLeft column content line 2")
    # Right column at x=350, y=100
    page.insert_text((350, 100), "RIGHT_COLUMN_HEADER\nRight column content line 1\nRight column content line 2")
    doc.save(str(pdf_path))
    doc.close()

    result = extract_pdf(pdf_path)
    assert "LEFT_COLUMN_HEADER" in result.text
    assert "RIGHT_COLUMN_HEADER" in result.text
    assert result.method == "pdf_text"

def test_extract_pdf_nonexistent():
    with pytest.raises(FileNotFoundError):
        extract_pdf(Path("nonexistent_resume.pdf"))
