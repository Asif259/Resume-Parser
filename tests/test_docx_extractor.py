import pytest
from pathlib import Path
from docx import Document

from app.services.docx_extractor import extract_docx
from app.services.pdf_extractor import ExtractedText

def test_extract_docx_with_text(tmp_path, sample_docx_bytes):
    docx_path = tmp_path / "sample.docx"
    docx_path.write_bytes(sample_docx_bytes)

    result = extract_docx(docx_path)

    assert isinstance(result, ExtractedText)
    assert result.method == "docx_text"
    assert "John Smith" in result.text
    assert "Software Engineer" in result.text
    assert "john.smith@email.com" in result.text
    assert "React" in result.text

def test_extract_docx_with_tables(tmp_path):
    docx_path = tmp_path / "table_resume.docx"
    doc = Document()
    doc.add_heading("Skills Table", level=1)
    table = doc.add_table(rows=2, cols=2)
    table.cell(0, 0).text = "Category"
    table.cell(0, 1).text = "Skills"
    table.cell(1, 0).text = "Frontend"
    table.cell(1, 1).text = "React, TypeScript"
    doc.save(str(docx_path))

    result = extract_docx(docx_path)
    assert "Skills Table" in result.text
    assert "Frontend" in result.text
    assert "React, TypeScript" in result.text

def test_extract_docx_nonexistent():
    with pytest.raises(FileNotFoundError):
        extract_docx(Path("missing_file.docx"))

