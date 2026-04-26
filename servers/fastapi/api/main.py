from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.lifespan import app_lifespan
from api.middlewares import UserConfigEnvUpdateMiddleware
from api.v1.ppt.router import API_V1_PPT_ROUTER
from api.v1.webhook.router import API_V1_WEBHOOK_ROUTER
from api.v1.mock.router import API_V1_MOCK_ROUTER
from api.v1.nextjs_proxy.router import API_V1_NEXTJS_PROXY_ROUTER


app = FastAPI(
    lifespan=app_lifespan,
    title="Presenton API",
    version="0.1.0",
    description=(
        "PPT 物化、模板/主题、文件、Webhook、Next 模板/版式发现（/api/v1/nextjs/*）等；"
        "MCP 由本 OpenAPI 全量生成，与 /docs 一致。"
    ),
)


@app.get("/api/v1/healthz", tags=["Health"])
async def presenton_api_healthz():
    """Liveness for Nginx :5000 → /api/v1/* → FastAPI (Agent 容器内 HTTP 探活)."""
    return {"ok": True, "status": "live", "service": "presenton-fastapi"}


# Routers
app.include_router(API_V1_PPT_ROUTER)
app.include_router(API_V1_WEBHOOK_ROUTER)
app.include_router(API_V1_MOCK_ROUTER)
app.include_router(API_V1_NEXTJS_PROXY_ROUTER)

# Middlewares
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(UserConfigEnvUpdateMiddleware)
