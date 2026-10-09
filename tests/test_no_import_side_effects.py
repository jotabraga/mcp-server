"""Importing modules must not open connections, download models, or read required env vars.

The original server instantiated the vector DB client at import time; this test guards
against that regression by importing the entrypoints in a subprocess with a clean env and
asserting it succeeds without any configuration present.
"""
import os
import subprocess
import sys


def test_entrypoints_import_without_side_effects():
    code = "import main, mcp_server; from src.services.provider import ServiceProvider"
    # Preserve the interpreter's own environment (PATH, venv) but strip app-specific vars,
    # so a successful import proves nothing is read or built at import time.
    env = {
        k: v
        for k, v in os.environ.items()
        if not k.startswith(("MCP_", "KEYCLOAK_", "QDRANT_", "REDIS_", "LOG_", "IA_"))
    }
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.dirname(__file__)),
        env=env,
    )
    assert result.returncode == 0, result.stderr


def test_service_provider_construction_is_cheap():
    # Constructing the provider must not build any heavy service.
    from src.services.provider import ServiceProvider
    from src.settings import Settings

    settings = Settings(
        mcp_api_key="k", log_level="INFO",
        keycloak_api_host=None, keycloak_client_id=None, keycloak_client_secret=None,
        ia_api_host=None,
        qdrant_host=None, qdrant_port=None, qdrant_api_key=None,
        qdrant_collection_name="knowledge-base",
        github_app_private_key=None, github_app_id=None, github_app_installation_id=None,
        redis_host="localhost", redis_port=6379, redis_db=0,
    )
    provider = ServiceProvider(settings)
    assert provider._keycloak is None  # nothing built yet
