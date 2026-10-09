from unittest.mock import MagicMock

from src.dispatch import execute_tool


def test_tool_requiring_services_without_provider_returns_error():
    out = execute_tool("whoami", {})
    assert "services are not available" in out


def test_tool_requiring_services_receives_injected_provider():
    services = MagicMock()
    services.keycloak.get_token.return_value = "x" * 42

    out = execute_tool("whoami", {}, services=services)

    assert "token length 42" in out
    services.keycloak.get_token.assert_called_once()


def test_tool_not_requiring_services_is_unaffected_by_provider():
    # echo does not set requires_services, so the provider must not leak into its kwargs.
    assert execute_tool("echo", {"message": "hi"}, services=MagicMock()) == "hi"
