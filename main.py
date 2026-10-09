"""HTTP entrypoint.

Thin transport layer: it authenticates, parses the request, and delegates to the shared
`execute_tool`. No tool logic lives here. Heavy services (if any) are created in the
lifespan, never at import time, so importing this module has no side effects.
"""
import contextlib
import logging

from dotenv import load_dotenv
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from src.dispatch import execute_tool
from src.http.auth import BearerAuthMiddleware
from src.logging_config import configure_logging
from src.settings import load_settings
from src.tools_registry import TOOLS

logger = logging.getLogger(__name__)


async def handle_invoke(request: Request) -> JSONResponse:
    data = await request.json()
    tool_name = data.get("tool")
    if not tool_name:
        return JSONResponse({"error": "Tool name is required"}, status_code=400)
    result = execute_tool(tool_name, data.get("arguments", {}))
    return JSONResponse({"response": result})


async def handle_get_tool(request: Request) -> JSONResponse:
    tool_name = request.path_params.get("tool_name")
    tool = TOOLS.get(tool_name)
    if tool is None:
        return JSONResponse({"error": f"Tool '{tool_name}' not found"}, status_code=404)
    return JSONResponse({"tool": tool.get_tool_input_schema().model_dump()})


async def handle_list_tools(request: Request) -> JSONResponse:
    return JSONResponse(
        {"tools": [t.get_tool_input_schema().model_dump() for t in TOOLS.values()]}
    )


def create_app() -> Starlette:
    load_dotenv()
    settings = load_settings(require_http_auth=True)
    configure_logging(settings.log_level)

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette):
        logger.info("MCP HTTP server starting with %d tools", len(TOOLS))
        yield

    app = Starlette(
        routes=[
            Route("/invoke", handle_invoke, methods=["POST"]),
            Route("/tools", handle_list_tools, methods=["GET"]),
            Route("/tools/{tool_name}", handle_get_tool, methods=["GET"]),
        ],
        lifespan=lifespan,
    )
    app.add_middleware(BearerAuthMiddleware, api_key=settings.mcp_api_key)
    return app
