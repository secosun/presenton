import asyncio
import os
import uuid
from typing import Annotated, List, Literal

import aiohttp
from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from constants.presentation import DEFAULT_TEMPLATES
from enums.webhook_event import WebhookEvent
from models.materialize_job_response import MaterializeJobAccepted, MaterializeJobStatusResponse
from models.materialize_presentation_request import MaterializePresentationRequest
from models.presentation_and_path import PresentationPathAndEditPath
from models.presentation_outline_model import (
    PresentationOutlineModel,
    SlideOutlineModel,
)
from models.pptx_models import PptxPresentationModel
from models.presentation_structure_model import PresentationStructureModel
from models.presentation_with_slides import PresentationWithSlides
from services.webhook_service import WebhookService
from utils.get_layout_by_name import get_layout_by_name
from utils.materialize_helpers import (
    materialize_derive_title,
    materialize_outline_line,
    validate_slide_json_schema,
)
from utils.template_validation import validate_presentation_template_name
from utils.export_utils import export_presentation
from services.database import async_session_maker, get_async_session
from services.materialize_job_store import get_materialize_job_store
from services.temp_file_service import TEMP_FILE_SERVICE
from services.concurrent_service import CONCURRENT_SERVICE
from models.sql.presentation import PresentationModel
from services.pptx_presentation_creator import PptxPresentationCreator
from models.sql.slide import SlideModel
from utils.asset_directory_utils import get_exports_directory


PRESENTATION_ROUTER = APIRouter(prefix="/presentation", tags=["Presentation"])


async def materialize_presentation_core(
    sql_session: AsyncSession,
    request: MaterializePresentationRequest,
) -> PresentationPathAndEditPath:
    """Persist structured slides and export (shared by sync /materialize and async jobs)."""
    template_key = request.template
    if template_key not in DEFAULT_TEMPLATES:
        template_key = template_key.lower()

    await validate_presentation_template_name(template_key, sql_session)

    if request.presentation_id is not None:
        existing = await sql_session.get(PresentationModel, request.presentation_id)
        if existing:
            raise HTTPException(
                status_code=409,
                detail="presentation_id already exists",
            )

    try:
        layout = await get_layout_by_name(template_key)
    except aiohttp.ClientConnectorError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Template service unavailable: {e!s}",
        ) from e

    presentation_id = request.presentation_id or uuid.uuid4()

    outline_slides = [
        SlideOutlineModel(content=materialize_outline_line(s)) for s in request.slides
    ]
    presentation_outline = PresentationOutlineModel(slides=outline_slides)

    structure_indices: List[int] = []
    for slide_req in request.slides:
        try:
            idx = layout.get_slide_layout_index(slide_req.layout_id)
        except HTTPException as e:
            if e.status_code == 404:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "message": "layout_id not found in template",
                        "layout_id": slide_req.layout_id,
                        "template": template_key,
                    },
                ) from e
            raise
        slide_def = layout.slides[idx]
        validate_slide_json_schema(
            slide_req.layout_id,
            slide_req.content,
            slide_def.json_schema,
        )
        structure_indices.append(idx)

    presentation_structure = PresentationStructureModel(slides=structure_indices)
    title = materialize_derive_title(request)

    presentation = PresentationModel(
        id=presentation_id,
        content=request.content or "",
        n_slides=len(request.slides),
        language=request.language,
        title=title,
        outlines=presentation_outline.model_dump(),
        layout=layout.model_dump(),
        structure=presentation_structure.model_dump(),
        tone=request.tone.value,
        verbosity=request.verbosity.value,
        instructions=request.instructions,
        include_table_of_contents=False,
        include_title_slide=True,
        web_search=False,
        theme=request.theme,
    )

    slides: List[SlideModel] = []
    for i, slide_req in enumerate(request.slides):
        slides.append(
            SlideModel(
                presentation=presentation_id,
                layout_group=layout.name,
                layout=slide_req.layout_id,
                index=i,
                speaker_note=slide_req.speaker_note,
                content=slide_req.content,
                html_content=slide_req.html_content,
                properties=slide_req.properties,
            )
        )

    sql_session.add(presentation)
    sql_session.add_all(slides)
    await sql_session.commit()

    presentation_and_path = await export_presentation(
        presentation_id,
        title,
        request.export_as,
    )

    return PresentationPathAndEditPath(
        **presentation_and_path.model_dump(),
        edit_path=f"/presentation?id={presentation_id}",
    )


def _http_error_payload(exc: HTTPException) -> dict:
    d = exc.detail
    if isinstance(d, dict):
        return {"detail": d, "status_code": exc.status_code}
    if isinstance(d, list):
        return {"detail": d, "status_code": exc.status_code}
    return {"detail": str(d), "status_code": exc.status_code}


async def _materialize_job_runner(job_id: str, payload: dict) -> None:
    store = get_materialize_job_store()
    try:
        await store.mark_running(job_id)
        req = MaterializePresentationRequest.model_validate(payload)
        async with async_session_maker() as sql_session:
            response = await materialize_presentation_core(sql_session, req)
        result_dict = response.model_dump(mode="json")
        await store.mark_completed(job_id, result_dict)
        CONCURRENT_SERVICE.run_task(
            None,
            WebhookService.send_webhook,
            WebhookEvent.PRESENTATION_GENERATION_COMPLETED,
            result_dict,
        )
    except HTTPException as exc:
        await store.mark_failed(job_id, _http_error_payload(exc))
    except Exception as exc:  # noqa: BLE001
        await store.mark_failed(
            job_id,
            {"detail": str(exc), "status_code": 500},
        )


