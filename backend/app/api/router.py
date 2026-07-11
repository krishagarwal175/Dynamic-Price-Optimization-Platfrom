"""Aggregate router for API v1.

Feature routers are included here; the version prefix is applied once in ``app.main``.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import datasets, health

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(datasets.router)
