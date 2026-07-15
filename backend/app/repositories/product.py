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

    def search(
        self,
        *,
        query: str | None = None,
        category_id: int | None = None,
        params: PageParams | None = None,
    ) -> Page[Product]:
        """Paginated catalog search by SKU/name substring and optional category."""
        params = params or PageParams()
        filters = []
        if category_id is not None:
            filters.append(Product.category_id == category_id)
        if query:
            like = f"%{query.strip()}%"
            filters.append(Product.sku.ilike(like) | Product.name.ilike(like))

        base = select(Product)
        count_stmt = select(func.count()).select_from(Product)
        for condition in filters:
            base = base.where(condition)
            count_stmt = count_stmt.where(condition)

        stmt = base.order_by(Product.sku).limit(params.limit).offset(params.offset)
        items = list(self._session.scalars(stmt).all())
        total = self._session.scalar(count_stmt) or 0
        return Page(items=items, total=total, limit=params.limit, offset=params.offset)