@PRESENTATION_ROUTER.get("/all", response_model=List[PresentationWithSlides])
async def get_all_presentations(sql_session: AsyncSession = Depends(get_async_session)):
    presentations_with_slides = []

    query = (
        select(PresentationModel, SlideModel)
        .join(
            SlideModel,
            (SlideModel.presentation == PresentationModel.id) & (SlideModel.index == 0),
        )
        .order_by(PresentationModel.created_at.desc())
    )

    results = await sql_session.execute(query)
    rows = results.all()
    presentations_with_slides = [
        PresentationWithSlides(
            **presentation.model_dump(),
            slides=[first_slide],
        )
        for presentation, first_slide in rows
    ]
    return presentations_with_slides


@PRESENTATION_ROUTER.get("/{id}", response_model=PresentationWithSlides)
async def get_presentation(
    id: uuid.UUID, sql_session: AsyncSession = Depends(get_async_session)
):
    presentation = await sql_session.get(PresentationModel, id)
    if not presentation:
        raise HTTPException(404, "Presentation not found")
    slides = await sql_session.scalars(
        select(SlideModel)
        .where(SlideModel.presentation == id)
        .order_by(SlideModel.index)
    )
    return PresentationWithSlides(
        **presentation.model_dump(),
        slides=slides,
    )


@PRESENTATION_ROUTER.delete("/{id}", status_code=204)
async def delete_presentation(
    id: uuid.UUID, sql_session: AsyncSession = Depends(get_async_session)
):
    presentation = await sql_session.get(PresentationModel, id)
    if not presentation:
        raise HTTPException(404, "Presentation not found")

    await sql_session.delete(presentation)
    await sql_session.commit()


@PRESENTATION_ROUTER.post("/export/pptx", response_model=str)
async def export_presentation_as_pptx(
    pptx_model: Annotated[PptxPresentationModel, Body()],
):
    temp_dir = TEMP_FILE_SERVICE.create_temp_dir()

    pptx_creator = PptxPresentationCreator(pptx_model, temp_dir)
    await pptx_creator.create_ppt()

    export_directory = get_exports_directory()
    pptx_path = os.path.join(
        export_directory, f"{pptx_model.name or uuid.uuid4()}.pptx"
    )
    pptx_creator.save(pptx_path)

    return pptx_path


@PRESENTATION_ROUTER.post("/export", response_model=PresentationPathAndEditPath)
async def export_presentation_as_pptx_or_pdf(
    id: Annotated[uuid.UUID, Body(description="Presentation ID to export")],
    export_as: Annotated[
        Literal["pptx", "pdf"], Body(description="Format to export the presentation as")
    ] = "pptx",
    sql_session: AsyncSession = Depends(get_async_session),
):
    presentation = await sql_session.get(PresentationModel, id)

    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")

    presentation_and_path = await export_presentation(
        id,
        presentation.title or str(uuid.uuid4()),
        export_as,
    )

    return PresentationPathAndEditPath(
        **presentation_and_path.model_dump(),
        edit_path=f"/presentation?id={id}",
    )


@PRESENTATION_ROUTER.post(
    "/materialize/async",
    response_model=MaterializeJobAccepted,
    status_code=202,
)
async def start_materialize_presentation_job(
    request: MaterializePresentationRequest,
):
    """Enqueue materialize; poll GET .../materialize/jobs/{job_id} until completed or failed."""
    job_id = str(uuid.uuid4())
    store = get_materialize_job_store()
    await store.create(job_id, request.model_dump(mode="json"))
    asyncio.create_task(_materialize_job_runner(job_id, request.model_dump(mode="json")))
    return MaterializeJobAccepted(job_id=uuid.UUID(job_id))


@PRESENTATION_ROUTER.get(
    "/materialize/jobs/{job_id}",
    response_model=MaterializeJobStatusResponse,
)
async def get_materialize_job_status(job_id: uuid.UUID):
    rec = await get_materialize_job_store().get(str(job_id))
    if not rec:
        raise HTTPException(status_code=404, detail="job not found")
    result = None
    if rec.get("result"):
        result = PresentationPathAndEditPath(**rec["result"])
    return MaterializeJobStatusResponse(
        job_id=job_id,
        status=rec["status"],
        created_at=rec.get("created_at"),
        started_at=rec.get("started_at"),
        completed_at=rec.get("completed_at"),
        result=result,
        error=rec.get("error"),
    )


@PRESENTATION_ROUTER.post("/materialize", response_model=PresentationPathAndEditPath)
async def materialize_presentation_from_agent(
    request: MaterializePresentationRequest,
    sql_session: AsyncSession = Depends(get_async_session),
):
    """Persist fully structured slides and export; does not call any LLM (sync)."""
    response = await materialize_presentation_core(sql_session, request)
    CONCURRENT_SERVICE.run_task(
        None,
        WebhookService.send_webhook,
        WebhookEvent.PRESENTATION_GENERATION_COMPLETED,
        response.model_dump(mode="json"),
    )
    return response
