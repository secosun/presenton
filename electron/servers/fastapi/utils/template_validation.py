import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from constants.presentation import DEFAULT_TEMPLATES
from models.sql.template import TemplateModel


async def validate_presentation_template_name(
    template: str,
    sql_session: AsyncSession,
) -> None:
    """Ensure template exists: built-in name or custom-{uuid} in DB."""
    if template in DEFAULT_TEMPLATES:
        return
    tl = template.lower()
    if not tl.startswith("custom-"):
        raise HTTPException(
            status_code=400,
            detail="Template not found. Please use a valid template.",
        )
    template_id = tl.replace("custom-", "")
    try:
        row = await sql_session.get(TemplateModel, uuid.UUID(template_id))
        if not row:
            raise Exception()
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Template not found. Please use a valid template.",
        ) from None
