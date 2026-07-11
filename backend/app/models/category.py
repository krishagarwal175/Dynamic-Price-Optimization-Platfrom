"""Category entity: a grouping of products."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.orm import IntIdMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.product import Product


class Category(Base, IntIdMixin, TimestampMixin):
    """A product category (e.g. "Beverages"). Parent of many products."""

    __tablename__ = "category"

    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # RESTRICT: a category with products cannot be deleted (protects referential data).
    products: Mapped[list[Product]] = relationship(
        back_populates="category",
        passive_deletes=True,
    )
