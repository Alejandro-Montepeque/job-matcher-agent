import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Analysis(Base):
    __tablename__ = "analyses"
    __table_args__ = (
        UniqueConstraint("cv_hash", "job_hash", name="uq_analysis_inputs"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    cv_hash: Mapped[str] = mapped_column(String(64), index=True)
    cv_filename: Mapped[str] = mapped_column(String(255))
    job_hash: Mapped[str] = mapped_column(String(64), index=True)
    job_posting: Mapped[str] = mapped_column(Text)

    match_score: Mapped[int] = mapped_column(Integer)
    summary: Mapped[str] = mapped_column(Text)
    matches: Mapped[list[Any]] = mapped_column(JSON, default=list)
    gaps: Mapped[list[Any]] = mapped_column(JSON, default=list)
    suggestions: Mapped[list[Any]] = mapped_column(JSON, default=list)
