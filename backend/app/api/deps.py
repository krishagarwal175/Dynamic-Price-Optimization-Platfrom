"""FastAPI dependency-injection providers.

Wire settings and services here so routes declare what they need via ``Depends`` and stay
free of construction logic.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings, get_settings
from app.core.database import session_scope
from app.services.analytics import AnalyticsService
from app.services.catalog import CatalogService
from app.services.health import HealthService
from app.services.ingestion import IngestionService
from app.storage.base import FileStorage

SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_file_storage(request: Request) -> FileStorage:
    """Return the app-wide file storage backend (built in the composition root)."""
    storage: FileStorage = request.app.state.file_storage
    return storage


def get_db(request: Request) -> Iterator[Session]:
    """Yield a request-scoped database session from the app's session factory.

    The factory is built once per application in the composition root and stored on
    ``app.state`` (see ``app.main``), so the session always reflects the app's configured
    database.
    """
    factory: sessionmaker[Session] = request.app.state.db_sessionmaker
    with session_scope(factory) as session:
        yield session


DbSessionDep = Annotated[Session, Depends(get_db)]


def get_health_service(settings: SettingsDep) -> HealthService:
    return HealthService(settings)


HealthServiceDep = Annotated[HealthService, Depends(get_health_service)]

FileStorageDep = Annotated[FileStorage, Depends(get_file_storage)]


def get_ingestion_service(
    session: DbSessionDep,
    storage: FileStorageDep,
    settings: SettingsDep,
) -> IngestionService:
    return IngestionService(session, storage, settings)


IngestionServiceDep = Annotated[IngestionService, Depends(get_ingestion_service)]


def get_analytics_service(session: DbSessionDep) -> AnalyticsService:
    return AnalyticsService(session)


AnalyticsServiceDep = Annotated[AnalyticsService, Depends(get_analytics_service)]


def get_catalog_service(session: DbSessionDep) -> CatalogService:
    return CatalogService(session)


CatalogServiceDep = Annotated[CatalogService, Depends(get_catalog_service)]
