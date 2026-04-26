"""将 Next App Router 的若干 JSON API 经 FastAPI 统一暴露，便于 /openapi.json 与 MCP 工具发现。"""

from __future__ import annotations

from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Query

from utils.get_env import get_nextjs_base_url, get_nextjs_request_timeout_seconds

API_V1_NEXTJS_PROXY_ROUTER = APIRouter(
    prefix="/api/v1/nextjs",
    tags=["Nextjs"],
)


def _fail_if_http_error(r: httpx.Response) -> None:
    if r.status_code < 400:
        return
    try:
        detail: Any = r.json()
    except Exception:
        detail = r.text
    raise HTTPException(status_code=r.status_code, detail=detail)


async def _get_json(
    next_path: str, *, timeout: float, params: dict[str, str] | None = None
) -> Any:
    """next_path 以 / 开头，例如 /api/template。"""
    base = get_nextjs_base_url().rstrip("/")
    url = f"{base}{next_path}"
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.get(url, params=params)
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Next.js 不可达: {e!s}",
        ) from e
    _fail_if_http_error(r)
    return r.json()


@API_V1_NEXTJS_PROXY_ROUTER.get(
    "/template",
    operation_id="get_nextjs_template",
    summary="Next /api/template：某模板下全部 slide 的 id、name、json_schema（物化前对照填 content）",
    description=(
        "透传至 Next 的 /api/template?group=…。Next 内部用 headless 拉取 schema 页，可能较慢；"
        "超时见 PRESENTON_NEXTJS_HTTP_TIMEOUT（默认 300s）。"
    ),
)
async def get_nextjs_template(
    group: str = Query(
        ...,
        description="与 materialize 请求中的 template 相同，如 general 或 custom-uuid。",
    ),
) -> Any:
    return await _get_json(
        "/api/template",
        timeout=get_nextjs_request_timeout_seconds(),
        params={"group": group},
    )


@API_V1_NEXTJS_PROXY_ROUTER.get(
    "/templates",
    operation_id="list_nextjs_presentation_templates",
    summary="Next /api/templates：扫描 presentation-templates 下模板目录、layout 文件名与 settings。",
    description="用于枚举可用 template 名，与 get_nextjs_template 配合。",
)
async def list_nextjs_presentation_templates() -> Any:
    t = min(get_nextjs_request_timeout_seconds(), 120.0)
    return await _get_json("/api/templates", timeout=t)


@API_V1_NEXTJS_PROXY_ROUTER.get(
    "/has-required-key",
    operation_id="get_nextjs_has_openai_key",
    summary="Next /api/has-required-key：是否已配置 OpenAI 密钥（仅 hasKey 布尔，不含密钥）",
    description="对纯物化无硬性要求；可用来判断 UI/内置 LLM 能力是否可用。",
)
async def get_nextjs_has_openai_key() -> Any:
    return await _get_json("/api/has-required-key", timeout=15.0)
