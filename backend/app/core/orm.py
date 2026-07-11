"""Reusable ORM building blocks: primary-key and timestamp conventions.

These mixins define project-wide model conventions (see ADR-0007) so every future entity
is consistent. They contain no business-specific fields.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class IntIdMixin:
    """Integer surrogate primary key (``id``) — the default key convention."""

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


class TimestampMixin:
    """``created_at`` / ``updated_at`` columns, database-populated in UTC."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
