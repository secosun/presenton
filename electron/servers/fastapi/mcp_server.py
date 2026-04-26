import sys
import argparse
import asyncio
import json
import os
import traceback
from pathlib import Path
from typing import Any

import httpx
from fastmcp import FastMCP

_SPEC_DIR = Path(__file__).resolve().parent


def load_openapi_spec() -> dict[str, Any]:
    """
    OpenAPI 规范：默认用 FastAPI 运行时的全量 spec（与 HTTP /docs 一致，便于 Agent 发现全部能力）。

    环境变量 PRESENTON_MCP_OPENAPI_SOURCE:
      - app（默认）: 从 api.main:app 生成
      - file / json / legacy: 读取同目录 openai_spec.json（仅物化子集，用于离线/调试/兼容）
    """
    source = os.environ.get("PRESENTON_MCP_OPENAPI_SOURCE", "app").strip().lower()
    if source in ("file", "json", "legacy"):
        spec_path = _SPEC_DIR / "openai_spec.json"
        with open(spec_path, "r", encoding="utf-8") as f:
            return json.load(f)
    if source != "app":
        print(
            f"FATAL: invalid PRESENTON_MCP_OPENAPI_SOURCE={source!r} "
            "(use 'app' or 'file')",
            file=sys.stderr,
        )
        raise SystemExit(2)
    from api.main import app

    return app.openapi()


async def main():
    try:
        print("DEBUG: MCP (OpenAPI) Server startup initiated")
        parser = argparse.ArgumentParser(
            description="Run the MCP server (from OpenAPI)"
        )
        parser.add_argument(
            "--port", type=int, default=8001, help="Port for the MCP HTTP server"
        )

        parser.add_argument(
            "--name",
            type=str,
            default="Presenton API (OpenAPI)",
            help="Display name for the generated MCP server",
        )
        args = parser.parse_args()
        print(f"DEBUG: Parsed args - port={args.port}")

        api_base = os.environ.get("PRESENTON_API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
        timeout_s = float(os.environ.get("PRESENTON_HTTP_TIMEOUT", "120"))
        bind_host = os.environ.get("MCP_HTTP_HOST", "127.0.0.1")
        uvicorn_reload = os.environ.get("MCP_UVICORN_RELOAD", "0").strip() in ("1", "true", "yes")

        print(f"DEBUG: PRESENTON_API_BASE_URL -> {api_base} (timeout={timeout_s}s, bind={bind_host})")
        oa_src = os.environ.get("PRESENTON_MCP_OPENAPI_SOURCE", "app").strip().lower()
        print(f"DEBUG: OpenAPI spec source -> {oa_src or 'app'}")

        # HTTP client used by generated MCP tools to call Presenton FastAPI
        api_client = httpx.AsyncClient(base_url=api_base, timeout=timeout_s)

        openapi_spec = load_openapi_spec()
        n_paths = len(openapi_spec.get("paths", {}))
        print(f"DEBUG: OpenAPI paths loaded: {n_paths}")

        # Build MCP server from OpenAPI
        print("DEBUG: Creating FastMCP server from OpenAPI spec...")
        mcp = FastMCP.from_openapi(
            openapi_spec=openapi_spec,
            client=api_client,
            name=args.name,
        )
        print("DEBUG: MCP server created from OpenAPI successfully")

        uvicorn_config = {"reload": uvicorn_reload}
        print(f"DEBUG: Starting MCP server on host={bind_host}, port={args.port}")
        await mcp.run_async(
            transport="http",
            host=bind_host,
            port=args.port,
            uvicorn_config=uvicorn_config,
        )
        print("DEBUG: MCP server run_async completed")
    except Exception as e:
        print(f"ERROR: MCP server startup failed: {e}")
        print(f"ERROR: Traceback: {traceback.format_exc()}")
        raise


if __name__ == "__main__":
    print("DEBUG: Starting MCP (OpenAPI) main function")
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        print(f"FATAL TRACEBACK: {traceback.format_exc()}")
        sys.exit(1)
