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

from src.services.ia_service import IaService
from src.services.kb_files_service import KBFilesService
from src.services.keycloak import Keycloak
from src.services.qdrant_service import QdrantService
from src.settings import Settings

logger = logging.getLogger(__name__)


class ServiceProvider:
    def __init__(self, settings: Settings):
        self._settings = settings
        self._keycloak: Optional[Keycloak] = None
        self._ia_service: Optional[IaService] = None
        self._qdrant: Optional[QdrantService] = None
        self._kb_files: Optional[KBFilesService] = None

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

    @property
    def ia_service(self) -> IaService:
        if self._ia_service is None:
            if not self._settings.ia_api_host:
                raise RuntimeError("IA_API_HOST is not configured")
            logger.info("Building IaService (lazy)")
            self._ia_service = IaService(self._settings.ia_api_host, self.keycloak)
        return self._ia_service

    @property
    def qdrant(self) -> QdrantService:
        if self._qdrant is None:
            s = self._settings
            if not s.qdrant_host:
                raise RuntimeError("QDRANT_HOST is not configured")
            logger.info("Building QdrantService (lazy)")
            self._qdrant = QdrantService(
                s.qdrant_host, s.qdrant_port, s.qdrant_api_key, s.qdrant_collection_name
            )
        return self._qdrant

    @property
    def kb_files(self) -> KBFilesService:
        if self._kb_files is None:
            s = self._settings
            if not (s.github_app_private_key and s.github_app_id and s.github_app_installation_id):
                raise RuntimeError("GitHub app settings are not configured")
            logger.info("Building KBFilesService (lazy)")
            self._kb_files = KBFilesService(
                int(s.github_app_id),
                int(s.github_app_installation_id),
                s.github_app_private_key,
            )
        return self._kb_files
