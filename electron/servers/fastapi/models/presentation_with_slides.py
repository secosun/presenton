from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, field_serializer

from models.sql.slide import SlideModel


def _rfc3339_utc_millis_for_json_schema(value: datetime) -> str:
    """
    OpenAPI `format: date-time` + strict JSON Schema validators (e.g. MCP / FastMCP)
    expect RFC 3339 strings. Coerce to UTC, use `Z` suffix, and cap fractional
    seconds at milliseconds to avoid 6-digit microsecond tails some validators reject.
    """
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    else:
        value = value.astimezone(timezone.utc)
    base = value.strftime("%Y-%m-%dT%H:%M:%S")
    if value.microsecond:
        base += f".{value.microsecond // 1000:03d}"
    return f"{base}Z"


class PresentationWithSlides(BaseModel):
    id: uuid.UUID
    content: str
    n_slides: int
    language: str
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    tone: Optional[str] = None
    verbosity: Optional[str] = None
    slides: List[SlideModel]
    theme: Optional[dict] = None

    @field_serializer("created_at", "updated_at", when_used="always")
    def _serialize_rfc3339_utc(self, value: datetime) -> str:
        return _rfc3339_utc_millis_for_json_schema(value)
