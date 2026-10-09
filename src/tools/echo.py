"""A dependency-free tool used to exercise the dispatch path end to end in tests."""
from mcp.types import Tool

from src.models.run_context import RunContext
from src.models.tool_interface import BaseTool


class EchoTool(BaseTool):
    skip_truncation = False

    def get_tool_input_schema(self) -> Tool:
        return Tool(
            name="echo",
            description="Returns the provided message unchanged. Useful as a connectivity check.",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Text to echo back.",
                    }
                },
                "required": ["message"],
            },
        )

    def execute(self, message: str, run_context: RunContext = None) -> str:
        return message
