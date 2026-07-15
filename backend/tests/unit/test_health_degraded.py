"""Health service reports 'degraded' when the database probe fails."""

from __future__ import annotations

from typing import Any

import pytest

from app.core.config import AppEnv, Settings
from app.services.health import HealthService


class _BrokenEngine:
    """Stand-in engine whose connection attempt fails."""

    def connect(self) -> Any:
        raise RuntimeError("database unreachable")


def _settings() -> Settings:
    return Settings(_env_file=None, app_name="Svc", app_env=AppEnv.STAGING)  # type: ignore[call-arg]


@pytest.mark.unit
def test_healthy_when_probe_succeeds_is_ok_without_engine() -> None:
    assert HealthService(_settings()).check().status == "ok"


@pytest.mark.unit
def test_degraded_when_database_probe_fails() -> None:
    result = HealthService(_settings(), _BrokenEngine()).check()  # type: ignore[arg-type]
    assert result.status == "degraded"
    assert result.service == "Svc"
