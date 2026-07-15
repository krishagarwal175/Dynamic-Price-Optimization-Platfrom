"""Catalog (read-only) API schemas — paginated product & category listings."""

from __future__ import annotations

from pydantic import BaseModel

from app.schemas.category import CategorySummary
from app.schemas.product import ProductSummary


class ProductListResponse(BaseModel):
    items: list[ProductSummary]
    total: int
    limit: int
    offset: int


class CategoryListResponse(BaseModel):
    items: list[CategorySummary]
    total: int
