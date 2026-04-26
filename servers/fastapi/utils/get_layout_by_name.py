import aiohttp
from fastapi import HTTPException
from models.presentation_layout import PresentationLayoutModel
from typing import List

from utils.get_env import get_nextjs_base_url, get_nextjs_request_timeout_seconds

async def get_layout_by_name(layout_name: str) -> PresentationLayoutModel:
    base = get_nextjs_base_url()
    url = f"{base}/api/template?group={layout_name}"
    t = aiohttp.ClientTimeout(total=get_nextjs_request_timeout_seconds())
    async with aiohttp.ClientSession(timeout=t) as session:
        async with session.get(url) as response:
            if response.status != 200:
                error_text = await response.text()
                raise HTTPException(
                    status_code=404,
                    detail=f"Template '{layout_name}' not found: {error_text}"
                )
            layout_json = await response.json()
    # Parse the JSON into your Pydantic model
    return PresentationLayoutModel(**layout_json)
