"""add materialize jobs

Revision ID: 5c6e2a7d8f91
Revises: 82abdbc476a7
Create Date: 2026-05-02 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "5c6e2a7d8f91"
down_revision: Union[str, None] = "82abdbc476a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "materialize_jobs",
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("request", sa.JSON(), nullable=False),
        sa.Column("result", sa.JSON(), nullable=True),
        sa.Column("error", sa.JSON(), nullable=True),
        sa.Column("rq_job_id", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_materialize_jobs_rq_job_id"),
        "materialize_jobs",
        ["rq_job_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_materialize_jobs_status"),
        "materialize_jobs",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_materialize_jobs_status"), table_name="materialize_jobs")
    op.drop_index(op.f("ix_materialize_jobs_rq_job_id"), table_name="materialize_jobs")
    op.drop_table("materialize_jobs")
