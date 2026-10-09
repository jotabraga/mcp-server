import requests
import html2text
from bs4 import BeautifulSoup
from mcp.types import Tool

from src.const import MAX_PAGINATED_RESPONSE_LENGTH
from src.models.run_context import RunContext
from src.models.tool_interface import BaseTool

_REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
    ),
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7",
    "DNT": "1",
}


class ReadWebpageTool(BaseTool):
    def get_tool_input_schema(self) -> Tool:
        return Tool(
            name="read_webpage",
            description=(
                f"Reads the content of a webpage, limited to {MAX_PAGINATED_RESPONSE_LENGTH} "
                "characters, starting from the skip position."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "status_message": {
                        "type": "string",
                        "description": "One sentence explanation as to why this tool is being used.",
                    },
                    "url": {"type": "string", "description": "The URL of the webpage to read"},
                    "skip": {
                        "type": "integer",
                        "description": "The number of characters to skip in the content",
                        "default": 0,
                    },
                },
                "required": ["status_message", "url"],
            },
        )

    def execute(
        self,
        status_message: str,
        url: str,
        skip: int = 0,
        run_context: RunContext = None,
    ) -> str:
        if skip < 0:
            return "'skip' cannot be negative."

        response = requests.get(url, headers=_REQUEST_HEADERS, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        content = html2text.html2text(str(soup))

        window = content[skip : skip + MAX_PAGINATED_RESPONSE_LENGTH]
        truncated = len(content) > skip + MAX_PAGINATED_RESPONSE_LENGTH

        return (
            "METADATA:\n"
            f"* URL: {url}\n"
            f"* Characters skipped: {skip}\n"
            f"* Displayed characters: {len(window)}\n"
            f"* Total characters: {len(content)}\n"
            f"* Response is truncated: {truncated}\n\n"
            f"{'TRUNCATED ' if truncated else ''}WEBPAGE CONTENT:\n\n{window}"
        )
