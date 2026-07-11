"""Tests for the forecasting path of the analytics service."""

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
from app.pricing.forecasting import ForecastMethod
from app.services.analytics import AnalyticsService
from tests.support import make_business_db


def _seed(session: Session) -> dict[str, int]:
    with transaction(session):
        cat = Category(name="Beverages")
        session.add(cat)
        session.flush()
        p1 = Product(
            category_id=cat.id,
            sku="P1",
            name="Cola",
            unit_cost=Decimal("1.00"),
            base_price=Decimal("4.00"),
        )
        one = Product(
            category_id=cat.id,
            sku="P0",
            name="OneSale",
            unit_cost=Decimal("1.00"),
            base_price=Decimal("4.00"),
        )
        session.add_all([p1, one])
        session.flush()
        start = date(2026, 1, 1)
        for i in range(6):  # constant demand of 10/day
            session.add(
                HistoricalSale(
                    product_id=p1.id,
                    sale_date=start + timedelta(days=i),
                    quantity=10,
                    unit_price=Decimal("4.00"),
                )
            )
        session.add(
            HistoricalSale(
                product_id=one.id, sale_date=start, quantity=5, unit_price=Decimal("4.00")
            )
        )
        return {"p1": p1.id, "one": one.id}


@pytest.mark.integration
def test_product_forecast() -> None:
    _, factory = make_business_db()
    with session_scope(factory) as session:
        ids = _seed(session)
        product, result = AnalyticsService(session).product_forecast(ids["p1"], horizon=3)
        assert product.sku == "P1"
        assert result.selected_strategy is ForecastMethod.NAIVE
        assert len(result.forecast) == 3
        assert result.forecast[0].predicted == pytest.approx(10.0)
        assert len(result.history) == 6


@pytest.mark.integration
def test_dataset_forecast_runs() -> None:
    _, factory = make_business_db()
    with session_scope(factory) as session:
        _seed(session)
        result = AnalyticsService(session).dataset_forecast(horizon=2)
        assert result.diagnostics.sample_size >= 2


@pytest.mark.integration
def test_missing_product_raises_not_found() -> None:
    _, factory = make_business_db()
    with session_scope(factory) as session:
        _seed(session)
        with pytest.raises(NotFoundError):
            AnalyticsService(session).product_forecast(9999)


@pytest.mark.integration
def test_insufficient_history_maps_to_validation_error() -> None:
    _, factory = make_business_db()
    with session_scope(factory) as session:
        ids = _seed(session)
        with pytest.raises(ValidationError):
            AnalyticsService(session).product_forecast(ids["one"])
