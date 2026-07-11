"""Competitor entity: a rival whose prices we track."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.orm import IntIdMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.competitor_price import CompetitorPrice


class Competitor(Base, IntIdMixin, TimestampMixin):
    """A competitor. Its observed prices per product live in ``CompetitorPrice``."""

    __tablename__ = "competitor"

    name: Mapped[str] = mapped_column(String(150), nullable=False, unique=True, index=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)

    prices: Mapped[list[CompetitorPrice]] = relationship(
        back_populates="competitor",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
