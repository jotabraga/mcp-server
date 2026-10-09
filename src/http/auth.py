"""HTTP authentication.

The original server exposed /invoke, /tools/* and the SSE transport with no auth at all,
which means anyone who can reach the pod can run arbitrary tools (including code execution).
This middleware rejects any request without a valid bearer token before it reaches a route.
"""
import hmac

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class BearerAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, api_key: str):
        super().__init__(app)
        self._api_key = api_key

    async def dispatch(self, request: Request, call_next):
        provided = self._extract_bearer(request)
        if provided is None or not self._matches(provided):
            return JSONResponse({"error": "unauthorized"}, status_code=401)
        return await call_next(request)

    @staticmethod
    def _extract_bearer(request: Request):
        header = request.headers.get("authorization", "")
        prefix = "bearer "
        if header.lower().startswith(prefix):
            return header[len(prefix):].strip()
        return None

    def _matches(self, provided: str) -> bool:
        # Constant-time comparison to avoid leaking the key via timing.
        return hmac.compare_digest(provided, self._api_key)
