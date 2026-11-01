import fitz
import pytest
from pathlib import Path

from app.services.pdf_extractor import extract_pdf, ExtractedText, evaluate_text_quality

def test_evaluate_text_quality_good_text():
    assert evaluate_text_quality("John Doe\nSoftware Engineer\nPython Java SQL React Node", page_count=1) is True

def test_evaluate_text_quality_garbled():
    assert evaluate_text_quality("##$$@@!!%%^^ &&**((__))++", page_count=1) is False

def test_evaluate_text_quality_empty():
    assert evaluate_text_quality("", page_count=1) is False

def test_evaluate_text_quality_too_few_words():
    assert evaluate_text_quality("abc", page_count=1) is False

def test_digital_pdf_with_images_no_ocr(tmp_path):
    """A valid PDF with real text should NOT trigger OCR."""
    pdf_path = tmp_path / "valid_doc.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 100), "John Doe\nSoftware Engineer at Google\nDeveloped scalable web applications in Python.")
    doc.save(str(pdf_path))
    doc.close()

    result = extract_pdf(pdf_path)
    assert result.method == "pdf_text"

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

def test_two_column_layout_coherence(tmp_path):
    pdf_path = tmp_path / "two_col_resume.pdf"
    doc = fitz.open()
    page = doc.new_page(width=600, height=800)
    # Left column: Experience
    page.insert_textbox(
        fitz.Rect(50, 100, 280, 500),
        "WORK EXPERIENCE\nSenior Software Engineer\nBuilt high throughput backend microservices.\nOptimized SQL queries."
    )
    # Right column: Skills
    page.insert_textbox(
        fitz.Rect(320, 100, 550, 500),
        "TECHNICAL SKILLS\nPython\nFastAPI\nPostgreSQL\nDocker\nKubernetes"
    )
    doc.save(str(pdf_path))
    doc.close()

    result = extract_pdf(pdf_path)
    assert result.metadata.get("layout") == "multi_column"
    # Content of left column should stay intact
    assert "Senior Software Engineer\nBuilt high throughput backend microservices." in result.text

def test_layout_detection_single_column(tmp_path, sample_pdf_bytes):
    pdf_path = tmp_path / "single_col.pdf"
    pdf_path.write_bytes(sample_pdf_bytes)
    result = extract_pdf(pdf_path)
    assert result.metadata.get("layout") == "single_column"

def test_extract_pdf_nonexistent():
    with pytest.raises(FileNotFoundError):
        extract_pdf(Path("nonexistent_resume.pdf"))
