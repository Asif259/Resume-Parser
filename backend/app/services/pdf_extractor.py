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

def _extract_page_layout_aware(page: fitz.Page) -> tuple[str, str]:
    """Extracts text from a page while detecting and preserving multi-column layout.
    Returns (page_text, layout_type) where layout_type is 'multi_column' or 'single_column'.
    """
    blocks = page.get_text("blocks")
    # Filter text blocks: (x0, y0, x1, y1, text, block_no, block_type)
    text_blocks = [b for b in blocks if len(b) >= 5 and b[4].strip()]
    if not text_blocks:
        return "", "single_column"

    page_width = page.rect.width
    mid_boundary = page_width * 0.5

    # Check for left and right column candidates
    left_blocks = [b for b in text_blocks if b[2] <= page_width * 0.58 and b[0] < mid_boundary]
    right_blocks = [b for b in text_blocks if b[0] >= page_width * 0.42 and b[2] > mid_boundary]

    # If left and right blocks overlap vertically, they are side-by-side columns
    is_multi_column = False
    if left_blocks and right_blocks:
        for lb in left_blocks:
            for rb in right_blocks:
                if max(lb[1], rb[1]) < min(lb[3], rb[3]):
                    is_multi_column = True
                    break
            if is_multi_column:
                break

    if is_multi_column:
        min_col_top = min(min(b[1] for b in left_blocks), min(b[1] for b in right_blocks))
        max_col_bottom = max(max(b[3] for b in left_blocks), max(b[3] for b in right_blocks))

        header_blocks = [b for b in text_blocks if b[3] <= min_col_top and b not in left_blocks and b not in right_blocks]
        footer_blocks = [b for b in text_blocks if b[1] >= max_col_bottom and b not in left_blocks and b not in right_blocks]

        # Sort each region vertically
        header_blocks.sort(key=lambda b: (b[1], b[0]))
        left_blocks.sort(key=lambda b: (b[1], b[0]))
        right_blocks.sort(key=lambda b: (b[1], b[0]))
        footer_blocks.sort(key=lambda b: (b[1], b[0]))

        ordered_texts = [
            b[4].strip()
            for b in (header_blocks + left_blocks + right_blocks + footer_blocks)
            if b[4].strip()
        ]
        return "\n\n".join(ordered_texts), "multi_column"

    # Single column: sort top-to-bottom, left-to-right
    text_blocks.sort(key=lambda b: (b[1], b[0]))
    ordered_texts = [b[4].strip() for b in text_blocks if b[4].strip()]
    return "\n\n".join(ordered_texts), "single_column"

def extract_pdf(path: Path) -> ExtractedText:
    """Extract text from a PDF document using PyMuPDF with layout awareness."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found at: {path}")

    doc = fitz.open(str(path))
    pages_count = len(doc)
    text_chunks: list[str] = []
    has_multi_column = False

    for page in doc:
        page_text, page_layout = _extract_page_layout_aware(page)
        if page_layout == "multi_column":
            has_multi_column = True
        if page_text:
            text_chunks.append(page_text)

    doc.close()

    full_text = "\n\n".join(text_chunks).strip()
    layout = "multi_column" if has_multi_column else "single_column"
    
    # Check if text is too sparse (scanned or image-only PDF)
    method = "ocr_needed" if len(full_text) < 50 else "pdf_text"

    return ExtractedText(
        text=full_text,
        pages=pages_count,
        method=method,
        metadata={
            "file_size": path.stat().st_size if path.exists() else 0,
            "layout": layout,
        },
    )

