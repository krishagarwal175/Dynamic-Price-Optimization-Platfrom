"""Unit tests for the health service."""

from __future__ import annotations

import pytest

from app.core.config import AppEnv, Settings
from app.services.health import HealthService


@pytest.mark.unit
def test_health_service_reports_ok() -> None:
    settings = Settings(  # type: ignore[call-arg]
        _env_file=None,
        app_name="Svc",
        app_env=AppEnv.STAGING,
    )
    result = HealthService(settings).check()
    assert result.status == "ok"
    assert result.service == "Svc"
    assert result.environment == "staging"
