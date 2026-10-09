from unittest.mock import MagicMock, patch

from src.services.keycloak import Keycloak


def _response(token: str, expires_in: int, status: int = 200):
    resp = MagicMock()
    resp.status_code = status
    resp.json.return_value = {"access_token": token, "expires_in": expires_in}
    resp.raise_for_status.return_value = None
    return resp


def test_token_is_cached_within_ttl():
    with patch("src.services.keycloak.requests.post") as post:
        post.return_value = _response("tok-1", expires_in=300)
        kc = Keycloak("https://kc", "cid", "secret")

        first = kc.get_token(now=0)
        second = kc.get_token(now=10)  # well within TTL

        assert first == second == "tok-1"
        assert post.call_count == 1  # second call served from cache


def test_token_is_renewed_after_expiry():
    with patch("src.services.keycloak.requests.post") as post:
        post.side_effect = [_response("tok-1", 300), _response("tok-2", 300)]
        kc = Keycloak("https://kc", "cid", "secret")

        first = kc.get_token(now=0)
        second = kc.get_token(now=1000)  # past expiry

        assert first == "tok-1"
        assert second == "tok-2"
        assert post.call_count == 2


def test_server_error_is_retried_then_succeeds():
    with patch("src.services.keycloak.requests.post") as post:
        post.side_effect = [_response("", 0, status=503), _response("tok-ok", 300)]
        kc = Keycloak("https://kc", "cid", "secret")

        assert kc.get_token(now=0) == "tok-ok"
        assert post.call_count == 2
