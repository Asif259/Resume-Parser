def test_health_check(test_client):
    response = test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "NLP Resume Parser API" in data["project"]

def test_fixtures(sample_pdf_bytes, sample_docx_bytes):
    assert len(sample_pdf_bytes) > 0
    assert len(sample_docx_bytes) > 0
