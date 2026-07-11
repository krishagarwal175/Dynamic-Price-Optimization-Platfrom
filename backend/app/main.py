"""FastAPI application factory and wiring.

Composition root: configure logging, build the app with OpenAPI metadata, install
middleware and exception handlers, wire persistence, and mount the versioned API router.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import Settings, get_settings
from app.core.database import (
    check_connection,
    create_db_engine,
    create_session_factory,
)
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.core.middleware import RequestContextMiddleware
from app.storage.local import LocalFileStorage

API_DESCRIPTION = (
    "Backend service for the Dynamic Pricing Optimization Platform. "
    "Provides the infrastructure foundation (configuration, logging, error handling, "
    "response envelope, persistence, and a health endpoint); business features arrive in "
    "later milestones."
)


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build and configure the FastAPI application."""
    settings = settings or get_settings()
    configure_logging(settings.log_level)
    logger = get_logger(__name__)

    engine = create_db_engine(settings)
    session_factory = create_session_factory(engine)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        # Startup: verify the database is reachable (schema is managed by Alembic, never
        # created here). Fail fast if it is not.
        check_connection(engine)
        logger.info("Database connection verified (%s)", engine.dialect.name)
        yield
        # Shutdown: release pooled connections.
        engine.dispose()
        logger.info("Database engine disposed")

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description=API_DESCRIPTION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Persistence handles live on app.state so request dependencies (get_db) resolve the
    # session factory this app was built with.
    app.state.db_engine = engine
    app.state.db_sessionmaker = session_factory

    # File storage backend for dataset ingestion (local filesystem in v1).
    app.state.file_storage = LocalFileStorage(settings.file_storage_path)

    # Bind the composed settings instance so every ``Depends(get_settings)`` resolves to
    # the configuration this app was built with (not a re-read of the environment).
    app.dependency_overrides[get_settings] = lambda: settings

    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    logger.info("Application initialized (env=%s)", settings.app_env.value)
    return app


app = create_app()
