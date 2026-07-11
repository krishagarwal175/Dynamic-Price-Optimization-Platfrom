"""Tests that Alembic migrations execute against a real (SQLite) database."""

from __future__ import annotations

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

BACKEND_ROOT = Path(__file__).resolve().parents[2]


def _alembic_config(db_url: str) -> Config:
    cfg = Config(str(BACKEND_ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_ROOT / "alembic"))
    cfg.set_main_option("sqlalchemy.url", db_url)
    return cfg


@pytest.mark.integration
def test_upgrade_head_then_downgrade_base(tmp_path: Path) -> None:
    db_path = tmp_path / "migrations.db"
    url = f"sqlite:///{db_path}"
    cfg = _alembic_config(url)

    # Upgrade to head: the migration pipeline must run cleanly and stamp a version.
    command.upgrade(cfg, "head")

    engine = create_engine(url)
    try:
        tables = set(inspect(engine).get_table_names())
        assert "alembic_version" in tables
    finally:
        engine.dispose()

    # Downgrade back to base must also run without error (proves reversibility).
    command.downgrade(cfg, "base")


@pytest.mark.integration
def test_single_head_revision() -> None:
    from alembic.script import ScriptDirectory

    script = ScriptDirectory.from_config(_alembic_config("sqlite://"))
    assert len(script.get_heads()) == 1, "migration history must have exactly one head"


BUSINESS_TABLES = {"category", "product", "historical_sale", "competitor", "competitor_price"}


@pytest.mark.integration
def test_fresh_upgrade_creates_business_schema(tmp_path: Path) -> None:
    url = f"sqlite:///{tmp_path / 'fresh.db'}"
    command.upgrade(_alembic_config(url), "head")

    engine = create_engine(url)
    try:
        tables = set(inspect(engine).get_table_names())
    finally:
        engine.dispose()

    assert BUSINESS_TABLES.issubset(tables)


@pytest.mark.integration
def test_migration_is_idempotent_and_reversible(tmp_path: Path) -> None:
    url = f"sqlite:///{tmp_path / 'idem.db'}"
    cfg = _alembic_config(url)

    command.upgrade(cfg, "head")
    command.upgrade(cfg, "head")  # running again is a no-op, must not error

    engine = create_engine(url)
    try:
        assert BUSINESS_TABLES.issubset(set(inspect(engine).get_table_names()))

        # Full down then up again recreates the schema cleanly (fresh-creation path).
        command.downgrade(cfg, "base")
        remaining = set(inspect(engine).get_table_names())
        assert not (BUSINESS_TABLES & remaining)

        command.upgrade(cfg, "head")
        assert BUSINESS_TABLES.issubset(set(inspect(engine).get_table_names()))
    finally:
        engine.dispose()
