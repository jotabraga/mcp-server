"""Thin Redis wrapper for shared state (e.g. canvas code/plan) and optional token caching.

Connection parameters are injected instead of read from the environment, and the `redis`
import is deferred to construction so importing this module stays cheap. The service is built
lazily by the provider inside the HTTP lifespan, never at import time.
"""
import logging

logger = logging.getLogger(__name__)

DEFAULT_TTL_SECONDS = 3600  # 1 hour


class RedisService:
    def __init__(self, host: str, port: int, db: int):
        import redis as redis_client

        pool = redis_client.ConnectionPool(host=host, port=port, db=db)
        self._redis = redis_client.Redis(connection_pool=pool)
        logger.info("RedisService connected to %s:%s/%s", host, port, db)

    def set(self, key: str, value: str, ttl: int = DEFAULT_TTL_SECONDS) -> None:
        self._redis.set(key, value, ex=ttl)

    def get(self, key: str) -> str | None:
        value = self._redis.get(key)
        return value.decode("utf-8") if value else None

    def append(self, key: str, value: str, ttl: int = DEFAULT_TTL_SECONDS) -> None:
        self._redis.append(key, value)
        self._redis.expire(key, ttl)

    def delete(self, key: str) -> None:
        self._redis.delete(key)

    def exists(self, key: str) -> bool:
        return bool(self._redis.exists(key))
