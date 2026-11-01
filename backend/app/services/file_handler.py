import uuid
from pathlib import Path
from typing import Tuple

from app.config import settings

def validate_and_save_file(filename: str, content: bytes) -> Tuple[Path, str, str]:
    """Validates file extension and size, then writes to UPLOAD_DIR with a unique ID."""
    if not filename or "." not in filename:
        raise ValueError("Invalid filename: missing extension")

    ext = filename.rsplit(".", 1)[1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise ValueError(f"Extension not allowed: .{ext}. Allowed: {settings.ALLOWED_EXTENSIONS}")

    if len(content) > settings.MAX_FILE_SIZE:
        raise ValueError(
            f"File size ({len(content)} bytes) exceeds maximum allowed ({settings.MAX_FILE_SIZE} bytes)"
        )

    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    doc_id = uuid.uuid4().hex
    saved_filename = f"{doc_id}.{ext}"
    saved_path = settings.UPLOAD_DIR / saved_filename

    saved_path.write_bytes(content)

    return saved_path, ext, doc_id

