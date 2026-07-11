"""Test-only support: a throwaway ORM model and in-memory engine helpers.

This model exists **only** to exercise the persistence foundation. It is not a business
entity and lives entirely in the test tree.
"""

from __future__ import annotations

import io

import pandas as pd
from sqlalchemy import Engine, String
from sqlalchemy.orm import Mapped, Session, mapped_column, sessionmaker

from app.core.config import AppEnv, Settings
from app.core.database import Base, create_db_engine, create_session_factory
from app.core.orm import IntIdMixin, TimestampMixin

# A well-formed product-catalog dataset (two categories, three products).
VALID_CATALOG_ROWS = [
    {
        "sku": "SKU-1",
        "name": "Cola",
        "category": "Beverages",
        "unit_cost": "1.00",
        "base_price": "2.50",
    },
    {
        "sku": "SKU-2",
        "name": "Water",
        "category": "Beverages",
        "unit_cost": "0.50",
        "base_price": "1.20",
    },
    {
        "sku": "SKU-3",
        "name": "Chips",
        "category": "Snacks",
        "unit_cost": "0.80",
        "base_price": "1.90",
    },
]


def catalog_df(rows: list[dict[str, str]] | None = None) -> pd.DataFrame:
    return pd.DataFrame(rows if rows is not None else VALID_CATALOG_ROWS, dtype=str)


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def to_xlsx_bytes(df: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine="openpyxl")
    return buffer.getvalue()


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


def make_business_db() -> tuple[Engine, sessionmaker[Session]]:
    """In-memory engine with the full business schema created (all registered models).

    Test scaffolding only — production schema is owned by Alembic.
    """
    import app.models  # noqa: F401  (register all business models on Base.metadata)

    engine = create_db_engine(make_memory_settings())
    Base.metadata.create_all(engine)
    return engine, create_session_factory(engine)
