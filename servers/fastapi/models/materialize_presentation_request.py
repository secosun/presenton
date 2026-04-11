from typing import Any, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from enums.tone import Tone
from enums.verbosity import Verbosity


class MaterializeSlideItem(BaseModel):
    layout_id: str
    content: dict[str, Any]
    outline_summary: Optional[str] = None
    speaker_note: Optional[str] = None
    html_content: Optional[str] = None
    properties: Optional[dict[str, Any]] = None


class MaterializePresentationRequest(BaseModel):
    """Structured slides from an external agent; no server-side LLM."""

    schema_version: Optional[str] = Field(
        default=None,
        description="Contract version; use 1.0 or omit",
    )
    template: str
    slides: List[MaterializeSlideItem]
    export_as: Literal["pptx", "pdf"]
    language: str = "English"
    title: Optional[str] = None
    presentation_id: Optional[UUID] = None
    content: str = Field(
        default="",
        description="Whole-document summary for audit/UI; not used for generation",
    )
    instructions: Optional[str] = None
    tone: Tone = Tone.DEFAULT
    verbosity: Verbosity = Verbosity.STANDARD
    theme: Optional[dict] = None

    @model_validator(mode="after")
    def _slides_nonempty(self) -> "MaterializePresentationRequest":
        if not self.slides:
            raise ValueError("slides must contain at least one slide")
        return self

    @model_validator(mode="after")
    def _schema_version_supported(self) -> "MaterializePresentationRequest":
        if self.schema_version is not None and self.schema_version not in ("1.0",):
            raise ValueError("Unsupported schema_version; use 1.0 or omit")
        return self
