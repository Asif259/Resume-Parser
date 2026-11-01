import io
import pytest

def test_upload_and_parse_pdf(test_client, sample_pdf_bytes):
    response = test_client.post(
        "/api/parse",
        files={"file": ("john_smith_resume.pdf", sample_pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["filename"] == "john_smith_resume.pdf"
    parsed = data["parsed_resume"]
    assert parsed["personal_info"]["name"] is not None
    assert "john.smith@email.com" in parsed["personal_info"]["email"]
    assert len(parsed["skills"]) > 0

    # Retrieve by ID
    resume_id = data["id"]
    get_res = test_client.get(f"/api/resumes/{resume_id}")
    assert get_res.status_code == 200
    get_data = get_res.json()
    assert get_data["id"] == resume_id
    assert get_data["parsed_resume"]["personal_info"]["name"] == parsed["personal_info"]["name"]

def test_upload_invalid_extension(test_client):
    response = test_client.post(
        "/api/parse",
        files={"file": ("script.sh", b"#!/bin/bash\necho hello", "text/x-sh")},
    )
    assert response.status_code == 400
    assert "Extension not allowed" in response.json()["detail"]

def test_get_nonexistent_resume(test_client):
    response = test_client.get("/api/resumes/nonexistent-id-999")
    assert response.status_code == 404

def test_list_resumes(test_client, sample_pdf_bytes):
    test_client.post(
        "/api/parse",
        files={"file": ("listed_resume.pdf", sample_pdf_bytes, "application/pdf")},
    )
    response = test_client.get("/api/resumes")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(r["filename"] == "listed_resume.pdf" for r in data)

