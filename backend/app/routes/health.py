from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/")
def root() -> dict[str, str]:
    return {"service": "job-matcher-agent", "status": "ok"}


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}
