"""Centralized configuration.

Reading os.environ is isolated here so the rest of the code depends on a typed object, and
so a missing required variable fails early with a clear message instead of surfacing as a
confusing error deep inside a request. Importing this module has no side effects; call
`load_settings()` explicitly at startup.
"""
import os
from dataclasses import dataclass
from typing import Optional


class SettingsError(RuntimeError):
    """Raised when required configuration is missing or invalid."""


@dataclass(frozen=True)
class Settings:
    # HTTP auth: the shared secret clients must present as a bearer token.
    mcp_api_key: str
    log_level: str
    # Keycloak (optional at boot; only required by tools that make authenticated calls).
    keycloak_api_host: Optional[str]
    keycloak_client_id: Optional[str]
    keycloak_client_secret: Optional[str]
    # Downstream APIs.
    ia_api_host: Optional[str]
    # Vector DB (knowledge base search).
    qdrant_host: Optional[str]
    qdrant_port: Optional[str]
    qdrant_api_key: Optional[str]
    qdrant_collection_name: str
    # GitHub app private key for reading knowledge-base files.
    github_app_private_key: Optional[str]
    github_app_id: Optional[str]
    github_app_installation_id: Optional[str]
    # Redis (shared cache: canvas state, optional token cache backend).
    redis_host: str
    redis_port: int
    redis_db: int


def load_settings(require_http_auth: bool = True) -> Settings:
    """Build Settings from the environment, failing fast on missing required values.

    `require_http_auth` is True for the HTTP entrypoint (an unauthenticated HTTP server is
    the main security risk we are closing) and can be False for the stdio entrypoint, which
    is not network-exposed.
    """
    missing: list[str] = []

    mcp_api_key = os.getenv("MCP_API_KEY", "")
    if require_http_auth and not mcp_api_key:
        missing.append("MCP_API_KEY")

    if missing:
        raise SettingsError(
            "Missing required environment variables: " + ", ".join(missing)
        )

    return Settings(
        mcp_api_key=mcp_api_key,
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        keycloak_api_host=os.getenv("KEYCLOAK_API_HOST") or None,
        keycloak_client_id=os.getenv("KEYCLOAK_CLIENT_ID") or None,
        keycloak_client_secret=os.getenv("KEYCLOAK_CLIENT_SECRET") or None,
        ia_api_host=os.getenv("IA_API_HOST") or None,
        qdrant_host=os.getenv("QDRANT_HOST") or None,
        qdrant_port=os.getenv("QDRANT_PORT") or None,
        qdrant_api_key=os.getenv("QDRANT_API_KEY") or None,
        qdrant_collection_name=os.getenv("QDRANT_COLLECTION_NAME", "knowledge-base"),
        github_app_private_key=os.getenv("GITHUB_APP_PRIVATE_KEY") or None,
        github_app_id=os.getenv("GITHUB_APP_ID") or None,
        github_app_installation_id=os.getenv("GITHUB_APP_INSTALLATION_ID") or None,
        redis_host=os.getenv("REDIS_HOST", "localhost"),
        redis_port=int(os.getenv("REDIS_PORT", "6379")),
        redis_db=int(os.getenv("REDIS_DB", "0")),
    )
