"""CompetitorPrice: an observed competitor price for a product on a date.

Association object linking Product and Competitor (many-to-many with attributes). Kept
normalized so competitor identity is not repeated per price observation.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.orm import IntIdMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.competitor import Competitor
    from app.models.product import Product


class CompetitorPrice(Base, IntIdMixin, TimestampMixin):
    """A single competitor price observation for a product."""

    __tablename__ = "competitor_price"
    __table_args__ = (
        CheckConstraint("price >= 0", name="price_non_negative"),
        UniqueConstraint(
            "product_id",
            "competitor_id",
            "observed_at",
            name="uq_competitor_price_product_competitor_observed",
        ),
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("product.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    competitor_id: Mapped[int] = mapped_column(
        ForeignKey("competitor.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    observed_at: Mapped[date] = mapped_column(Date, nullable=False)

    product: Mapped[Product] = relationship(back_populates="competitor_prices")
    competitor: Mapped[Competitor] = relationship(back_populates="prices")
