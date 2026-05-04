"""
Regression: MCP / JSON Schema `format: date-time` validation on
GET /presentation/all (PresentationWithSlides) needs RFC 3339 UTC with Z.
"""

import re
import uuid
from datetime import datetime, timedelta, timezone

from models.presentation_with_slides import (
    PresentationWithSlides,
    _rfc3339_utc_millis_for_json_schema,
)
from models.sql.slide import SlideModel

# RFC 3339 profile used in responses: optional .mmm before Z, no 6-digit micros.
_RFC3339_Z_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z$"
)


def test_rfc3339_helper_utc_z_and_millis() -> None:
    assert _rfc3339_utc_millis_for_json_schema(
        datetime(2020, 1, 2, 3, 4, 5, 123_000, tzinfo=timezone.utc)
    ) == "2020-01-02T03:04:05.123Z"
    assert _rfc3339_utc_millis_for_json_schema(
        datetime(2020, 1, 2, 3, 4, 5, 0, tzinfo=timezone.utc)
    ) == "2020-01-02T03:04:05Z"
    # Naive → treated as UTC
    assert _rfc3339_utc_millis_for_json_schema(
        datetime(2019, 6, 15, 12, 0, 0)
    ) == "2019-06-15T12:00:00Z"
    # Non-UTC offset → normalized to Z
    assert _rfc3339_utc_millis_for_json_schema(
        datetime(2020, 1, 1, 1, 0, 0, tzinfo=timezone(timedelta(hours=8)))
    ) == "2019-12-31T17:00:00Z"


def _slide_for(pid: uuid.UUID) -> SlideModel:
    return SlideModel(
        id=uuid.uuid4(),
        presentation=pid,
        layout_group="general",
        layout="general:intro",
        index=0,
        content={},
        html_content=None,
    )


def test_presentation_with_slides_model_dump_uses_rfc3339_strings() -> None:
    pid = uuid.uuid4()
    created = datetime(2020, 1, 1, 0, 0, 0, 456_000, tzinfo=timezone.utc)
    updated = datetime(2020, 1, 2, 0, 0, 0, tzinfo=timezone.utc)
    pws = PresentationWithSlides(
        id=pid,
        content="x",
        n_slides=1,
        language="en",
        title=None,
        created_at=created,
        updated_at=updated,
        slides=[_slide_for(pid)],
    )
    d = pws.model_dump()
    assert isinstance(d["created_at"], str)
    assert isinstance(d["updated_at"], str)
    assert d["created_at"] == "2020-01-01T00:00:00.456Z"
    assert d["updated_at"] == "2020-01-02T00:00:00Z"
    assert _RFC3339_Z_RE.match(d["created_at"])
    assert _RFC3339_Z_RE.match(d["updated_at"])

    dj = pws.model_dump(mode="json")
    assert dj["created_at"] == d["created_at"]
    assert dj["updated_at"] == d["updated_at"]


def test_jsonschema_format_date_time_accepts_serialized_values() -> None:
    from jsonschema import Draft202012Validator
    from jsonschema.exceptions import ValidationError

    schema = {
        "type": "object",
        "properties": {
            "created_at": {"type": "string", "format": "date-time"},
            "updated_at": {"type": "string", "format": "date-time"},
        },
        "required": ["created_at", "updated_at"],
    }
    pid = uuid.uuid4()
    pws = PresentationWithSlides(
        id=pid,
        content="x",
        n_slides=1,
        language="en",
        created_at=datetime(2020, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        updated_at=datetime(2020, 1, 2, 0, 0, 0, 999_000, tzinfo=timezone.utc),
        slides=[_slide_for(pid)],
    )
    payload = {
        "created_at": pws.model_dump()["created_at"],
        "updated_at": pws.model_dump()["updated_at"],
    }
    v = Draft202012Validator(schema, format_checker=Draft202012Validator.FORMAT_CHECKER)
    try:
        v.validate(payload)
    except ValidationError as e:
        raise AssertionError(
            f"date-time should validate: {payload!r}: {e.message}"
        ) from e
