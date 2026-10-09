import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def fake_redis(monkeypatch):
    """Install a fake `redis` module so RedisService builds without a real server."""
    client = MagicMock()
    module = SimpleNamespace(
        ConnectionPool=MagicMock(return_value="pool"),
        Redis=MagicMock(return_value=client),
    )
    monkeypatch.setitem(sys.modules, "redis", module)
    return client


def _service(fake_redis):
    from src.services.redis_service import RedisService

    return RedisService("localhost", 6379, 0), fake_redis


def test_set_forwards_value_and_ttl(fake_redis):
    svc, client = _service(fake_redis)
    svc.set("k", "v", ttl=42)
    client.set.assert_called_once_with("k", "v", ex=42)


def test_get_decodes_bytes(fake_redis):
    svc, client = _service(fake_redis)
    client.get.return_value = b"hello"
    assert svc.get("k") == "hello"


def test_get_returns_none_when_missing(fake_redis):
    svc, client = _service(fake_redis)
    client.get.return_value = None
    assert svc.get("k") is None


def test_exists_returns_bool(fake_redis):
    svc, client = _service(fake_redis)
    client.exists.return_value = 1
    assert svc.exists("k") is True
    client.exists.return_value = 0
    assert svc.exists("k") is False
