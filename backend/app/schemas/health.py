"""Health check response schema."""

from __future__ import annotations

from pydantic import BaseModel, Field


class HealthStatus(BaseModel):
    """Operational status of the backend service."""

    status: str = Field(description="Overall service status, e.g. 'ok'.")
    service: str = Field(description="Human-readable service name.")
    environment: str = Field(description="Deployment environment.")
