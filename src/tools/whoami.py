"""Example of a tool that depends on an injected service.

It asks the ServiceProvider for a Keycloak token. The point is to demonstrate dependency
injection via `requires_services` without any special-casing in the dispatcher.
"""
from mcp.types import Tool

from src.models.run_context import RunContext
from src.models.tool_interface import BaseTool


class WhoAmITool(BaseTool):
    requires_services = True

    def get_tool_input_schema(self) -> Tool:
        return Tool(
            name="whoami",
            description="Returns a short confirmation that an authenticated token was obtained.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        )

    def execute(self, run_context: RunContext = None, services=None) -> str:
        token = services.keycloak.get_token()
        return f"authenticated: token length {len(token)}"
