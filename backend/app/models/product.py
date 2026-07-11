"""Product entity: a sellable item belonging to a category."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.orm import IntIdMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.competitor_price import CompetitorPrice
    from app.models.historical_sale import HistoricalSale


class Product(Base, IntIdMixin, TimestampMixin):
    """A product in the catalog. Costs/prices are stored as exact decimals."""

    __tablename__ = "product"
    __table_args__ = (
        CheckConstraint("unit_cost >= 0", name="unit_cost_non_negative"),
        CheckConstraint("base_price >= 0", name="base_price_non_negative"),
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey("category.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    sku: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    base_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    category: Mapped[Category] = relationship(back_populates="products")
    sales: Mapped[list[HistoricalSale]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    competitor_prices: Mapped[list[CompetitorPrice]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
