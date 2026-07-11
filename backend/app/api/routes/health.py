"""Health endpoint: ``GET /api/v1/health``."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import HealthServiceDep
from app.schemas.envelope import SuccessResponse
from app.schemas.health import HealthStatus

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=SuccessResponse[HealthStatus],
    summary="Health check",
    description="Verify that the backend service is operational.",
)
def health(service: HealthServiceDep) -> SuccessResponse[HealthStatus]:
    return SuccessResponse(data=service.check())
