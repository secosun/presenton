from fastapi import APIRouter

from api.v1.ppt.endpoints.presentation import PRESENTATION_ROUTER
from api.v1.ppt.endpoints.files import FILES_ROUTER
from api.v1.ppt.endpoints.fonts import FONTS_ROUTER
from api.v1.ppt.endpoints.icons import ICONS_ROUTER
from api.v1.ppt.endpoints.theme import THEMES_ROUTER
from api.v1.ppt.endpoints.theme_generate import THEME_ROUTER


API_V1_PPT_ROUTER = APIRouter(prefix="/api/v1/ppt")

API_V1_PPT_ROUTER.include_router(FILES_ROUTER)
API_V1_PPT_ROUTER.include_router(FONTS_ROUTER)
API_V1_PPT_ROUTER.include_router(PRESENTATION_ROUTER)
API_V1_PPT_ROUTER.include_router(ICONS_ROUTER)
API_V1_PPT_ROUTER.include_router(THEME_ROUTER)
API_V1_PPT_ROUTER.include_router(THEMES_ROUTER)
