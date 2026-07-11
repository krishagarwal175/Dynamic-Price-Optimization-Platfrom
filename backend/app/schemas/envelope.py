"""Standard API response/error envelope models.

Mirrors the frozen contract in ``vault4/02-Architecture/api_design.md``:

    success  -> {"data": ..., "meta": {...}}
    error    -> {"error": {"code", "message", "details"?}, "meta": {...}}
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

from app.core.context import get_request_id

T = TypeVar("T")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Meta(BaseModel):
    """Correlation metadata attached to every response.

    ``request_id`` defaults to the current request's correlation id (set at the edge by
    ``RequestContextMiddleware``), so both success and error envelopes carry it without
    each call site having to thread it through.
    """

    request_id: str | None = Field(default_factory=get_request_id, alias="requestId")
    timestamp: datetime = Field(default_factory=_utcnow)

    model_config = {"populate_by_name": True}


class SuccessResponse(BaseModel, Generic[T]):
    """Envelope for a successful response."""

    data: T
    meta: Meta = Field(default_factory=Meta)


class ErrorDetail(BaseModel):
    """A single field-level validation problem."""

    field: str
    issue: str


class ErrorBody(BaseModel):
    """The error payload inside an error envelope."""

    code: str
    message: str
    details: list[ErrorDetail] | None = None


class ErrorResponse(BaseModel):
    """Envelope for an error response."""

    error: ErrorBody
    meta: Meta = Field(default_factory=Meta)
