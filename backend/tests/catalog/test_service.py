"""Unit coverage for the catalog service and product search branches."""

from __future__ import annotations

from decimal import Decimal

import pytest
from sqlalchemy.orm import Session

from app.core.database import transaction
from app.core.errors import NotFoundError
from app.models.category import Category
from app.models.product import Product
from app.services.catalog import CatalogService
from tests.support import make_business_db


def _seeded_service() -> tuple[Session, CatalogService]:
    _, factory = make_business_db()
    session = factory()
    with transaction(session):
        bev = Category(name="Beverages")
        snacks = Category(name="Snacks")
        session.add_all([bev, snacks])
        session.flush()
        session.add_all(
            [
                Product(
                    category_id=bev.id,
                    sku="COLA-1",
                    name="Cola",
                    unit_cost=Decimal("1.00"),
                    base_price=Decimal("2.50"),
                ),
                Product(
                    category_id=snacks.id,
                    sku="CHIP-1",
                    name="Chips",
                    unit_cost=Decimal("0.80"),
                    base_price=Decimal("1.90"),
                ),
            ]
        )
    return session, CatalogService(session)


@pytest.mark.integration
def test_search_by_term_filters() -> None:
    _, service = _seeded_service()
    page = service.list_products(query="cola")
    assert [p.sku for p in page.items] == ["COLA-1"]
    assert page.total == 1


@pytest.mark.integration
def test_whitespace_query_is_treated_as_no_filter() -> None:
    _, service = _seeded_service()
    page = service.list_products(query="   ")
    assert page.total == 2  # blank search does not accidentally filter to nothing


@pytest.mark.integration
def test_category_filter() -> None:
    session, service = _seeded_service()
    snacks = session.query(Category).filter_by(name="Snacks").one()
    page = service.list_products(category_id=snacks.id)
    assert [p.sku for p in page.items] == ["CHIP-1"]


@pytest.mark.integration
def test_list_categories_returns_all() -> None:
    _, service = _seeded_service()
    assert {c.name for c in service.list_categories()} == {"Beverages", "Snacks"}


@pytest.mark.integration
def test_get_missing_product_raises_not_found() -> None:
    _, service = _seeded_service()
    with pytest.raises(NotFoundError):
        service.get_product(99999)
