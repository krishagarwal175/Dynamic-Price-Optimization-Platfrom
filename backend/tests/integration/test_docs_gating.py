"""Interactive docs and the OpenAPI schema are disabled in production."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.core.config import AppEnv, Settings
from app.main import create_app


def _client(env: AppEnv) -> TestClient:
    settings = Settings(  # type: ignore[call-arg]
        _env_file=None,
        app_env=env,
        app_name="Test API",
        database_url="sqlite://",
        cors_allowed_origins=["http://testserver"],
    )
    return TestClient(create_app(settings))


@pytest.mark.integration
def test_docs_are_disabled_in_production() -> None:
    with _client(AppEnv.PRODUCTION) as client:
        assert client.get("/docs").status_code == 404
        assert client.get("/redoc").status_code == 404
        assert client.get("/openapi.json").status_code == 404


@pytest.mark.integration
def test_docs_are_available_outside_production() -> None:
    with _client(AppEnv.LOCAL) as client:
        assert client.get("/docs").status_code == 200
        assert client.get("/openapi.json").status_code == 200
