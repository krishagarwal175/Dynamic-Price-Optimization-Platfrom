"""Per-request context shared across logging and the response envelope.

The request id is generated once at the edge (middleware), stored here, and read by both
the structured logger and the response/error envelope so a single request can be
correlated end to end.
"""

from __future__ import annotations

from contextvars import ContextVar

_request_id: ContextVar[str | None] = ContextVar("request_id", default=None)


def set_request_id(request_id: str) -> None:
    _request_id.set(request_id)


def get_request_id() -> str | None:
    return _request_id.get()
