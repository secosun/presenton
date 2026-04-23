import uuid
from typing import Optional

from pydantic import BaseModel


class PresentationAndPath(BaseModel):
    presentation_id: uuid.UUID
    path: str
    download_url: str  # 远程下载 URL（通过 Nginx 代理，多为内网 origin）
    # 与 download_url 同 path；公网 HTTPS（环境变量 PRESENTON_PUBLIC_EXPORT_BASE）
    download_url_public: Optional[str] = None


class PresentationPathAndEditPath(PresentationAndPath):
    edit_path: str
