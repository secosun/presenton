import sys
import argparse
import asyncio
import traceback
import os

import httpx
from fastmcp import FastMCP
import json

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
openapi_spec_path = os.path.join(script_dir, "openai_spec.json")

with open(openapi_spec_path, "r") as f:
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

        # Create an HTTP client that the MCP server will use to call the API
        # Use PRESENTON_API_BASE_URL env var if set, otherwise default to container-internal API
        presenton_api_url = os.environ.get("PRESENTON_API_BASE_URL", "http://127.0.0.1:8000")
        print(f"DEBUG: Using Presenton API URL: {presenton_api_url}")
        api_client = httpx.AsyncClient(base_url=presenton_api_url, timeout=60.0)

        # Build MCP server from OpenAPI
        print("DEBUG: Creating FastMCP server from OpenAPI spec...")
        mcp = FastMCP.from_openapi(
            openapi_spec=openapi_spec,
            client=api_client,
            name=args.name,
        )
        print("DEBUG: MCP server created from OpenAPI successfully")

        # Start the MCP server
        uvicorn_config = {"reload": True}
        print(f"DEBUG: Starting MCP server on host=0.0.0.0, port={args.port}")
        await mcp.run_async(
            transport="http",
            host="0.0.0.0",
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
