"""Application error hierarchy and global exception handlers.

Services raise typed :class:`AppError` subclasses; a small set of handlers map every
error (typed, framework validation, or unexpected) onto the standard error envelope.
Internal messages and stack traces are never exposed to clients.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.context import get_request_id
from app.core.logging import get_logger
from app.schemas.envelope import ErrorBody, ErrorDetail, ErrorResponse, Meta

logger = get_logger(__name__)

# HTTP status codes (explicit integers; avoids a deprecated Starlette constant name).
HTTP_404_NOT_FOUND = 404
HTTP_409_CONFLICT = 409
HTTP_413_TOO_LARGE = 413
HTTP_415_UNSUPPORTED_MEDIA_TYPE = 415
HTTP_422_UNPROCESSABLE = 422
HTTP_500_INTERNAL = 500


class AppError(Exception):
    """Base class for expected application errors.

    Subclasses set a stable machine-readable ``code`` and an HTTP ``status_code``.
    """

    code: str = "INTERNAL_ERROR"
    status_code: int = HTTP_500_INTERNAL

    def __init__(
        self,
        message: str,
        *,
        details: list[ErrorDetail] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.details = details


class NotFoundError(AppError):
    code = "NOT_FOUND"
    status_code = HTTP_404_NOT_FOUND


class ValidationError(AppError):
    code = "VALIDATION_ERROR"
    status_code = HTTP_422_UNPROCESSABLE


class ConflictError(AppError):
    code = "CONFLICT"
    status_code = HTTP_409_CONFLICT


class UnsupportedMediaTypeError(AppError):
    code = "UNSUPPORTED_MEDIA_TYPE"
    status_code = HTTP_415_UNSUPPORTED_MEDIA_TYPE


class PayloadTooLargeError(AppError):
    code = "PAYLOAD_TOO_LARGE"
    status_code = HTTP_413_TOO_LARGE


# Single source of truth: the code→status mapping is derived from the error classes
# themselves, so a handler that builds an envelope by code cannot drift from the class.
_STATUS_BY_CODE: dict[str, int] = {
    cls.code: cls.status_code
    for cls in (
        AppError,
        NotFoundError,
        ValidationError,
        ConflictError,
        UnsupportedMediaTypeError,
        PayloadTooLargeError,
    )
}


def _envelope(code: str, message: str, details: list[ErrorDetail] | None) -> JSONResponse:
    body = ErrorResponse(
        error=ErrorBody(code=code, message=message, details=details),
        meta=Meta(request_id=get_request_id()),
    )
    return JSONResponse(
        status_code=_STATUS_BY_CODE.get(code, HTTP_500_INTERNAL),
        content=jsonable_encoder(body, by_alias=True),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Attach the global exception handlers to the application."""

    @app.exception_handler(AppError)
    async def _handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        body = ErrorResponse(
            error=ErrorBody(code=exc.code, message=exc.message, details=exc.details),
            meta=Meta(request_id=get_request_id()),
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=jsonable_encoder(body, by_alias=True),
        )

    @app.exception_handler(RequestValidationError)
    async def _handle_validation(_: Request, exc: RequestValidationError) -> JSONResponse:
        details = [
            ErrorDetail(
                field=".".join(str(p) for p in err.get("loc", []) if p != "body"),
                issue=err.get("msg", "invalid"),
            )
            for err in exc.errors()
        ]
        return _envelope("VALIDATION_ERROR", "Request validation failed.", details)

    @app.exception_handler(Exception)
    async def _handle_unexpected(_: Request, exc: Exception) -> JSONResponse:
        # Log the real cause; never leak internals to the client.
        logger.exception("Unhandled exception: %s", exc)
        return _envelope("INTERNAL_ERROR", "An unexpected error occurred.", None)
