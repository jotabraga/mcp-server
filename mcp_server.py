"""stdio entrypoint for MCP clients.

Not network-exposed, so HTTP auth is not required here. Tool logic is shared via
`execute_tool`, keeping stdio and HTTP behaviour identical.
"""
import asyncio
import logging

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from src.dispatch import execute_tool
from src.logging_config import configure_logging
from src.settings import load_settings
from src.tools_registry import TOOLS

logger = logging.getLogger(__name__)
app = Server("mcp-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [tool.get_tool_input_schema() for tool in TOOLS.values()]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    return [TextContent(type="text", text=execute_tool(name, arguments))]


async def main() -> None:
    load_dotenv()
    settings = load_settings(require_http_auth=False)
    configure_logging(settings.log_level)
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
