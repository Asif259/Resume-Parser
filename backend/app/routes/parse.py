import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Security, UploadFile, File, status
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.orm import Session

from app.config import settings
from app.database.session import get_db
from app.database.models import save_resume, get_resume, list_resumes
from app.schemas.resume import ParseResponse, ParsedResume
from app.services.file_handler import validate_and_save_file
from app.services.pipeline import parse_resume

logger = logging.getLogger(__name__)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: Optional[str] = Security(api_key_header)) -> Optional[str]:
    """Validates X-API-Key header if API_KEY setting is populated.
    Permits unauthenticated requests when API_KEY is unset (None / empty).
    """
    if settings.API_KEY:
        if not api_key or api_key != settings.API_KEY:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing API key in X-API-Key header",
            )
    return api_key

router = APIRouter(prefix="/api", tags=["Resumes"], dependencies=[Depends(verify_api_key)])

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
        parsed_resume = parse_resume(
            file_path=saved_path,
            file_type=ext,
            use_ml=settings.USE_ML,
            use_semantic=settings.USE_SEMANTIC,
        )
    except ValueError as e:
        if saved_path.exists():
            saved_path.unlink()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        if saved_path.exists():
            saved_path.unlink()
        logger.error("Failed to parse resume document: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Failed to parse resume document. Please verify document formatting and integrity.",
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
def list_parsed_resumes(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
):
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

