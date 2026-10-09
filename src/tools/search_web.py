from math import ceil

from ddgs import DDGS
from mcp.types import Tool

from src.models.run_context import RunContext
from src.models.tool_interface import BaseTool

_MAX_RESULTS = 20


class SearchWebTool(BaseTool):
    def get_tool_input_schema(self) -> Tool:
        return Tool(
            name="search_web",
            description="Performs a web search based on your query (similar to a Google search).",
            inputSchema={
                "type": "object",
                "properties": {
                    "status_message": {
                        "type": "string",
                        "description": "One sentence explanation as to why this tool is being used.",
                    },
                    "query": {"type": "string", "description": "The search query to perform"},
                },
                "required": ["status_message", "query"],
            },
        )

    def execute(self, status_message: str, query: str, run_context: RunContext = None) -> str:
        per_region = ceil(_MAX_RESULTS / 2)
        ddgs = DDGS()
        results = ddgs.text(query, max_results=per_region, region="us-en")
        results.extend(ddgs.text(query, max_results=per_region, region="br-pt"))

        if not results:
            return "No results found. Try a less restrictive/shorter query."

        formatted = [
            f"[{r['title']}]({r['href']})\n{r['body']}" for r in results
        ]
        return "## Search Results\n\n" + "\n\n".join(formatted)
