import pytest
from app.database.session import get_db, init_db, SessionLocal
from app.database.models import ResumeRecord, save_resume, get_resume, list_resumes
from app.schemas.resume import ParsedResume, PersonalInfo

def test_save_and_retrieve_resume():
    init_db()
    db = SessionLocal()
    try:
        parsed = ParsedResume(
            personal_info=PersonalInfo(name="Alice Test", email="alice@test.com"),
            skills=["Python", "FastAPI"],
        )
        doc_id = "test-doc-123"
        filename = "alice_resume.pdf"
        file_path = "/path/to/alice_resume.pdf"
        original_text = "Alice Test raw text"

        saved_id = save_resume(
            db=db,
            doc_id=doc_id,
            filename=filename,
            parsed_resume=parsed,
            original_text=original_text,
            file_path=file_path,
        )

        assert saved_id == doc_id

        retrieved = get_resume(db, doc_id)
        assert retrieved is not None
        assert retrieved.id == doc_id
        assert retrieved.filename == filename
        assert retrieved.parsed_data["personal_info"]["name"] == "Alice Test"
        assert retrieved.parsed_data["skills"] == ["Python", "FastAPI"]
        assert retrieved.original_text == original_text

        all_resumes = list_resumes(db)
        assert any(r.id == doc_id for r in all_resumes)
    finally:
        db.close()
