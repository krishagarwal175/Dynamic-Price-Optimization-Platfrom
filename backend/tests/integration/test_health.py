"""Integration tests for the health endpoint and response envelope."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_health_returns_ok_envelope(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()

    # Success envelope shape
    assert set(body.keys()) == {"data", "meta"}
    assert body["data"] == {
        "status": "ok",
        "service": "Test API",
        "environment": "local",
    }
    assert "requestId" in body["meta"]
    assert "timestamp" in body["meta"]


@pytest.mark.integration
def test_health_sets_request_id_header(client: TestClient) -> None:
    response = client.get("/api/v1/health")
    assert response.headers.get("X-Request-ID")
    # The header and the envelope meta agree.
    assert response.headers["X-Request-ID"] == response.json()["meta"]["requestId"]


@pytest.mark.integration
def test_incoming_request_id_is_propagated(client: TestClient) -> None:
    response = client.get("/api/v1/health", headers={"X-Request-ID": "abc123"})
    assert response.headers["X-Request-ID"] == "abc123"
    assert response.json()["meta"]["requestId"] == "abc123"
