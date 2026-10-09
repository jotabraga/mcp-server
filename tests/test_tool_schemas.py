import pytest

from src.tools_registry import TOOLS

ALL_TOOLS = list(TOOLS.values())


@pytest.mark.parametrize("tool", ALL_TOOLS, ids=lambda t: t.get_tool_input_schema().name)
def test_tool_schema_is_well_formed(tool):
    schema = tool.get_tool_input_schema()

    assert schema.name, "tool must have a name"
    assert schema.description, "tool must have a description"

    input_schema = schema.inputSchema
    assert input_schema["type"] == "object"
    assert "properties" in input_schema

    # Every required field must be declared in properties.
    required = input_schema.get("required", [])
    properties = input_schema["properties"]
    for field in required:
        assert field in properties, f"required field {field!r} missing from properties"


def test_registry_keys_match_schema_names():
    for name, tool in TOOLS.items():
        assert name == tool.get_tool_input_schema().name
