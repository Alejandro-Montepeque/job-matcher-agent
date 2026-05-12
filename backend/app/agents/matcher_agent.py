"""Matcher agent built with Google ADK + Gemini.

The agent receives a CV (text) and a job posting (text), and returns a structured
analysis: match score, lists of matches/gaps, and concrete CV improvement suggestions.
"""

import json
import logging

import google.generativeai as genai
from google.generativeai.types import GenerationConfig

from app.config import settings
from app.schemas.analyze import AnalyzeResponse, Suggestion

logger = logging.getLogger(__name__)

genai.configure(api_key=settings.gemini_api_key)

SYSTEM_INSTRUCTION = """You are a senior technical recruiter.
You receive a candidate CV and a job posting. Analyze how well they match.

Return ONLY a JSON object with this exact shape:
{
  "match_score": <integer 0-100>,
  "summary": "<one-paragraph overall assessment>",
  "matches": ["<skill or experience that matches>", ...],
  "gaps": ["<requirement from the posting not found in the CV>", ...],
  "suggestions": [
    {"title": "<short title>", "detail": "<actionable advice for the CV>"},
    ...
  ]
}

Be specific, cite concrete skills and years of experience. Do not hallucinate.
If the CV does not mention a skill, treat it as a gap, do not assume it.
"""


class AgentError(Exception):
    """Raised when the agent cannot produce a valid analysis."""


def _build_prompt(cv_text: str, job_posting: str) -> str:
    return f"""CV:
\"\"\"
{cv_text}
\"\"\"

JOB POSTING:
\"\"\"
{job_posting}
\"\"\"
"""


async def run_matcher_agent(cv_text: str, job_posting: str) -> AnalyzeResponse:
    model = genai.GenerativeModel(
        model_name=settings.gemini_model,
        system_instruction=SYSTEM_INSTRUCTION,
        generation_config=GenerationConfig(
            response_mime_type="application/json",
            temperature=0.3,
        ),
    )

    try:
        response = await model.generate_content_async(_build_prompt(cv_text, job_posting))
    except Exception as e:
        logger.exception("Gemini API call failed")
        raise AgentError(f"Gemini API error: {e}") from e

    if not getattr(response, "text", None):
        logger.error("Empty response from Gemini: %r", response)
        raise AgentError("Gemini returned an empty response.")

    try:
        data = json.loads(response.text)
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON from Gemini: %s\n---\n%s", e, response.text)
        raise AgentError(f"Gemini returned invalid JSON: {e}") from e

    try:
        return AnalyzeResponse(
            match_score=int(data["match_score"]),
            summary=str(data["summary"]),
            matches=[str(m) for m in data.get("matches", [])],
            gaps=[str(g) for g in data.get("gaps", [])],
            suggestions=[Suggestion(**s) for s in data.get("suggestions", [])],
        )
    except (KeyError, ValueError, TypeError) as e:
        logger.error("Unexpected JSON shape from Gemini: %s\n---\n%s", e, data)
        raise AgentError(f"Unexpected response shape: {e}") from e
