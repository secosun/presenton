import sys
import argparse
import asyncio
import json
import os
import traceback
from pathlib import Path

import httpx
from fastmcp import FastMCP

_SPEC_DIR = Path(__file__).resolve().parent
with open(_SPEC_DIR / "openai_spec.json", "r", encoding="utf-8") as f:
    openapi_spec = json.load(f)


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

        api_client = httpx.AsyncClient(base_url=api_base, timeout=timeout_s)

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
