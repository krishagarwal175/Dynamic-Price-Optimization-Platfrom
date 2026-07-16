"""Alembic migration environment.

The connection URL comes from the application's typed settings (a caller may override it
via ``config.set_main_option('sqlalchemy.url', ...)``, which tests use). ``target_metadata``
is the shared declarative ``Base.metadata`` so autogenerate sees every registered model.
"""

from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Import side-effect: registering all ORM models keeps Base.metadata complete for
# autogenerate.
import app.models  # noqa: F401  (imported for registration side-effect)
from app.core.config import get_settings
from app.core.database import Base, _normalize_url

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Resolve the URL: an explicitly-set option (e.g. from tests) wins; otherwise settings.
if not config.get_main_option("sqlalchemy.url"):
    url = _normalize_url(get_settings().database_url)
    # Escape '%' so ConfigParser interpolation doesn't choke on URL-encoded passwords
    # (e.g. a '@' in a Postgres password is encoded as '%40').
    config.set_main_option("sqlalchemy.url", url.replace("%", "%%"))

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Emit SQL without a live connection (``--sql`` mode)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against a live connection."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,  # enables SQLite ALTER via batch operations
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
