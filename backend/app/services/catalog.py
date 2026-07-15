"""Catalog read service — thin, read-only access to products and categories.

Presentation support for the frontend catalog. Contains no business/analytics logic; it
simply reads via the existing repositories.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.models.category import Category
from app.models.product import Product
from app.repositories.category import CategoryRepository
from app.repositories.pagination import Page, PageParams
from app.repositories.product import ProductRepository


class CatalogService:
    def __init__(self, session: Session) -> None:
        self._products = ProductRepository(session)
        self._categories = CategoryRepository(session)

    def list_products(
        self,
        *,
        query: str | None = None,
        category_id: int | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Page[Product]:
        return self._products.search(
            query=query, category_id=category_id, params=PageParams(limit=limit, offset=offset)
        )

    def get_product(self, product_id: int) -> Product:
        product = self._products.get(product_id)
        if product is None:
            raise NotFoundError(f"Product {product_id} not found.")
        return product

    def list_categories(self) -> list[Category]:
        return self._categories.list(PageParams(limit=200)).items
