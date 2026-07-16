"""Database infrastructure: declarative base, engine, sessions, and lifecycle.

Provider-agnostic by design — the engine is built from a SQLAlchemy URL in the typed
settings, so switching SQLite (local/tests) → PostgreSQL (deployment) is a configuration
change only. Schema is owned by Alembic; the application never calls
``Base.metadata.create_all()`` at startup.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import Engine, MetaData, create_engine, event, make_url, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import Settings

# Deterministic constraint names so Alembic autogenerate produces stable migrations.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Declarative base for all ORM models (business models arrive in later milestones)."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


def _is_sqlite(url: str) -> bool:
    return url.startswith("sqlite")


def _is_sqlite_memory(url: str) -> bool:
    return _is_sqlite(url) and (":memory:" in url or url in {"sqlite://", "sqlite+pysqlite://"})


def _ensure_sqlite_parent_dir(url: str) -> None:
    """Create the parent directory for a file-based SQLite database if needed, so the
    default configuration works from a clean checkout without manual setup."""
    database = make_url(url).database
    if database and database != ":memory:":
        parent = Path(database).expanduser().parent
        if parent and not parent.exists():
            parent.mkdir(parents=True, exist_ok=True)


def _enable_sqlite_foreign_keys(engine: Engine) -> None:
    """SQLite disables foreign-key enforcement by default; turn it on per connection so
    ON DELETE cascades and RESTRICTs behave as declared."""

    @event.listens_for(engine, "connect")
    def _set_pragma(dbapi_connection: object, _record: object) -> None:
        cursor = dbapi_connection.cursor()  # type: ignore[attr-defined]
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def _normalize_url(url: str) -> str:
    """Accept the legacy ``postgres://`` scheme some providers (Supabase, Heroku) emit and
    rewrite it to the ``postgresql://`` form SQLAlchemy 2.0 requires."""
    if url.startswith("postgres://"):
        return "postgresql://" + url[len("postgres://") :]
    return url


def create_db_engine(settings: Settings) -> Engine:
    """Create a SQLAlchemy engine from settings, applying provider-specific tuning."""
    url = _normalize_url(settings.database_url)
    if _is_sqlite(url):
        if not _is_sqlite_memory(url):
            _ensure_sqlite_parent_dir(url)
        # SQLite needs cross-thread access relaxed; an in-memory DB must share one
        # connection (StaticPool) so schema/data persist across sessions.
        connect_args = {"check_same_thread": False}
        if _is_sqlite_memory(url):
            engine = create_engine(
                url,
                echo=settings.db_echo,
                connect_args=connect_args,
                poolclass=StaticPool,
            )
        else:
            engine = create_engine(url, echo=settings.db_echo, connect_args=connect_args)
        _enable_sqlite_foreign_keys(engine)
        return engine

    # PostgreSQL (and other servers): pre-ping to drop stale pooled connections.
    return create_engine(url, echo=settings.db_echo, pool_pre_ping=True)


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Build a session factory. Sessions do not autoflush and survive commit expiry so
    callers can read attributes after commit without an extra round-trip."""
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def check_connection(engine: Engine) -> None:
    """Verify connectivity with a trivial round-trip. Raises on failure."""
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))


@contextmanager
def session_scope(factory: sessionmaker[Session]) -> Iterator[Session]:
    """Provide a session, rolling back on error and always closing.

    This is the read-oriented scope (no implicit commit); services own the write
    boundary via :func:`transaction`.
    """
    session = factory()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def transaction(session: Session) -> Iterator[Session]:
    """Run a unit of work: commit on success, roll back on any exception."""
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
