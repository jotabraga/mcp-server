from src.dispatch import execute_tool


def test_known_tool_executes_and_returns_result():
    assert execute_tool("echo", {"message": "hi"}) == "hi"


def test_unknown_tool_returns_bounded_error():
    out = execute_tool("does_not_exist", {})
    assert "Unknown tool: does_not_exist" in out


def test_tool_exception_is_caught_and_reported():
    # Missing required arg triggers a TypeError inside the tool; dispatch must contain it.
    out = execute_tool("echo", {})
    assert "Error executing echo" in out


def test_run_context_is_stripped_from_tool_arguments():
    # run_context is consumed by the dispatcher, not forwarded as a tool kwarg.
    assert execute_tool("echo", {"message": "hi", "run_context": {"user_id": "u1"}}) == "hi"
