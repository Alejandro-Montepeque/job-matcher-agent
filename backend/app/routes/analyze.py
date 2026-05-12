import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.matcher_agent import AgentError
from app.db.database import get_db
from app.schemas.analyze import AnalyzeResponse
from app.services.cache import find_cached, hash_text, save_analysis
from app.services.cv_parser import extract_text_from_pdf
from app.services.matcher import analyze_match

logger = logging.getLogger(__name__)

router = APIRouter(tags=["analyze"])


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    cv: UploadFile = File(..., description="CV in PDF format"),
    job_posting: str = Form(..., min_length=20, description="Job posting text"),
    db: AsyncSession = Depends(get_db),
) -> AnalyzeResponse:
    if cv.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="CV must be a PDF file")

    pdf_bytes = await cv.read()
    if len(pdf_bytes) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="CV exceeds 5MB limit")

    cv_hash = hash_text(pdf_bytes)
    job_hash = hash_text(job_posting.strip())

    cached = await find_cached(db, cv_hash=cv_hash, job_hash=job_hash)
    if cached is not None:
        cached.cached = True
        return cached

    cv_text = extract_text_from_pdf(pdf_bytes)
    if not cv_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from PDF")

    try:
        result = await analyze_match(cv_text=cv_text, job_posting=job_posting)
    except AgentError as e:
        logger.error("Agent failed: %s", e)
        raise HTTPException(status_code=502, detail=str(e)) from e

    await save_analysis(
        db,
        cv_hash=cv_hash,
        cv_filename=cv.filename or "cv.pdf",
        job_hash=job_hash,
        job_posting=job_posting,
        result=result,
    )
    return result
