"""Client for the IA API.

Adapted from the original service: dependencies (Keycloak, base URL) are injected instead
of read from the environment inside the constructor, so it is testable and has no import-time
side effects.
"""
import logging

import requests

from src import const
from src.services.keycloak import Keycloak

logger = logging.getLogger(__name__)

_MAX_ATTEMPTS = 3
_TIMEOUT_SECONDS = 60


class IaService:
    def __init__(self, base_url: str, keycloak: Keycloak):
        self._base_url = base_url
        self._keycloak = keycloak

    def get_skills(self) -> list[dict]:
        response = self._get(
            path="/agent-skills",
            params={"search": "", "limit": 99999, "enabled": "true"},
        )
        return response.json().get("agent_skills", [])

    def _get(self, path: str, params: dict | None = None) -> requests.Response:
        endpoint = f"{self._base_url}{path}"
        headers = {
            "User-Agent": const.App.USER_AGENT,
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._keycloak.get_token()}",
        }

        response = None
        for attempt in range(1, _MAX_ATTEMPTS + 1):
            response = requests.get(
                endpoint, headers=headers, params=params or {}, timeout=_TIMEOUT_SECONDS
            )
            if response.status_code < 500:
                break
            logger.warning("IA API GET %s attempt %d returned %d", path, attempt, response.status_code)

        response.raise_for_status()
        return response
