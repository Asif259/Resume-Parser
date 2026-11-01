from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models import save_resume, get_resume, list_resumes
from app.schemas.resume import ParseResponse, ParsedResume
from app.services.file_handler import validate_and_save_file
from app.services.pipeline import parse_resume

router = APIRouter(prefix="/api", tags=["Resumes"])

@router.post("/parse", response_model=ParseResponse, status_code=status.HTTP_200_OK)
async def upload_and_parse_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Uploads a resume file (PDF, DOCX, image), extracts structured data via NLP,
    stores the record in the database, and returns the parsed result.
    """
    try:
        content = await file.read()
        saved_path, ext, doc_id = validate_and_save_file(
            filename=file.filename or "resume",
            content=content,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    try:
        parsed_resume = parse_resume(file_path=saved_path, file_type=ext)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse resume document: {str(e)}",
        )

    # Save to database
    save_resume(
        db=db,
        doc_id=doc_id,
        filename=file.filename or saved_path.name,
        parsed_resume=parsed_resume,
        original_text=parsed_resume.raw_text or "",
        file_path=str(saved_path),
    )

    return ParseResponse(
        id=doc_id,
        filename=file.filename or saved_path.name,
        parsed_resume=parsed_resume,
    )

@router.get("/resumes/{doc_id}", response_model=ParseResponse)
def get_parsed_resume_by_id(doc_id: str, db: Session = Depends(get_db)):
    """Retrieves a single parsed resume by ID."""
    record = get_resume(db, doc_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

    parsed_model = ParsedResume(**record.parsed_data)
    return ParseResponse(
        id=record.id,
        filename=record.filename,
        parsed_resume=parsed_model,
        created_at=record.created_at,
    )

@router.get("/resumes", response_model=List[ParseResponse])
def list_parsed_resumes(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """Lists parsed resumes with pagination."""
    records = list_resumes(db, skip=skip, limit=limit)
    results = []
    for r in records:
        parsed_model = ParsedResume(**r.parsed_data)
        results.append(
            ParseResponse(
                id=r.id,
                filename=r.filename,
                parsed_resume=parsed_model,
                created_at=r.created_at,
            )
        )
    return results

