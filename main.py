"""HTTP entrypoint.

Thin transport layer: it authenticates, parses the request, and delegates to the shared
`execute_tool` (or the shared MCP Server for SSE). No tool logic lives here. Heavy services
are created in the lifespan via the service provider, never at import time, so importing this
module has no side effects.
"""
import contextlib
import logging

from dotenv import load_dotenv
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Mount, Route

from src.dispatch import execute_tool
from src.http.auth import BearerAuthMiddleware
from src.logging_config import configure_logging
from src.mcp_app import build_mcp_server
from src.services.provider import ServiceProvider
from src.settings import load_settings
from src.tools_registry import TOOLS

logger = logging.getLogger(__name__)


async def handle_invoke(request: Request) -> JSONResponse:
    data = await request.json()
    tool_name = data.get("tool")
    if not tool_name:
        return JSONResponse({"error": "Tool name is required"}, status_code=400)
    services = getattr(request.app.state, "services", None)
    result = execute_tool(tool_name, data.get("arguments", {}), services=services)
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


async def handle_health(request: Request) -> JSONResponse:
    # Unauthenticated by design: used by k8s liveness/readiness probes.
    return JSONResponse({"status": "ok"})


def create_app() -> Starlette:
    load_dotenv()
    settings = load_settings(require_http_auth=True)
    configure_logging(settings.log_level)

    mcp_server = build_mcp_server()
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> Response:
        async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
            await mcp_server.run(
                streams[0], streams[1], mcp_server.create_initialization_options()
            )
        return Response()

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette):
        # Heavy services (vector DB, embedding models, ...) are built here, never at import.
        app.state.services = ServiceProvider(settings)
        logger.info("MCP HTTP server starting with %d tools", len(TOOLS))
        yield
        app.state.services = None

    app = Starlette(
        routes=[
            Route("/healthz", handle_health, methods=["GET"]),
            Route("/invoke", handle_invoke, methods=["POST"]),
            Route("/tools", handle_list_tools, methods=["GET"]),
            Route("/tools/{tool_name}", handle_get_tool, methods=["GET"]),
            Route("/sse", handle_sse, methods=["GET"]),
            Mount("/messages", app=sse.handle_post_message),
        ],
        lifespan=lifespan,
    )
    # Single middleware guards every route except the health probe.
    app.add_middleware(
        BearerAuthMiddleware,
        api_key=settings.mcp_api_key,
        exempt_paths=frozenset({"/healthz"}),
    )
    return app
