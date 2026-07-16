"""Aggregate router for API v1.

Feature routers are included here; the version prefix is applied once in ``app.main``.

The dataset-upload router is mounted only when ``enable_uploads`` is set (the default). In a
read-only deployment it is left out entirely so the ingestion stack — and its heavy
pandas/openpyxl dependencies — is never imported.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import analytics, catalog, health
from app.core.config import get_settings

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(catalog.router)
api_router.include_router(analytics.router)

if get_settings().enable_uploads:
    from app.api.routes import datasets

    api_router.include_router(datasets.router)
