"""Test-only support: a throwaway ORM model and in-memory engine helpers.

This model exists **only** to exercise the persistence foundation. It is not a business
entity and lives entirely in the test tree.
"""

from __future__ import annotations

from sqlalchemy import Engine, String
from sqlalchemy.orm import Mapped, Session, mapped_column, sessionmaker

from app.core.config import AppEnv, Settings
from app.core.database import Base, create_db_engine, create_session_factory
from app.core.orm import IntIdMixin, TimestampMixin


class ExampleRecord(Base, IntIdMixin, TimestampMixin):
    """Minimal table used to validate the repository/session infrastructure."""

    __tablename__ = "example_record"

    name: Mapped[str] = mapped_column(String(100), nullable=False)


def make_memory_settings() -> Settings:
    return Settings(  # type: ignore[call-arg]
        _env_file=None,
        app_env=AppEnv.LOCAL,
        database_url="sqlite://",  # shared in-memory (StaticPool) engine
    )


def make_memory_engine() -> Engine:
    """Build an in-memory engine with only the test table created (never used at app
    startup — this is deterministic test scaffolding)."""
    engine = create_db_engine(make_memory_settings())
    Base.metadata.create_all(engine, tables=[ExampleRecord.__table__])
    return engine


def make_memory_db() -> tuple[Engine, sessionmaker[Session]]:
    engine = make_memory_engine()
    return engine, create_session_factory(engine)
