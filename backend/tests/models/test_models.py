"""Tests for business models: creation, relationships, and constraints."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from app.core.database import session_scope, transaction
from app.models.category import Category
from app.models.competitor import Competitor
from app.models.competitor_price import CompetitorPrice
from app.models.historical_sale import HistoricalSale
from app.models.product import Product
from tests.support import make_business_db


def _product(category_id: int, sku: str = "SKU-1") -> Product:
    return Product(
        category_id=category_id,
        sku=sku,
        name="Widget",
        unit_cost=Decimal("2.00"),
        base_price=Decimal("5.00"),
    )


@pytest.mark.integration
def test_create_product_with_category() -> None:
    _, factory = make_business_db()
    with session_scope(factory) as session, transaction(session):
        cat = Category(name="Beverages")
        session.add(cat)
        session.flush()
        session.add(_product(cat.id))

    with session_scope(factory) as verify:
        product = verify.query(Product).one()
        assert product.category.name == "Beverages"
        assert product.created_at is not None


@pytest.mark.integration
def test_relationships_backpopulate() -> None:
    _, factory = make_business_db()
    with session_scope(factory) as session, transaction(session):
        cat = Category(name="Snacks")
        session.add(cat)
        session.flush()
        product = _product(cat.id)
        product.sales.append(
            HistoricalSale(sale_date=date(2026, 1, 1), quantity=3, unit_price=Decimal("5.00"))
        )
        comp = Competitor(name="RivalCo")
        session.add(comp)
        session.flush()
        product.competitor_prices.append(
            CompetitorPrice(
                competitor_id=comp.id, price=Decimal("4.50"), observed_at=date(2026, 1, 1)
            )
        )
        session.add(product)

    with session_scope(factory) as verify:
        product = verify.query(Product).one()
        assert len(product.sales) == 1
        assert len(product.competitor_prices) == 1
        assert product.sales[0].product is product


@pytest.mark.integration
def test_unique_sku_enforced() -> None:
    _, factory = make_business_db()
    with pytest.raises(IntegrityError), session_scope(factory) as session, transaction(session):
        cat = Category(name="C")
        session.add(cat)
        session.flush()
        session.add(_product(cat.id, sku="DUP"))
        session.add(_product(cat.id, sku="DUP"))


@pytest.mark.integration
def test_check_constraint_rejects_negative_price() -> None:
    _, factory = make_business_db()
    with pytest.raises(IntegrityError), session_scope(factory) as session, transaction(session):
        cat = Category(name="C")
        session.add(cat)
        session.flush()
        bad = _product(cat.id)
        bad.base_price = Decimal("-1.00")
        session.add(bad)


@pytest.mark.integration
def test_deleting_product_cascades_to_sales() -> None:
    _, factory = make_business_db()
    with session_scope(factory) as session, transaction(session):
        cat = Category(name="C")
        session.add(cat)
        session.flush()
        product = _product(cat.id)
        product.sales.append(
            HistoricalSale(sale_date=date(2026, 1, 1), quantity=1, unit_price=Decimal("5.00"))
        )
        session.add(product)

    with session_scope(factory) as session, transaction(session):
        product = session.query(Product).one()
        session.delete(product)

    with session_scope(factory) as verify:
        assert verify.query(HistoricalSale).count() == 0


@pytest.mark.integration
def test_deleting_category_with_products_is_restricted() -> None:
    _, factory = make_business_db()
    with session_scope(factory) as session, transaction(session):
        cat = Category(name="C")
        session.add(cat)
        session.flush()
        session.add(_product(cat.id))

    with pytest.raises(IntegrityError), session_scope(factory) as session, transaction(session):
        cat = session.query(Category).one()
        session.delete(cat)
