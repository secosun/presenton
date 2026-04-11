import json
from typing import Any

import jsonschema
from fastapi import HTTPException
from jsonschema import ValidationError

from models.materialize_presentation_request import (
    MaterializePresentationRequest,
    MaterializeSlideItem,
)


def materialize_outline_line(item: MaterializeSlideItem) -> str:
    if item.outline_summary:
        return item.outline_summary
    try:
        return json.dumps(item.content, ensure_ascii=False)[:500]
    except Exception:
        return ""


def materialize_derive_title(request: MaterializePresentationRequest) -> str:
    if request.title:
        return request.title
    for slide in request.slides:
        if slide.outline_summary:
            return slide.outline_summary[:200]
    if request.content.strip():
        return request.content.strip()[:200]
    return "Untitled"


def validate_slide_json_schema(
    layout_id: str,
    content: dict[str, Any],
    json_schema: dict | None,
) -> None:
    schema = json_schema if isinstance(json_schema, dict) else {}
    if not schema:
        return
    try:
        jsonschema.validate(instance=content, schema=schema)
    except ValidationError as e:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Slide content failed JSON Schema validation",
                "layout_id": layout_id,
                "errors": [{"path": list(e.path), "message": e.message}],
            },
        ) from e
