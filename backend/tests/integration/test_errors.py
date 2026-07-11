"""Integration tests for the global exception handlers and error envelope.

A throwaway app mounts routes that raise each error kind, so the handler-to-envelope
mapping is verified end to end without depending on business endpoints.
"""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.core.errors import NotFoundError, ValidationError, register_exception_handlers
from app.core.middleware import RequestContextMiddleware
from app.schemas.envelope import ErrorDetail


class _Payload(BaseModel):
    """Module-level so FastAPI can resolve the annotation under
    ``from __future__ import annotations`` (string annotations are looked up in module
    globals, not local scope)."""

    price: float


@pytest.fixture
def error_client() -> TestClient:
    app = FastAPI()
    app.add_middleware(RequestContextMiddleware)
    register_exception_handlers(app)

    @app.get("/boom/not-found")
    def _not_found() -> None:
        raise NotFoundError("Product not found.")

    @app.get("/boom/validation")
    def _validation() -> None:
        raise ValidationError(
            "Bad price.",
            details=[ErrorDetail(field="price", issue="must be >= 0")],
        )

    @app.get("/boom/unexpected")
    def _unexpected() -> None:
        raise RuntimeError("kaboom")

    @app.post("/echo")
    def _echo(payload: _Payload) -> dict[str, float]:
        return {"price": payload.price}

    return TestClient(app, raise_server_exceptions=False)


@pytest.mark.integration
def test_not_found_maps_to_envelope(error_client: TestClient) -> None:
    response = error_client.get("/boom/not-found")
    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "NOT_FOUND"
    assert body["error"]["message"] == "Product not found."
    assert "requestId" in body["meta"]


@pytest.mark.integration
def test_domain_validation_includes_details(error_client: TestClient) -> None:
    response = error_client.get("/boom/validation")
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert body["error"]["details"] == [{"field": "price", "issue": "must be >= 0"}]


@pytest.mark.integration
def test_unexpected_error_is_masked(error_client: TestClient) -> None:
    response = error_client.get("/boom/unexpected")
    assert response.status_code == 500
    body = response.json()
    assert body["error"]["code"] == "INTERNAL_ERROR"
    # Internal detail must not leak.
    assert "kaboom" not in response.text


@pytest.mark.integration
def test_request_validation_maps_to_envelope(error_client: TestClient) -> None:
    response = error_client.post("/echo", json={"price": "not-a-number"})
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert any(d["field"] == "price" for d in body["error"]["details"])
