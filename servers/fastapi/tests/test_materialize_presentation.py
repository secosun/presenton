import asyncio
import uuid
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from utils.export_utils import build_download_url, build_public_download_url
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
            "general:general-intro-slide",
            {},
            {
                "type": "object",
                "properties": {"title": {"type": "string"}},
                "required": ["title"],
            },
        )
    assert ei.value.status_code == 422


def test_layout_structure_indices():
    # Align ids with Presenton Next templates (general: + component layoutId).
    layout = PresentationLayoutModel(
        name="general",
        ordered=False,
        slides=[
            SlideLayoutModel(id="general:general-intro-slide", json_schema={}),
            SlideLayoutModel(id="general:basic-info-slide", json_schema={}),
        ],
    )
    assert layout.get_slide_layout_index("general:general-intro-slide") == 0
    assert layout.get_slide_layout_index("general:basic-info-slide") == 1


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


def test_build_public_download_url_replaces_origin(monkeypatch):
    monkeypatch.setenv("PRESENTON_PUBLIC_EXPORT_BASE", "https://ppt.example.com")
    internal = "http://192.168.3.58:5000/exports/E2E%20MCP%20Probe.pptx"
    assert build_public_download_url(internal) == (
        "https://ppt.example.com/exports/E2E%20MCP%20Probe.pptx"
    )


def test_build_public_download_url_alt_env_name(monkeypatch):
    monkeypatch.delenv("PRESENTON_PUBLIC_EXPORT_BASE", raising=False)
    monkeypatch.setenv("PRESENTON_PUBLIC_BASE_URL", "https://ppt.example.com")
    internal = "http://10.0.0.1:5000/exports/foo.pptx"
    assert build_public_download_url(internal) == "https://ppt.example.com/exports/foo.pptx"


def test_build_public_download_url_unset_env(monkeypatch):
    monkeypatch.delenv("PRESENTON_PUBLIC_EXPORT_BASE", raising=False)
    monkeypatch.delenv("PRESENTON_PUBLIC_BASE_URL", raising=False)
    assert build_public_download_url("http://x/exports/a.pptx") is None


def test_build_download_url_uses_presenton_host(monkeypatch):
    monkeypatch.setenv("PRESENTON_HOST", "10.0.0.2")
    monkeypatch.setenv("PRESENTON_PORT", "8080")
    u = build_download_url("/app_data/exports/My%20File.pptx")
    assert u == "http://10.0.0.2:8080/exports/My%20File.pptx"
