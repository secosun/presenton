import uuid
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

from models.presentation_and_path import PresentationPathAndEditPath


class MaterializeJobAccepted(BaseModel):
    job_id: uuid.UUID
    status: Literal["pending"] = "pending"


class MaterializeJobStatusResponse(BaseModel):
    job_id: uuid.UUID
    status: Literal["pending", "running", "completed", "failed"]
    created_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[PresentationPathAndEditPath] = None
    error: Optional[dict[str, Any]] = Field(
        default=None,
        description="Present when status=failed (detail, optional status_code)",
    )
