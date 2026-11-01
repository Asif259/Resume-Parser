import io
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.main import app
from app.config import settings

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def sample_pdf_bytes():
    import fitz  # PyMuPDF
    doc = fitz.open()
    page = doc.new_page()
    text = (
        "John Smith\n"
        "john.smith@email.com | +1 555 123 4567 | New York, USA\n\n"
        "Professional Summary\n"
        "Full-stack developer with 3 years of experience building web applications using React, Node.js, and PostgreSQL.\n\n"
        "Work Experience\n"
        "Software Engineer, ABC Technologies\n"
        "January 2023 - Present\n"
        "Developed web applications using React and Node.js.\n"
        "Designed REST APIs and PostgreSQL databases.\n\n"
        "Education\n"
        "Bachelor of Computer Science, XYZ University, 2022.\n\n"
        "Skills\n"
        "JavaScript, TypeScript, React, Node.js, Express, PostgreSQL, Git."
    )
    page.insert_text((50, 72), text, fontsize=11)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes

@pytest.fixture
def sample_docx_bytes():
    from docx import Document
    doc = Document()
    doc.add_heading("John Smith", level=0)
    doc.add_paragraph("john.smith@email.com | +1 555 123 4567 | New York, USA")
    doc.add_heading("Professional Summary", level=1)
    doc.add_paragraph("Full-stack developer with 3 years of experience building web applications.")
    doc.add_heading("Work Experience", level=1)
    doc.add_paragraph("Software Engineer, ABC Technologies\nJanuary 2023 - Present")
    doc.add_paragraph("Developed web applications using React and Node.js.")
    doc.add_heading("Education", level=1)
    doc.add_paragraph("Bachelor of Computer Science, XYZ University, 2022.")
    doc.add_heading("Skills", level=1)
    doc.add_paragraph("JavaScript, TypeScript, React, Node.js, Express, PostgreSQL, Git.")
    
    stream = io.BytesIO()
    doc.save(stream)
    return stream.getvalue()

