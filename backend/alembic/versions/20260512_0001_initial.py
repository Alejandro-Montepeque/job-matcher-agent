"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-05-12

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "analyses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("cv_hash", sa.String(64), nullable=False),
        sa.Column("cv_filename", sa.String(255), nullable=False),
        sa.Column("job_hash", sa.String(64), nullable=False),
        sa.Column("job_posting", sa.Text(), nullable=False),
        sa.Column("match_score", sa.Integer(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("matches", sa.JSON(), nullable=False),
        sa.Column("gaps", sa.JSON(), nullable=False),
        sa.Column("suggestions", sa.JSON(), nullable=False),
        sa.UniqueConstraint("cv_hash", "job_hash", name="uq_analysis_inputs"),
    )
    op.create_index("ix_analyses_created_at", "analyses", ["created_at"])
    op.create_index("ix_analyses_cv_hash", "analyses", ["cv_hash"])
    op.create_index("ix_analyses_job_hash", "analyses", ["job_hash"])


def downgrade() -> None:
    op.drop_index("ix_analyses_job_hash", table_name="analyses")
    op.drop_index("ix_analyses_cv_hash", table_name="analyses")
    op.drop_index("ix_analyses_created_at", table_name="analyses")
    op.drop_table("analyses")
