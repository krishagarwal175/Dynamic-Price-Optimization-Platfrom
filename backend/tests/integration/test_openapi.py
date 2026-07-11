"""Integration tests for API documentation surfaces."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_openapi_schema_available(client: TestClient) -> None:
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "Test API"
    assert "/api/v1/health" in schema["paths"]


@pytest.mark.integration
@pytest.mark.parametrize("path", ["/docs", "/redoc"])
def test_documentation_ui_available(client: TestClient, path: str) -> None:
    response = client.get(path)
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
