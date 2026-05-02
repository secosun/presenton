"""Persistent store for async materialize jobs."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from models.sql.materialize_job import MaterializeJobModel
from utils.datetime_utils import get_current_utc_datetime


def _dt_to_iso(value: Optional[datetime]) -> Optional[str]:
    return value.isoformat() if value else None


def _model_to_dict(job: MaterializeJobModel) -> dict[str, Any]:
    return {
        "job_id": job.id,
        "status": job.status,
        "created_at": _dt_to_iso(job.created_at),
        "updated_at": _dt_to_iso(job.updated_at),
        "started_at": _dt_to_iso(job.started_at),
        "completed_at": _dt_to_iso(job.completed_at),
        "request": job.request,
        "result": job.result,
        "error": job.error,
        "rq_job_id": job.rq_job_id,
    }


class MaterializeJobStore:
    def __init__(self, sql_session: AsyncSession) -> None:
        self._session = sql_session

    async def create(self, job_id: str, request_payload: dict[str, Any]) -> None:
        self._session.add(
            MaterializeJobModel(
                id=job_id,
                status="pending",
                request=request_payload,
            )
        )
        await self._session.commit()

    async def attach_queue_job(self, job_id: str, rq_job_id: str) -> None:
        rec = await self._session.get(MaterializeJobModel, job_id)
        if rec:
            rec.rq_job_id = rq_job_id
            rec.updated_at = get_current_utc_datetime()
            self._session.add(rec)
            await self._session.commit()

    async def mark_running(self, job_id: str) -> None:
        rec = await self._session.get(MaterializeJobModel, job_id)
        if rec:
            rec.status = "running"
            rec.started_at = rec.started_at or get_current_utc_datetime()
            rec.updated_at = get_current_utc_datetime()
            self._session.add(rec)
            await self._session.commit()

    async def mark_completed(self, job_id: str, result: dict[str, Any]) -> None:
        rec = await self._session.get(MaterializeJobModel, job_id)
        if rec:
            rec.status = "completed"
            rec.result = result
            rec.error = None
            rec.completed_at = get_current_utc_datetime()
            rec.updated_at = get_current_utc_datetime()
            self._session.add(rec)
            await self._session.commit()

    async def mark_failed(self, job_id: str, error: dict[str, Any]) -> None:
        rec = await self._session.get(MaterializeJobModel, job_id)
        if rec:
            rec.status = "failed"
            rec.error = error
            rec.completed_at = get_current_utc_datetime()
            rec.updated_at = get_current_utc_datetime()
            self._session.add(rec)
            await self._session.commit()

    async def get(self, job_id: str) -> Optional[dict[str, Any]]:
        rec = await self._session.get(MaterializeJobModel, job_id)
        return _model_to_dict(rec) if rec else None
