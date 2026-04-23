import json
import os
import uuid
from typing import Literal
from urllib.parse import urlparse

import aiohttp
from fastapi import HTTPException
from pathvalidate import sanitize_filename

from models.pptx_models import PptxPresentationModel
from models.presentation_and_path import PresentationAndPath
from services.pptx_presentation_creator import PptxPresentationCreator
from services.temp_file_service import TEMP_FILE_SERVICE
from utils.asset_directory_utils import get_exports_directory

def _presenton_export_origin() -> tuple[str, str]:
    """内网导出 URL 的 host:port（每次调用读取环境变量，便于测试与无需重载进程改配置）。"""
    host = os.environ.get("PRESENTON_HOST", "192.168.3.58")
    port = os.environ.get("PRESENTON_PORT", "5000")
    return host, port


def build_download_url(container_path: str) -> str:
    """将容器路径转换为远程下载 URL"""
    # 容器路径 /app_data/exports/xxx.pptx → URL 路径 /exports/xxx.pptx
    file_name = os.path.basename(container_path)
    host, port = _presenton_export_origin()
    return f"http://{host}:{port}/exports/{file_name}"


def build_public_download_url(internal_download_url: str) -> str | None:
    """与内网 download_url 同 path，仅替换为公网 origin（无尾斜杠）。与 OpenClaw PRESENTON_PUBLIC_EXPORT_BASE 对齐。"""
    raw = (
        os.environ.get("PRESENTON_PUBLIC_EXPORT_BASE", "").strip()
        or os.environ.get("PRESENTON_PUBLIC_BASE_URL", "").strip()
    )
    if not raw or not internal_download_url:
        return None
    base = raw.rstrip("/")
    try:
        p = urlparse(internal_download_url)
        return f"{base}{p.path}" + (f"?{p.query}" if p.query else "")
    except Exception:
        return None


async def export_presentation(
    presentation_id: uuid.UUID, title: str, export_as: Literal["pptx", "pdf"]
) -> PresentationAndPath:
    if export_as == "pptx":

        # Get the converted PPTX model from the Next.js service
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"http://localhost/api/presentation_to_pptx_model?id={presentation_id}"
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    print(f"Failed to get PPTX model: {error_text}")
                    raise HTTPException(
                        status_code=500,
                        detail="Failed to convert presentation to PPTX model",
                    )
                pptx_model_data = await response.json()

        # Create PPTX file using the converted model
        pptx_model = PptxPresentationModel(**pptx_model_data)
        temp_dir = TEMP_FILE_SERVICE.create_temp_dir()
        pptx_creator = PptxPresentationCreator(pptx_model, temp_dir)
        await pptx_creator.create_ppt()

        export_directory = get_exports_directory()
        pptx_path = os.path.join(
            export_directory,
            f"{sanitize_filename(title or str(uuid.uuid4()))}.pptx",
        )
        pptx_creator.save(pptx_path)

        internal = build_download_url(pptx_path)
        return PresentationAndPath(
            presentation_id=presentation_id,
            path=pptx_path,
            download_url=internal,
            download_url_public=build_public_download_url(internal),
        )
    else:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost/api/export-as-pdf",
                json={
                    "id": str(presentation_id),
                    "title": sanitize_filename(title or str(uuid.uuid4())),
                },
            ) as response:
                response_json = await response.json()

        internal = build_download_url(response_json["path"])
        return PresentationAndPath(
            presentation_id=presentation_id,
            path=response_json["path"],
            download_url=internal,
            download_url_public=build_public_download_url(internal),
        )
