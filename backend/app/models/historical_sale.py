"""HistoricalSale entity: an observed sales record for a product."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, ForeignKey, Index, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.orm import IntIdMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.product import Product


class HistoricalSale(Base, IntIdMixin, TimestampMixin):
    """A single observed sale: quantity sold at a unit price on a date.

    Revenue is intentionally not stored (derivable from quantity * unit_price) to keep the
    model normalized.
    """

    __tablename__ = "historical_sale"
    __table_args__ = (
        CheckConstraint("quantity >= 0", name="quantity_non_negative"),
        CheckConstraint("unit_price >= 0", name="unit_price_non_negative"),
        Index("ix_historical_sale_product_date", "product_id", "sale_date"),
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("product.id", ondelete="CASCADE"),
        nullable=False,
    )
    sale_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    product: Mapped[Product] = relationship(back_populates="sales")
