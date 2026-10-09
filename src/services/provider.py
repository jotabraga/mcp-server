"""Lazy provider for heavy services (vector DB clients, embedding models, token providers).

Rules this enforces:
- Importing this module does nothing expensive.
- Constructing ServiceProvider does nothing expensive either; it only stores settings.
- A heavy service is built on first access and memoized, so the lifespan can hold the
  provider while nothing is actually created until a request needs it.

This is where the original server went wrong: it instantiated the Qdrant client (which loads
embedding models and requires the DB to be up) at module import, breaking tests and any import.
"""
from __future__ import annotations

import logging
from typing import Optional

from src.services.keycloak import Keycloak
from src.settings import Settings

logger = logging.getLogger(__name__)


class ServiceProvider:
    def __init__(self, settings: Settings):
        self._settings = settings
        self._keycloak: Optional[Keycloak] = None

    @property
    def keycloak(self) -> Keycloak:
        if self._keycloak is None:
            s = self._settings
            if not (s.keycloak_api_host and s.keycloak_client_id and s.keycloak_client_secret):
                raise RuntimeError("Keycloak settings are not configured")
            logger.info("Building Keycloak client (lazy)")
            self._keycloak = Keycloak(
                s.keycloak_api_host, s.keycloak_client_id, s.keycloak_client_secret
            )
        return self._keycloak
