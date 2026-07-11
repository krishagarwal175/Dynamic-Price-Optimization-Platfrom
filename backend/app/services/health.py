"""Health service.

Trivial in M2, but placed in the service layer so the API stays a thin adapter and the
dependency-injection seam exists from day one (future readiness checks — e.g. database
connectivity — will live here without touching the route).
"""

from __future__ import annotations

from app.core.config import Settings
from app.schemas.health import HealthStatus


class HealthService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def check(self) -> HealthStatus:
        """Return the current operational status of the backend."""
        return HealthStatus(
            status="ok",
            service=self._settings.app_name,
            environment=self._settings.app_env.value,
        )
