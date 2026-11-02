import uuid
from pathlib import Path
from typing import Tuple

from app.config import settings

MAGIC_SIGNATURES: dict[str, list[bytes]] = {
    "pdf": [b"%PDF-"],
    "docx": [b"PK\x03\x04"],
    "doc": [b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"],
    "jpg": [b"\xff\xd8\xff"],
    "jpeg": [b"\xff\xd8\xff"],
    "png": [b"\x89PNG\r\n\x1a\n"],
}

def validate_magic_bytes(ext: str, content: bytes) -> bool:
    """Validates that initial bytes match expected file signature."""
    signatures = MAGIC_SIGNATURES.get(ext)
    if not signatures:
        return True
    return any(content.startswith(sig) for sig in signatures)

def validate_and_save_file(filename: str, content: bytes) -> Tuple[Path, str, str]:
    """Validates file extension, size, and magic bytes, then writes to UPLOAD_DIR with a unique ID."""
    if not filename or "." not in filename:
        raise ValueError("Invalid filename: missing extension")

    ext = filename.rsplit(".", 1)[1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise ValueError(f"Extension not allowed: .{ext}. Allowed: {settings.ALLOWED_EXTENSIONS}")

    if len(content) > settings.MAX_FILE_SIZE:
        raise ValueError(
            f"File size ({len(content)} bytes) exceeds maximum allowed ({settings.MAX_FILE_SIZE} bytes)"
        )

    if not validate_magic_bytes(ext, content):
        raise ValueError(f"File content signature does not match declared extension: .{ext}")

    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    doc_id = uuid.uuid4().hex
    saved_filename = f"{doc_id}.{ext}"
    saved_path = settings.UPLOAD_DIR / saved_filename

    saved_path.write_bytes(content)

    return saved_path, ext, doc_id

