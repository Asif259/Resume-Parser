import json
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import Column, String, Text, DateTime, JSON
from sqlalchemy.orm import Session

from app.database.session import Base
from app.schemas.resume import ParsedResume

class ResumeRecord(Base):
    __tablename__ = "resumes"

    id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=True)
    original_text = Column(Text, nullable=True)
    parsed_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

def save_resume(
    db: Session,
    doc_id: str,
    filename: str,
    parsed_resume: ParsedResume,
    original_text: str = "",
    file_path: str = "",
) -> str:
    """Persists a parsed resume record to the database."""
    parsed_dict = json.loads(parsed_resume.model_dump_json())

    record = ResumeRecord(
        id=doc_id,
        filename=filename,
        file_path=file_path,
        original_text=original_text,
        parsed_data=parsed_dict,
        created_at=datetime.now(timezone.utc),
    )
    db.merge(record)
    db.commit()
    return doc_id

def get_resume(db: Session, doc_id: str) -> Optional[ResumeRecord]:
    """Fetches a single resume by its ID."""
    return db.query(ResumeRecord).filter(ResumeRecord.id == doc_id).first()

def list_resumes(db: Session, skip: int = 0, limit: int = 100) -> List[ResumeRecord]:
    """Lists resumes ordered by most recent first."""
    return (
        db.query(ResumeRecord)
        .order_by(ResumeRecord.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
