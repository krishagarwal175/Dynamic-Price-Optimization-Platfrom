"""Tests for engine creation and connectivity."""

from __future__ import annotations

import pytest
from sqlalchemy import Engine
from sqlalchemy.pool import StaticPool

from app.core.config import AppEnv, Settings
from app.core.database import check_connection, create_db_engine


def _settings(url: str) -> Settings:
    return Settings(_env_file=None, app_env=AppEnv.LOCAL, database_url=url)  # type: ignore[call-arg]


@pytest.mark.integration
def test_creates_engine_for_sqlite_file(tmp_path) -> None:
    url = f"sqlite:///{tmp_path / 'x.db'}"
    engine = create_db_engine(_settings(url))
    assert isinstance(engine, Engine)
    assert engine.dialect.name == "sqlite"


@pytest.mark.integration
def test_in_memory_sqlite_uses_static_pool() -> None:
    engine = create_db_engine(_settings("sqlite://"))
    # StaticPool keeps a single shared connection so an in-memory DB persists.
    assert isinstance(engine.pool, StaticPool)


@pytest.mark.integration
def test_check_connection_succeeds() -> None:
    engine = create_db_engine(_settings("sqlite://"))
    check_connection(engine)  # must not raise


@pytest.mark.integration
def test_check_connection_raises_when_unreachable(tmp_path) -> None:
    # Point SQLite at a path that is a directory: it cannot be opened as a database file.
    # Driver-independent, deterministic, and unaffected by parent-dir auto-creation.
    a_dir = tmp_path / "a_dir"
    a_dir.mkdir()
    engine = create_db_engine(_settings(f"sqlite:///{a_dir}"))
    with pytest.raises(Exception):  # noqa: B017 - any connection error is a failure here
        check_connection(engine)
