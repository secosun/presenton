from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Column, DateTime, String
from sqlmodel import Field, SQLModel

from utils.datetime_utils import get_current_utc_datetime


class MaterializeJobModel(SQLModel, table=True):
    __tablename__ = "materialize_jobs"

    id: str = Field(primary_key=True)
    status: str = Field(sa_column=Column(String, nullable=False, index=True))
    request: dict = Field(sa_column=Column(JSON, nullable=False), default_factory=dict)
    result: Optional[dict] = Field(sa_column=Column(JSON), default=None)
    error: Optional[dict] = Field(sa_column=Column(JSON), default=None)
    rq_job_id: Optional[str] = Field(
        sa_column=Column(String, nullable=True, index=True),
        default=None,
    )
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            default=get_current_utc_datetime,
        ),
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            default=get_current_utc_datetime,
            onupdate=get_current_utc_datetime,
        ),
    )
    started_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True),
        default=None,
    )
    completed_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True),
        default=None,
    )
