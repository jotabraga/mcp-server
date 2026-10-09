"""The SSE and messages routes must sit behind the same auth middleware as the REST routes."""
import os

from starlette.testclient import TestClient


def _app():
    os.environ["MCP_API_KEY"] = "secret"
    import main

    return main.create_app()


def test_sse_requires_authentication():
    client = TestClient(_app())
    # No token: must be rejected before the SSE stream opens.
    resp = client.get("/sse")
    assert resp.status_code == 401


def test_messages_endpoint_requires_authentication():
    client = TestClient(_app())
    resp = client.post("/messages/", json={})
    assert resp.status_code == 401


def test_invoke_requires_authentication():
    client = TestClient(_app())
    resp = client.post("/invoke", json={"tool": "echo", "arguments": {"message": "x"}})
    assert resp.status_code == 401


def test_health_is_reachable_without_authentication():
    client = TestClient(_app())
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
