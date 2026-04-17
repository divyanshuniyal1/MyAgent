# shared/mcp_client.py
# Primary: fastmcp SDK Client (streamable-http).
# Fallback: raw JSON-RPC 2.0 over HTTP (uses shared/jsonrpc.py).

import os
from fastmcp import Client as MCPClient
from shared.jsonrpc import build_request, parse_response

MCP_URL = os.getenv("MCP_URL", "http://mcp:9000/mcp/")

async def call_mcp_tool(tool_name: str, params: dict):
    async with MCPClient(MCP_URL) as client:
        result = await client.call_tool(tool_name, params)
        if result and hasattr(result[0], "text"):
            return result[0].text
        return str(result)


# async def _call_mcp_jsonrpc(tool_name: str, params: dict):
#     """Raw JSON-RPC 2.0 fallback — uses shared/jsonrpc.py helpers."""
#     payload = build_request(
#         method="tools/call",
#         params={"name": tool_name, "arguments": params},
#     )
#     async with httpx.AsyncClient(timeout=30.0) as client:
#         resp = await client.post(MCP_HTTP_URL, json=payload)
#         resp.raise_for_status()
#         result = parse_response(resp.json())
#         # MCP tools/call result shape: {"content": [{"type": "text", "text": "..."}]}
#         if result and isinstance(result, dict):
#             content = result.get("content", [])
#             if content:
#                 return content[0].get("text", str(result))
#         return str(result)