from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from src.http.auth import BearerAuthMiddleware


def _client(api_key: str = "secret") -> TestClient:
    async def ok(request):
        return JSONResponse({"ok": True})

    app = Starlette(routes=[Route("/invoke", ok, methods=["POST"])])
    app.add_middleware(BearerAuthMiddleware, api_key=api_key)
    return TestClient(app)


def test_request_without_token_is_rejected():
    resp = _client().post("/invoke", json={})
    assert resp.status_code == 401


def test_request_with_wrong_token_is_rejected():
    resp = _client().post("/invoke", json={}, headers={"Authorization": "Bearer nope"})
    assert resp.status_code == 401


def test_request_with_valid_token_passes():
    resp = _client().post("/invoke", json={}, headers={"Authorization": "Bearer secret"})
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}
