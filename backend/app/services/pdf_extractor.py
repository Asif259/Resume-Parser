from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import fitz  # PyMuPDF

@dataclass
class ExtractedText:
    text: str
    pages: int
    method: str
    metadata: dict[str, Any] = field(default_factory=dict)

def extract_pdf(path: Path) -> ExtractedText:
    """Extract text from a PDF document using PyMuPDF.
    
    Uses sort=True to preserve spatial reading order across columns.
    If extracted text length is under 50 characters, marks method as 'ocr_needed'.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found at: {path}")

    doc = fitz.open(str(path))
    pages_count = len(doc)
    text_chunks: list[str] = []

    for page in doc:
        # sort=True ensures proper reading order for multi-column layouts
        page_text = page.get_text("text", sort=True)
        if page_text:
            text_chunks.append(page_text.strip())

    doc.close()

    full_text = "\n\n".join(text_chunks).strip()
    
    # Check if text is too sparse (scanned or image-only PDF)
    method = "ocr_needed" if len(full_text) < 50 else "pdf_text"

    return ExtractedText(
        text=full_text,
        pages=pages_count,
        method=method,
        metadata={"file_size": path.stat().st_size if path.exists() else 0},
    )
