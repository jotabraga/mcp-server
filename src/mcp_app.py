"""Builds the MCP `Server` shared by the stdio and SSE transports.

Keeping the Server (and its list_tools/call_tool handlers) in one place means both transports
expose the exact same tools and dispatch behaviour.
"""
from mcp.server import Server
from mcp.types import TextContent, Tool

from src.dispatch import execute_tool
from src.tools_registry import TOOLS


def build_mcp_server(name: str = "mcp-server") -> Server:
    server = Server(name)

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [tool.get_tool_input_schema() for tool in TOOLS.values()]

    @server.call_tool()
    async def call_tool(tool_name: str, arguments: dict) -> list[TextContent]:
        return [TextContent(type="text", text=execute_tool(tool_name, arguments))]

    return server
