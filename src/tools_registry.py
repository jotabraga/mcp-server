"""Tool registry.

A dict keyed by tool name gives O(1) lookup in the dispatcher (the original used a linear
scan over a list on every call). To register a new tool, add an instance here.
"""
from typing import Dict

from src.models.tool_interface import BaseTool
from src.tools.echo import EchoTool
from src.tools.fetch_skill import FetchSkillTool
from src.tools.read_webpage import ReadWebpageTool
from src.tools.search_web import SearchWebTool
from src.tools.whoami import WhoAmITool

_TOOL_INSTANCES = [
    EchoTool(),
    WhoAmITool(),
    SearchWebTool(),
    ReadWebpageTool(),
    FetchSkillTool(),
]

TOOLS: Dict[str, BaseTool] = {
    tool.get_tool_input_schema().name: tool for tool in _TOOL_INSTANCES
}
