import hashlib

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Analysis
from app.schemas.analyze import AnalyzeResponse, Suggestion


def hash_text(content: bytes | str) -> str:
    data = content if isinstance(content, bytes) else content.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


async def find_cached(
    db: AsyncSession, cv_hash: str, job_hash: str
) -> AnalyzeResponse | None:
    stmt = select(Analysis).where(
        Analysis.cv_hash == cv_hash,
        Analysis.job_hash == job_hash,
    )
    result = await db.execute(stmt)
    row = result.scalar_one_or_none()
    if row is None:
        return None

    return AnalyzeResponse(
        match_score=row.match_score,
        summary=row.summary,
        matches=list(row.matches or []),
        gaps=list(row.gaps or []),
        suggestions=[Suggestion(**s) for s in (row.suggestions or [])],
    )


async def save_analysis(
    db: AsyncSession,
    *,
    cv_hash: str,
    cv_filename: str,
    job_hash: str,
    job_posting: str,
    result: AnalyzeResponse,
) -> None:
    row = Analysis(
        cv_hash=cv_hash,
        cv_filename=cv_filename,
        job_hash=job_hash,
        job_posting=job_posting,
        match_score=result.match_score,
        summary=result.summary,
        matches=result.matches,
        gaps=result.gaps,
        suggestions=[s.model_dump() for s in result.suggestions],
    )
    db.add(row)
    await db.commit()
