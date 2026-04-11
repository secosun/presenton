import asyncio
import uuid
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from models.materialize_presentation_request import (
    MaterializePresentationRequest,
    MaterializeSlideItem,
)
from models.presentation_layout import PresentationLayoutModel, SlideLayoutModel
from utils.materialize_helpers import (
    materialize_derive_title,
    materialize_outline_line,
    validate_slide_json_schema,
)
from utils.template_validation import validate_presentation_template_name


def test_materialize_outline_line_prefers_summary():
    item = MaterializeSlideItem(
        layout_id="a",
        content={"x": 1},
        outline_summary="hello",
    )
    assert materialize_outline_line(item) == "hello"


def test_materialize_derive_title_chain():
    req = MaterializePresentationRequest(
        template="general",
        slides=[
            MaterializeSlideItem(layout_id="a", content={}),
        ],
        export_as="pptx",
    )
    assert materialize_derive_title(req) == "Untitled"

    req2 = MaterializePresentationRequest(
        template="general",
        slides=[
            MaterializeSlideItem(
                layout_id="a",
                content={},
                outline_summary="first slide title",
            ),
        ],
        export_as="pptx",
    )
    assert materialize_derive_title(req2) == "first slide title"


def test_validate_slide_json_schema_empty_schema_ok():
    validate_slide_json_schema("lid", {"any": "thing"}, None)
    validate_slide_json_schema("lid", {}, {})


def test_validate_slide_json_schema_fail():
    with pytest.raises(HTTPException) as ei:
        validate_slide_json_schema(
            "slide_a",
            {},
            {
                "type": "object",
                "properties": {"title": {"type": "string"}},
                "required": ["title"],
            },
        )
    assert ei.value.status_code == 422


def test_layout_structure_indices():
    layout = PresentationLayoutModel(
        name="general",
        ordered=False,
        slides=[
            SlideLayoutModel(id="slide_a", json_schema={}),
            SlideLayoutModel(id="slide_b", json_schema={}),
        ],
    )
    assert layout.get_slide_layout_index("slide_a") == 0
    assert layout.get_slide_layout_index("slide_b") == 1


def test_validate_presentation_template_name_builtin():
    session = AsyncMock()
    asyncio.run(validate_presentation_template_name("general", session))


def test_validate_presentation_template_name_unknown():
    session = AsyncMock()
    with pytest.raises(HTTPException) as ei:
        asyncio.run(validate_presentation_template_name("not-a-template", session))
    assert ei.value.status_code == 400


def test_validate_presentation_template_name_custom_missing():
    session = AsyncMock()
    session.get = AsyncMock(return_value=None)
    with pytest.raises(HTTPException) as ei:
        asyncio.run(
            validate_presentation_template_name(
                "custom-" + str(uuid.uuid4()),
                session,
            )
        )
    assert ei.value.status_code == 400
