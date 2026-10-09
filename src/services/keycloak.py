"""Keycloak client-credentials token provider with in-memory caching.

The original fetched a fresh token on every outbound call. Here we cache the token and only
renew it shortly before it expires, cutting one HTTP round-trip (and Keycloak load) per tool
call. ponytail: ceiling — cache is per-process in-memory; with multiple replicas each holds
its own token, which is fine for client_credentials. Upgrade path: back it with Redis if a
shared cache is ever needed.
"""
import logging
import time

import requests

from src import const

logger = logging.getLogger(__name__)

# Renew this many seconds before the real expiry to avoid using a token that dies mid-flight.
_EXPIRY_SKEW_SECONDS = 30
_MAX_ATTEMPTS = 3
_TIMEOUT_SECONDS = 60


class Keycloak:
    def __init__(self, api_host: str, client_id: str, client_secret: str):
        self._api_host = api_host
        self._client_id = client_id
        self._client_secret = client_secret
        self._cached_token: str | None = None
        self._expires_at: float = 0.0

    def get_token(self, now: float | None = None) -> str:
        now = time.monotonic() if now is None else now
        if self._cached_token is not None and now < self._expires_at:
            return self._cached_token

        token, expires_in = self._request_token()
        self._cached_token = token
        self._expires_at = now + max(expires_in - _EXPIRY_SKEW_SECONDS, 0)
        return token

    def _request_token(self) -> tuple[str, int]:
        data = {
            "grant_type": const.Keycloak.GRANT_TYPE,
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "scope": const.Keycloak.SCOPE,
        }
        headers = {
            "Content-Type": const.Keycloak.CONTENT_TYPE,
            "User-Agent": const.App.USER_AGENT,
        }

        response = None
        for attempt in range(1, _MAX_ATTEMPTS + 1):
            response = requests.post(
                self._api_host, headers=headers, data=data, timeout=_TIMEOUT_SECONDS
            )
            if response.status_code < 500:
                break
            logger.warning(
                "Keycloak token request attempt %d returned %d",
                attempt,
                response.status_code,
            )

        response.raise_for_status()
        body = response.json()
        return body["access_token"], int(body.get("expires_in", 0))
