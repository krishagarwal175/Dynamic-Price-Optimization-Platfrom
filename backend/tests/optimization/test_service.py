"""Tests for the optimization orchestration in the analytics service."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest
from sqlalchemy.orm import Session

from app.core.database import session_scope, transaction
from app.core.errors import NotFoundError, ValidationError
from app.models.category import Category
from app.models.historical_sale import HistoricalSale
from app.models.product import Product
from app.pricing.optimization import Objective, OptimizationConstraints
from app.services.analytics import AnalyticsService
from tests.support import make_business_db

# Two price levels giving elasticity ~ -2 (Q = 100 at 4, ~44 at 6), across 6 dated periods.
_PATTERN = [(4, 100), (6, 44), (4, 100), (6, 44), (4, 100), (6, 44)]


def _seed(session: Session) -> dict[str, int]:
    with transaction(session):
        cat = Category(name="Beverages")
        session.add(cat)
        session.flush()
        p1 = Product(
            category_id=cat.id,
            sku="P1",
            name="Cola",
            unit_cost=Decimal("2.00"),
            base_price=Decimal("5.00"),
        )
        thin = Product(
            category_id=cat.id,
            sku="P0",
            name="Thin",
            unit_cost=Decimal("2.00"),
            base_price=Decimal("5.00"),
        )
        session.add_all([p1, thin])
        session.flush()
        start = date(2026, 1, 1)
        for i, (price, qty) in enumerate(_PATTERN):
            session.add(
                HistoricalSale(
                    product_id=p1.id,
                    sale_date=start + timedelta(days=i),
                    quantity=qty,
                    unit_price=Decimal(price),
                )
            )
        session.add(
            HistoricalSale(
                product_id=thin.id, sale_date=start, quantity=10, unit_price=Decimal("5.00")
            )
        )
        return {"p1": p1.id, "thin": thin.id}


@pytest.mark.integration
def test_product_optimization_recommends_profit_price() -> None:
    _, factory = make_business_db()
    with session_scope(factory) as session:
        ids = _seed(session)
        product, result = AnalyticsService(session).product_optimization(
            ids["p1"], objective=Objective.MAXIMIZE_GROSS_PROFIT
        )
        assert product.sku == "P1"
        # closed-form profit optimum ~ c·E/(E+1) ≈ 3.9 for E ≈ -2, c = 2
        assert 3.4 <= result.recommended_price <= 4.4
        assert result.expected_demand > 0


@pytest.mark.integration
def test_product_optimization_with_constraint() -> None:
    _, factory = make_business_db()
    with session_scope(factory) as session:
        ids = _seed(session)
        _, result = AnalyticsService(session).product_optimization(
            ids["p1"],
            objective=Objective.MAXIMIZE_GROSS_PROFIT,
            constraints=OptimizationConstraints(min_price=4.5),
        )
        assert result.recommended_price >= 4.5 - 1e-6


@pytest.mark.integration
def test_dataset_optimization_runs() -> None:
    _, factory = make_business_db()
    with session_scope(factory) as session:
        _seed(session)
        result = AnalyticsService(session).dataset_optimization(
            objective=Objective.MAXIMIZE_REVENUE
        )
        assert result.recommended_price > 0


@pytest.mark.integration
def test_missing_product_raises_not_found() -> None:
    _, factory = make_business_db()
    with session_scope(factory) as session:
        _seed(session)
        with pytest.raises(NotFoundError):
            AnalyticsService(session).product_optimization(
                9999, objective=Objective.MAXIMIZE_GROSS_PROFIT
            )


@pytest.mark.integration
def test_insufficient_data_maps_to_validation_error() -> None:
    _, factory = make_business_db()
    with session_scope(factory) as session:
        ids = _seed(session)
        with pytest.raises(ValidationError):
            AnalyticsService(session).product_optimization(
                ids["thin"], objective=Objective.MAXIMIZE_GROSS_PROFIT
            )
