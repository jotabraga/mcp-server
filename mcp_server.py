"""stdio entrypoint for MCP clients.

Not network-exposed, so HTTP auth is not required here. Tool logic is shared via
`execute_tool`, and the MCP Server is built by the shared factory, keeping stdio and SSE
behaviour identical.
"""
import asyncio
import logging

from dotenv import load_dotenv
from mcp.server.stdio import stdio_server

from src.logging_config import configure_logging
from src.mcp_app import build_mcp_server
from src.settings import load_settings

logger = logging.getLogger(__name__)
app = build_mcp_server()


async def main() -> None:
    load_dotenv()
    settings = load_settings(require_http_auth=False)
    configure_logging(settings.log_level)
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
