"""Test configuration.

Set required environment variables before any `app.*` module is imported.
Tests do not call Gemini or hit a real database; they only need the app to
construct successfully so the FastAPI TestClient can exercise it.
"""

import os

os.environ.setdefault("GEMINI_API_KEY", "test-key-not-real")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://test:test@localhost:5432/test",
)
os.environ.setdefault("ALLOWED_ORIGINS", "http://localhost:5173")
os.environ.setdefault("ENV", "test")
