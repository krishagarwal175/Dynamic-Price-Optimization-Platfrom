"""HistoricalSale persistence."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.historical_sale import HistoricalSale
from app.models.product import Product
from app.repositories.base import BaseRepository


class HistoricalSaleRepository(BaseRepository[HistoricalSale]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, HistoricalSale)

    def list_for_product(self, product_id: int) -> list[HistoricalSale]:
        stmt = (
            select(HistoricalSale)
            .where(HistoricalSale.product_id == product_id)
            .order_by(HistoricalSale.sale_date)
        )
        return list(self._session.scalars(stmt).all())

    def unit_economics(
        self,
        *,
        product_id: int | None = None,
        category_id: int | None = None,
    ) -> list[tuple[int, Decimal, Decimal]]:
        """Return ``(quantity, unit_price, product.unit_cost)`` rows for analytics.

        A single join avoids N+1 loading. Optionally scoped to a product or a category;
        with no scope it returns every sale line in the dataset.
        """
        stmt = select(
            HistoricalSale.quantity,
            HistoricalSale.unit_price,
            Product.unit_cost,
        ).join(Product, HistoricalSale.product_id == Product.id)
        if product_id is not None:
            stmt = stmt.where(HistoricalSale.product_id == product_id)
        if category_id is not None:
            stmt = stmt.where(Product.category_id == category_id)
        return [(int(q), up, uc) for q, up, uc in self._session.execute(stmt).all()]
