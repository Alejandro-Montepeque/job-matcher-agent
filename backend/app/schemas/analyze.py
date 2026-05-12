from pydantic import BaseModel, Field


class Suggestion(BaseModel):
    title: str
    detail: str


class AnalyzeResponse(BaseModel):
    match_score: int = Field(..., ge=0, le=100)
    summary: str
    matches: list[str]
    gaps: list[str]
    suggestions: list[Suggestion]
    cached: bool = False


class StatsResponse(BaseModel):
    total_analyses: int
    average_score: float
