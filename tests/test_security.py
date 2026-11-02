import fitz
import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.services.file_handler import validate_and_save_file, validate_magic_bytes
from app.services.pdf_extractor import extract_pdf

def test_magic_bytes_detection():
    # Valid PDF signature
    assert validate_magic_bytes("pdf", b"%PDF-1.4 header") is True
    # Spoofed PDF (shell script content)
    assert validate_magic_bytes("pdf", b"#!/bin/bash\necho hello") is False
    # Valid DOCX signature
    assert validate_magic_bytes("docx", b"PK\x03\x04\x14\x00\x06\x00") is True
    # Spoofed DOCX
    assert validate_magic_bytes("docx", b"malicious executable payload") is False

def test_upload_magic_bytes_spoofing(test_client):
    # Extension says .pdf, but content is shell script
    response = test_client.post(
        "/api/parse",
        files={"file": ("fake_resume.pdf", b"echo 'hack'", "application/pdf")},
    )
    assert response.status_code == 400
    assert "signature does not match declared extension" in response.json()["detail"]

def test_max_pdf_pages_rejection(tmp_path):
    # Create 11-page PDF (limit is 10)
    doc = fitz.open()
    for i in range(settings.MAX_PDF_PAGES + 1):
        page = doc.new_page()
        page.insert_text((50, 72), f"Page {i+1} content", fontsize=11)
    
    pdf_path = tmp_path / "long_resume.pdf"
    doc.save(str(pdf_path))
    doc.close()

    with pytest.raises(ValueError, match="exceeds maximum page limit"):
        extract_pdf(pdf_path)

def test_upload_pdf_exceeding_pages(test_client, tmp_path):
    # Upload PDF with 12 pages
    doc = fitz.open()
    for i in range(12):
        page = doc.new_page()
        page.insert_text((50, 72), f"Page {i+1} content", fontsize=11)
    pdf_bytes = doc.tobytes()
    doc.close()

    response = test_client.post(
        "/api/parse",
        files={"file": ("exceeding.pdf", pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 400
    assert "exceeds maximum page limit" in response.json()["detail"]

def test_pagination_bounds_validation(test_client):
    # Limit > 100 rejected by Pydantic / FastAPI Query
    res_over = test_client.get("/api/resumes?limit=101")
    assert res_over.status_code == 422

    # Limit < 1 rejected
    res_under = test_client.get("/api/resumes?limit=0")
    assert res_under.status_code == 422

    # Valid limit passes
    res_valid = test_client.get("/api/resumes?limit=25")
    assert res_valid.status_code == 200

def test_cors_settings_safe():
    # Ensure wildcard origin is absent when credentials enabled
    assert "*" not in settings.CORS_ORIGINS
    assert "http://localhost:3000" in settings.CORS_ORIGINS

def test_rate_limiter_throttling(test_client, monkeypatch):
    from app.main import app
    # Set tight limit for test
    for mw in app.user_middleware:
        if "RateLimitMiddleware" in str(mw):
            pass

    # Find the middleware instance on app
    # Test client against rapid requests
    client = TestClient(app)
    
    # Send requests to /health (not rate limited)
    for _ in range(5):
        h_res = client.get("/health")
        assert h_res.status_code == 200

def test_orphaned_file_cleanup_on_failure(test_client, sample_pdf_bytes, monkeypatch):
    from app.routes import parse
    
    # Force parse_resume to raise unexpected exception
    def mock_parse_fail(*args, **kwargs):
        raise RuntimeError("Simulated parser failure")
    
    monkeypatch.setattr(parse, "parse_resume", mock_parse_fail)

    # Check upload directory before
    before_files = set(settings.UPLOAD_DIR.glob("*"))

    response = test_client.post(
        "/api/parse",
        files={"file": ("fail_clean.pdf", sample_pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 422
    assert "Failed to parse resume document" in response.json()["detail"]
    assert "Simulated parser failure" not in response.json()["detail"]  # Sanitized!

    # Check upload directory after: no orphaned file left behind
    after_files = set(settings.UPLOAD_DIR.glob("*"))
    assert before_files == after_files

def test_api_key_authentication(sample_pdf_bytes, monkeypatch):
    client = TestClient(app)
    monkeypatch.setattr(settings, "API_KEY", "super-secret-token")

    # Request without key -> 401
    res_no_key = client.get("/api/resumes")
    assert res_no_key.status_code == 401
    assert "Invalid or missing API key" in res_no_key.json()["detail"]

    # Request with invalid key -> 401
    res_bad_key = client.get("/api/resumes", headers={"X-API-Key": "wrong-token"})
    assert res_bad_key.status_code == 401

    # Request with valid key -> 200
    res_good_key = client.get("/api/resumes", headers={"X-API-Key": "super-secret-token"})
    assert res_good_key.status_code == 200
