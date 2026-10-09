import pytest

from src.settings import SettingsError, load_settings


def test_http_auth_requires_api_key(monkeypatch):
    monkeypatch.delenv("MCP_API_KEY", raising=False)
    with pytest.raises(SettingsError) as exc:
        load_settings(require_http_auth=True)
    assert "MCP_API_KEY" in str(exc.value)


def test_stdio_does_not_require_api_key(monkeypatch):
    monkeypatch.delenv("MCP_API_KEY", raising=False)
    settings = load_settings(require_http_auth=False)
    assert settings.mcp_api_key == ""


def test_settings_reads_values_from_env(monkeypatch):
    monkeypatch.setenv("MCP_API_KEY", "secret")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    settings = load_settings(require_http_auth=True)
    assert settings.mcp_api_key == "secret"
    assert settings.log_level == "DEBUG"
