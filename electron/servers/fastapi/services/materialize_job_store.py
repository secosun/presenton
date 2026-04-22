"""In-memory store for async materialize jobs (MCP / long-running friendly)."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Optional


class MaterializeJobStore:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._jobs: dict[str, dict[str, Any]] = {}

    async def create(self, job_id: str, request_payload: dict[str, Any]) -> None:
        async with self._lock:
            self._jobs[job_id] = {
                "job_id": job_id,
                "status": "pending",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "request": request_payload,
                "result": None,
                "error": None,
                "started_at": None,
                "completed_at": None,
            }

    async def mark_running(self, job_id: str) -> None:
        async with self._lock:
            rec = self._jobs.get(job_id)
            if rec:
                rec["status"] = "running"
                rec["started_at"] = datetime.now(timezone.utc).isoformat()

    async def mark_completed(self, job_id: str, result: dict[str, Any]) -> None:
        async with self._lock:
            rec = self._jobs.get(job_id)
            if rec:
                rec["status"] = "completed"
                rec["result"] = result
                rec["completed_at"] = datetime.now(timezone.utc).isoformat()

    async def mark_failed(self, job_id: str, error: dict[str, Any]) -> None:
        async with self._lock:
            rec = self._jobs.get(job_id)
            if rec:
                rec["status"] = "failed"
                rec["error"] = error
                rec["completed_at"] = datetime.now(timezone.utc).isoformat()

    async def get(self, job_id: str) -> Optional[dict[str, Any]]:
        async with self._lock:
            rec = self._jobs.get(job_id)
            return dict(rec) if rec else None


_store: Optional[MaterializeJobStore] = None


def get_materialize_job_store() -> MaterializeJobStore:
    global _store
    if _store is None:
        _store = MaterializeJobStore()
    return _store
