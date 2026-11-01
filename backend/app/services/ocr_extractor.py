import io
from pathlib import Path
from PIL import Image
import pytesseract
import fitz  # PyMuPDF

from app.services.pdf_extractor import ExtractedText

def extract_image(path: Path) -> ExtractedText:
    """Extract text from an image file (PNG, JPG, TIFF, etc.) using Tesseract OCR."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Image file not found at: {path}")

    image = Image.open(str(path))
    # Convert RGBA/P to RGB for clean OCR
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")

    raw_text = pytesseract.image_to_string(image)
    cleaned_text = raw_text.strip()

    return ExtractedText(
        text=cleaned_text,
        pages=1,
        method="ocr",
        metadata={
            "image_size": image.size,
            "format": image.format,
            "file_size": path.stat().st_size,
        },
    )

def extract_pdf_ocr(path: Path, dpi: int = 200) -> ExtractedText:
    """Extract text from a scanned/image-based PDF by rendering pages and running OCR."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found at: {path}")

    doc = fitz.open(str(path))
    pages_count = len(doc)
    text_chunks: list[str] = []

    for page_idx, page in enumerate(doc):
        pix = page.get_pixmap(dpi=dpi)
        img_bytes = pix.tobytes("png")
        image = Image.open(io.BytesIO(img_bytes))
        page_text = pytesseract.image_to_string(image).strip()
        if page_text:
            text_chunks.append(page_text)

    doc.close()

    full_text = "\n\n".join(text_chunks).strip()

    return ExtractedText(
        text=full_text,
        pages=pages_count,
        method="pdf_ocr",
        metadata={"file_size": path.stat().st_size if path.exists() else 0},
    )

