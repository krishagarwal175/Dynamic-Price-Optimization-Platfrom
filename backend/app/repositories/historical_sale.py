"""HistoricalSale persistence."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.historical_sale import HistoricalSale
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
