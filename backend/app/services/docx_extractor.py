from pathlib import Path
from docx import Document

from app.services.pdf_extractor import ExtractedText

def extract_docx(path: Path) -> ExtractedText:
    """Extract text from a DOCX document using python-docx.
    
    Extracts text from both paragraphs and table structures.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"DOCX file not found at: {path}")

    doc = Document(str(path))
    content_lines: list[str] = []

    # 1. Extract paragraphs
    for p in doc.paragraphs:
        line = p.text.strip()
        if line:
            content_lines.append(line)

    # 2. Extract tables
    for table in doc.tables:
        for row in table.rows:
            row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if row_cells:
                # Deduplicate identical adjacent cells (often created by merged cells)
                deduped = []
                for cell_txt in row_cells:
                    if not deduped or deduped[-1] != cell_txt:
                        deduped.append(cell_txt)
                content_lines.append(" | ".join(deduped))

    full_text = "\n".join(content_lines).strip()

    return ExtractedText(
        text=full_text,
        pages=1,  # DOCX does not expose strict page boundaries
        method="docx_text",
        metadata={
            "file_size": path.stat().st_size if path.exists() else 0,
            "paragraphs_count": len(doc.paragraphs),
            "tables_count": len(doc.tables),
        },
    )
