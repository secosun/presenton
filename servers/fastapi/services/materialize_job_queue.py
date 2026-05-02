from __future__ import annotations

import asyncio
import os
from typing import Any

from fastapi import HTTPException
from redis import Redis

from enums.webhook_event import WebhookEvent
from models.materialize_presentation_request import MaterializePresentationRequest
from services.concurrent_service import CONCURRENT_SERVICE
from services.database import async_session_maker
from services.materialize_job_store import MaterializeJobStore
from services.webhook_service import WebhookService


DEFAULT_MATERIALIZE_QUEUE_NAME = "presenton-materialize"


def get_materialize_redis_url() -> str:
    return os.environ.get("PRESENTON_REDIS_URL") or os.environ.get(
        "REDIS_URL",
        "redis://localhost:6379/0",
    )


def get_materialize_queue_name() -> str:
    return os.environ.get("PRESENTON_MATERIALIZE_QUEUE", DEFAULT_MATERIALIZE_QUEUE_NAME)


def get_materialize_job_timeout_seconds() -> int:
    raw = os.environ.get("PRESENTON_MATERIALIZE_JOB_TIMEOUT", "1800")
    try:
        return max(30, int(raw))
    except ValueError:
        return 1800


def _http_error_payload(exc: HTTPException) -> dict[str, Any]:
    d = exc.detail
    if isinstance(d, dict):
        return {"detail": d, "status_code": exc.status_code}
    if isinstance(d, list):
        return {"detail": d, "status_code": exc.status_code}
    return {"detail": str(d), "status_code": exc.status_code}


def enqueue_materialize_job(job_id: str, payload: dict[str, Any]) -> str:
    from rq import Queue

    redis_conn = Redis.from_url(get_materialize_redis_url())
    queue = Queue(get_materialize_queue_name(), connection=redis_conn)
    rq_job = queue.enqueue(
        "services.materialize_job_queue.run_materialize_job",
        job_id,
        payload,
        job_id=f"materialize-{job_id}",
        job_timeout=get_materialize_job_timeout_seconds(),
        result_ttl=86400,
        failure_ttl=604800,
    )
    return rq_job.id


def run_materialize_job(job_id: str, payload: dict[str, Any]) -> None:
    asyncio.run(_run_materialize_job_async(job_id, payload))


async def _mark_failed(job_id: str, error: dict[str, Any]) -> None:
    async with async_session_maker() as sql_session:
        await MaterializeJobStore(sql_session).mark_failed(job_id, error)


async def _run_materialize_job_async(job_id: str, payload: dict[str, Any]) -> None:
    try:
        async with async_session_maker() as sql_session:
            await MaterializeJobStore(sql_session).mark_running(job_id)

        req = MaterializePresentationRequest.model_validate(payload)
        from api.v1.ppt.endpoints.presentation import materialize_presentation_core

        async with async_session_maker() as sql_session:
            response = await materialize_presentation_core(sql_session, req)

        result_dict = response.model_dump(mode="json")
        async with async_session_maker() as sql_session:
            await MaterializeJobStore(sql_session).mark_completed(job_id, result_dict)

        CONCURRENT_SERVICE.run_task(
            None,
            WebhookService.send_webhook,
            WebhookEvent.PRESENTATION_GENERATION_COMPLETED,
            result_dict,
        )
    except HTTPException as exc:
        await _mark_failed(job_id, _http_error_payload(exc))
        raise
    except Exception as exc:
        await _mark_failed(job_id, {"detail": str(exc), "status_code": 500})
        raise
