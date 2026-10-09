"""Single source of truth for executing a tool by name.

Both entrypoints (stdio and HTTP) call `execute_tool`, so error handling, truncation and
run-context construction never diverge between transports (they did in the original repo).
"""
import logging

from src.models.run_context import RunContext
from src.tools_registry import TOOLS
from src.utils import truncate_response

logger = logging.getLogger(__name__)


def execute_tool(name: str, arguments: dict) -> str:
    tool = TOOLS.get(name)
    if tool is None:
        return truncate_response(f"Unknown tool: {name}")

    args = dict(arguments or {})
    run_context = RunContext.from_dict(args.pop("run_context", None))

    try:
        result = tool.execute(run_context=run_context, **args)
    except Exception as exc:  # noqa: BLE001 - surface a bounded error string to the caller
        logger.exception("Tool %s failed", name)
        return truncate_response(f"Error executing {name}: {exc}")

    text = str(result)
    return text if tool.skip_truncation else truncate_response(text)
