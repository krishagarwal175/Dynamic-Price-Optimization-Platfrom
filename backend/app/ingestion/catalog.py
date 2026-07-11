"""Product-catalog dataset type: schema + importer.

Maps validated rows into the business entities (Category, Product) using the repository
layer. Contains no analytics — only normalization and persistence mapping.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

import pandas as pd
from sqlalchemy.orm import Session

from app.ingestion.validation import ColumnSpec, ColumnType, DatasetSchema
from app.models.category import Category
from app.models.product import Product
from app.repositories.category import CategoryRepository
from app.repositories.product import ProductRepository

PRODUCT_CATALOG_SCHEMA = DatasetSchema(
    columns=[
        ColumnSpec("sku", ColumnType.STRING, required=True, unique=True),
        ColumnSpec("name", ColumnType.STRING, required=True),
        ColumnSpec("category", ColumnType.STRING, required=True),
        ColumnSpec("unit_cost", ColumnType.NUMERIC, required=True, non_negative=True),
        ColumnSpec("base_price", ColumnType.NUMERIC, required=True, non_negative=True),
        ColumnSpec("description", ColumnType.STRING, required=False),
        ColumnSpec("currency", ColumnType.STRING, required=False),
    ]
)

_CENTS = Decimal("0.01")


@dataclass(frozen=True)
class ImportSummary:
    rows_imported: int
    categories_created: int
    products_created: int


def _money(value: object) -> Decimal:
    try:
        return Decimal(str(value)).quantize(_CENTS)
    except (InvalidOperation, ValueError) as exc:  # pragma: no cover - validated upstream
        raise ValueError(f"Invalid monetary value: {value!r}") from exc


def _clean(value: object) -> str | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip()
    return text or None


class ProductCatalogImporter:
    """Imports a product-catalog dataset into Category/Product."""

    schema = PRODUCT_CATALOG_SCHEMA

    def run(self, session: Session, df: pd.DataFrame) -> ImportSummary:
        categories = CategoryRepository(session)
        products = ProductRepository(session)

        cache: dict[str, Category] = {}
        categories_created = 0
        products_created = 0

        records = df.where(pd.notna(df), None).to_dict(orient="records")
        for record in records:
            category_name = _clean(record.get("category")) or ""
            category = cache.get(category_name)
            if category is None:
                category = categories.get_by_name(category_name)
                if category is None:
                    category = categories.add(Category(name=category_name))
                    categories_created += 1
                cache[category_name] = category

            currency = _clean(record.get("currency")) or "USD"
            products.add(
                Product(
                    category_id=category.id,
                    sku=_clean(record.get("sku")) or "",
                    name=_clean(record.get("name")) or "",
                    description=_clean(record.get("description")),
                    unit_cost=_money(record.get("unit_cost")),
                    base_price=_money(record.get("base_price")),
                    currency=currency,
                )
            )
            products_created += 1

        return ImportSummary(
            rows_imported=len(records),
            categories_created=categories_created,
            products_created=products_created,
        )
