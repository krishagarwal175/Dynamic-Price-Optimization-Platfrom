"""Product persistence."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.product import Product
from app.repositories.base import BaseRepository
from app.repositories.pagination import Page, PageParams


class ProductRepository(BaseRepository[Product]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Product)

    def get_by_sku(self, sku: str) -> Product | None:
        return self._session.scalar(select(Product).where(Product.sku == sku))

    def list_by_category(
        self,
        category_id: int,
        params: PageParams | None = None,
    ) -> Page[Product]:
        params = params or PageParams()
        stmt = (
            select(Product)
            .where(Product.category_id == category_id)
            .limit(params.limit)
            .offset(params.offset)
        )
        items = list(self._session.scalars(stmt).all())
        total = self._session.scalar(
            select(func.count()).select_from(Product).where(Product.category_id == category_id)
        )
        return Page(items=items, total=total or 0, limit=params.limit, offset=params.offset)
