#!/bin/bash
# Start Presenton MCP Server in development mode

set -e

CONTAINER_NAME="presenton_development_1"
MCP_PORT=8001

echo "=== Presenton MCP Server Starter ==="

# Check if container is running
if ! docker ps | grep -q "$CONTAINER_NAME"; then
    echo "ERROR: Container $CONTAINER_NAME is not running"
    echo "Start it with: docker-compose up development -d"
    exit 1
fi

echo "1. Stopping existing MCP server (if any)..."
docker exec $CONTAINER_NAME pkill -f "mcp_server.py" 2>/dev/null || true
sleep 1

echo "2. Starting MCP server on port $MCP_PORT..."
docker exec -d -w /app/servers/fastapi $CONTAINER_NAME python /app/servers/fastapi/mcp_server.py --port $MCP_PORT --name "Presenton"

sleep 3

echo "3. Verifying MCP server is running..."
if docker exec $CONTAINER_NAME netstat -tlnp 2>/dev/null | grep -q ":$MCP_PORT"; then
    echo "SUCCESS: MCP server is running on port $MCP_PORT"
    echo ""
    echo "=== Connection Info ==="
    echo "MCP HTTP Endpoint: http://localhost:$MCP_PORT/mcp"
    echo "Transport: HTTP (SSE)"
    echo ""
    echo "=== OpenClaw/Cursor Configuration ==="
    echo "Add to your MCP settings:"
    echo '{
  "mcpServers": {
    "presenton": {
      "url": "http://localhost:'$MCP_PORT'/mcp",
      "transport": "http",
      "name": "Presenton PPT Generator"
    }
  }
}'
    echo ""
    echo "=== Testing API connectivity ==="
    docker exec $CONTAINER_NAME curl -s http://localhost:8000/docs | head -c 100
    echo "..."
    echo ""
    echo "NOTE: To expose MCP to external hosts, update docker-compose.yml:"
    echo "  services:"
    echo "    development:"
    echo "      ports:"
    echo "        - \"5000:80\"      # Presenton Web UI"
    echo "        - \"1455:1455\"    # OAuth callback"
    echo "        - \"8001:8001\"    # MCP Server (add this)"
else
    echo "ERROR: MCP server failed to start"
    docker exec $CONTAINER_NAME python /app/servers/fastapi/mcp_server.py --port $MCP_PORT 2>&1 | tail -20
    exit 1
fi
