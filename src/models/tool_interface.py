from typing import Protocol

from mcp.types import Tool

from src.models.run_context import RunContext


class BaseTool(Protocol):
    """Interface implemented by every tool the server can dispatch."""

    # When True, the dispatcher injects the ServiceProvider as a `services` kwarg. This
    # replaces the original hard-coded `if name == "search_knowledge_base"` special case.
    requires_services: bool = False
    skip_truncation: bool = False

    def get_tool_input_schema(self) -> Tool:
        """Return the MCP Tool schema (name, description, input schema)."""
        ...

    def execute(self, run_context: RunContext, **kwargs) -> str:
        """Run the tool and return a string result."""
        ...
