"""CompetitorPrice persistence."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.competitor_price import CompetitorPrice
from app.repositories.base import BaseRepository


class CompetitorPriceRepository(BaseRepository[CompetitorPrice]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, CompetitorPrice)

    def list_for_product(self, product_id: int) -> list[CompetitorPrice]:
        stmt = (
            select(CompetitorPrice)
            .where(CompetitorPrice.product_id == product_id)
            .order_by(CompetitorPrice.observed_at)
        )
        return list(self._session.scalars(stmt).all())
