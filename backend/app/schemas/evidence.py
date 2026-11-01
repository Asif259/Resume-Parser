from typing import Optional
from pydantic import BaseModel

class FieldEvidence(BaseModel):
    value: str
    normalized_value: Optional[str] = None
    source_section: str
    source_text: str
    confidence: float = 1.0
    page: Optional[int] = None
