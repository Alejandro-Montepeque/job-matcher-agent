from app.agents.matcher_agent import run_matcher_agent
from app.schemas.analyze import AnalyzeResponse


async def analyze_match(cv_text: str, job_posting: str) -> AnalyzeResponse:
    return await run_matcher_agent(cv_text=cv_text, job_posting=job_posting)
