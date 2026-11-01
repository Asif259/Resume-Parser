import pytest
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from app.services.ocr_extractor import extract_image, extract_pdf_ocr
from app.services.pdf_extractor import ExtractedText

def test_extract_image_with_text(tmp_path):
    img_path = tmp_path / "resume_snippet.png"
    # Create an image with high-contrast readable text
    img = Image.new("RGB", (600, 200), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    # Use default bitmap font or basic text
    draw.text((30, 40), "John Smith", fill=(0, 0, 0))
    draw.text((30, 80), "Software Engineer", fill=(0, 0, 0))
    draw.text((30, 120), "john.smith@email.com", fill=(0, 0, 0))
    img.save(str(img_path))

    result = extract_image(img_path)

    assert isinstance(result, ExtractedText)
    assert result.method == "ocr"
    assert "John" in result.text or "Smith" in result.text
    assert "Software" in result.text or "Engineer" in result.text

def test_extract_image_nonexistent():
    with pytest.raises(FileNotFoundError):
        extract_image(Path("missing_image.png"))

def test_extract_pdf_ocr_fallback(tmp_path, sample_pdf_bytes):
    # Tests OCR applied page by page to a PDF
    pdf_path = tmp_path / "scanned_sample.pdf"
    pdf_path.write_bytes(sample_pdf_bytes)

    result = extract_pdf_ocr(pdf_path)
    assert isinstance(result, ExtractedText)
    assert result.method == "pdf_ocr"
    assert "John" in result.text

