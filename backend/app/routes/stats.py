from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import Analysis
from app.schemas.analyze import StatsResponse

router = APIRouter(tags=["stats"])


@router.get("/stats", response_model=StatsResponse)
async def stats(db: AsyncSession = Depends(get_db)) -> StatsResponse:
    stmt = select(func.count(Analysis.id), func.avg(Analysis.match_score))
    result = await db.execute(stmt)
    total, avg = result.one()
    return StatsResponse(
        total_analyses=int(total or 0),
        average_score=round(float(avg or 0), 1),
    )
