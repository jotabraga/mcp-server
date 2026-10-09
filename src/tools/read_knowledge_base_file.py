import logging

from mcp.types import Tool

from src.const import MAX_PAGINATED_RESPONSE_LENGTH
from src.models.run_context import RunContext
from src.models.tool_interface import BaseTool

logger = logging.getLogger(__name__)


class ReadKnowledgeBaseFileTool(BaseTool):
    requires_services = True

    def get_tool_input_schema(self) -> Tool:
        return Tool(
            name="read_knowledge_base_file",
            description=(
                f"Reads a file from the knowledge base, limited to {MAX_PAGINATED_RESPONSE_LENGTH} "
                "characters, starting from the skip position."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "status_message": {
                        "type": "string",
                        "description": "One sentence explanation as to why this tool is being used.",
                    },
                    "file": {
                        "type": "string",
                        "description": "The complete path to the file in the knowledge base",
                    },
                    "skip": {
                        "type": "integer",
                        "description": "The number of characters to skip in the content",
                        "default": 0,
                    },
                },
                "required": ["status_message", "file"],
            },
        )

    def execute(
        self,
        status_message: str,
        file: str,
        skip: int = 0,
        run_context: RunContext = None,
        services=None,
    ) -> str:
        if skip < 0:
            return "'skip' cannot be negative."

        kb_files = run_context.extra.get("kb_files") if run_context else None
        if kb_files and not any(file.startswith(prefix) for prefix in kb_files):
            return f"File '{file}' not found in knowledge base."

        try:
            content = services.kb_files.read_file(file)
        except Exception as exc:  # noqa: BLE001
            logger.error("Error reading file '%s': %s", file, exc)
            return f"File '{file}' not found in knowledge base."

        if not content:
            return f"File '{file}' not found in knowledge base."

        window = content[skip : skip + MAX_PAGINATED_RESPONSE_LENGTH]
        truncated = len(content) > skip + MAX_PAGINATED_RESPONSE_LENGTH

        return (
            "METADATA:\n"
            f"* File: {file}\n"
            f"* Characters skipped: {skip}\n"
            f"* Displayed characters: {len(window)}\n"
            f"* Total characters: {len(content)}\n"
            f"* Response is truncated: {truncated}\n\n"
            f"{'TRUNCATED ' if truncated else ''}FILE CONTENT:\n\n{window}"
        )
