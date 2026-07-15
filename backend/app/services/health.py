"""Health service.

Reports the backend's operational status. When a database engine is supplied it runs a
lightweight connectivity probe so the endpoint reflects readiness (``ok`` vs ``degraded``)
rather than mere process liveness — without leaking any error detail to the client.
"""

from __future__ import annotations

from sqlalchemy.engine import Engine

from app.core.config import Settings
from app.core.database import check_connection
from app.core.logging import get_logger
from app.schemas.health import HealthStatus

logger = get_logger(__name__)


class HealthService:
    def __init__(self, settings: Settings, engine: Engine | None = None) -> None:
        self._settings = settings
        self._engine = engine

    def check(self) -> HealthStatus:
        """Return the current operational status of the backend.

        With a database engine configured, a failed connectivity probe yields a
        ``degraded`` status (and an error log) instead of a false ``ok``.
        """
        status = "ok"
        if self._engine is not None:
            try:
                check_connection(self._engine)
            except Exception as exc:  # noqa: BLE001 - report degraded, never leak details
                logger.error("Health check: database probe failed: %s", exc)
                status = "degraded"
        return HealthStatus(
            status=status,
            service=self._settings.app_name,
            environment=self._settings.app_env.value,
        )
