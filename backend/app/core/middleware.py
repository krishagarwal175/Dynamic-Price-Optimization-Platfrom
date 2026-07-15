"""HTTP middleware: correlation id assignment.

Generates (or accepts) a request id at the edge, stores it in the request context so the
logger and response envelope can read it, and echoes it back in the ``X-Request-ID``
response header.
"""

from __future__ import annotations

import time
import uuid
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.context import set_request_id
from app.core.logging import get_logger

logger = get_logger("app.request")

_REQUEST_ID_HEADER = "X-Request-ID"


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = request.headers.get(_REQUEST_ID_HEADER) or uuid.uuid4().hex
        set_request_id(request_id)

        logger.debug("%s %s (start)", request.method, request.url.path)
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 1)

        response.headers[_REQUEST_ID_HEADER] = request_id
        logger.info(
            "%s %s -> %s (%sms)",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response
