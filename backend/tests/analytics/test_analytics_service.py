"""Tests for the analytics service: aggregation scopes and error mapping."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy.orm import Session

from app.core.database import session_scope, transaction
from app.core.errors import NotFoundError, ValidationError
from app.models.category import Category
from app.models.historical_sale import HistoricalSale
from app.models.product import Product
from app.services.analytics import AnalyticsService
from tests.support import make_business_db


def _seed(session: Session) -> dict[str, int]:
    with transaction(session):
        bev = Category(name="Beverages")
        snacks = Category(name="Snacks")
        session.add_all([bev, snacks])
        session.flush()

        p1 = Product(
            category_id=bev.id,
            sku="P1",
            name="Cola",
            unit_cost=Decimal("2.00"),
            base_price=Decimal("5.00"),
        )
        p2 = Product(
            category_id=bev.id,
            sku="P2",
            name="Water",
            unit_cost=Decimal("1.00"),
            base_price=Decimal("3.00"),
        )
        p3 = Product(
            category_id=snacks.id,
            sku="P3",
            name="Chips",
            unit_cost=Decimal("5.00"),
            base_price=Decimal("10.00"),
        )
        session.add_all([p1, p2, p3])
        session.flush()

        session.add_all(
            [
                HistoricalSale(
                    product_id=p1.id,
                    sale_date=date(2026, 1, 1),
                    quantity=10,
                    unit_price=Decimal("5.00"),
                ),
                HistoricalSale(
                    product_id=p2.id,
                    sale_date=date(2026, 1, 1),
                    quantity=5,
                    unit_price=Decimal("3.00"),
                ),
                HistoricalSale(
                    product_id=p3.id,
                    sale_date=date(2026, 1, 1),
                    quantity=2,
                    unit_price=Decimal("10.00"),
                ),
            ]
        )
        return {"bev": bev.id, "snacks": snacks.id, "p1": p1.id, "p2": p2.id, "p3": p3.id}


@pytest.mark.integration
def test_product_scope() -> None:
    _, factory = make_business_db()
    with session_scope(factory) as session:
        ids = _seed(session)
        service = AnalyticsService(session)
        product, metrics = service.product_financials(ids["p1"])
        assert product.sku == "P1"
        assert metrics.revenue == Decimal("50.00")
        assert metrics.total_units == 10
        assert metrics.gross_profit == Decimal("30.00")


@pytest.mark.integration
def test_category_scope_aggregates_products() -> None:
    _, factory = make_business_db()
    with session_scope(factory) as session:
        ids = _seed(session)
        service = AnalyticsService(session)
        category, metrics = service.category_financials(ids["bev"])
        assert category.name == "Beverages"
        assert metrics.revenue == Decimal("65.00")  # 50 + 15
        assert metrics.total_units == 15
        assert metrics.cogs == Decimal("25.00")  # 10*2 + 5*1


@pytest.mark.integration
def test_dataset_scope_aggregates_everything() -> None:
    _, factory = make_business_db()
    with session_scope(factory) as session:
        _seed(session)
        metrics = AnalyticsService(session).dataset_financials()
        assert metrics.revenue == Decimal("85.00")  # 50 + 15 + 20
        assert metrics.total_units == 17
        assert metrics.gross_profit == Decimal("50.00")  # 85 - 35


@pytest.mark.integration
def test_missing_product_raises_not_found() -> None:
    _, factory = make_business_db()
    with session_scope(factory) as session:
        _seed(session)
        with pytest.raises(NotFoundError):
            AnalyticsService(session).product_financials(9999)


@pytest.mark.integration
def test_no_data_maps_to_validation_error() -> None:
    _, factory = make_business_db()
    # Empty dataset -> insufficient data -> ValidationError (422).
    with session_scope(factory) as session, pytest.raises(ValidationError):
        AnalyticsService(session).dataset_financials()
