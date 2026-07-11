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
from app.services.health import HealthService

SettingsDep = Annotated[Settings, Depends(get_settings)]


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
