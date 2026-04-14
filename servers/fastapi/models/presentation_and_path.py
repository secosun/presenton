from pydantic import BaseModel
import uuid


class PresentationAndPath(BaseModel):
    presentation_id: uuid.UUID
    path: str
    download_url: str  # 远程下载 URL（通过 Nginx 代理）


class PresentationPathAndEditPath(PresentationAndPath):
    edit_path: str
