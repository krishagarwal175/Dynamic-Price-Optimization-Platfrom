"""Tests for the elasticity path of the analytics service."""

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
from app.pricing.elasticity.models import ElasticityClass
from app.services.analytics import AnalyticsService
from tests.support import make_business_db

# Q = 200 / P  -> perfect log-log line, elasticity = -1 (unit elastic). Integer quantities.
_UNIT_ELASTIC = [(2, 100), (4, 50), (5, 40), (8, 25)]


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
        flat = Product(
            category_id=cat.id,
            sku="P0",
            name="Flat",
            unit_cost=Decimal("1.00"),
            base_price=Decimal("4.00"),
        )
        session.add_all([p1, flat])
        session.flush()
        for price, qty in _UNIT_ELASTIC:
            session.add(
                HistoricalSale(
                    product_id=p1.id,
                    sale_date=date(2026, 1, 1),
                    quantity=qty,
                    unit_price=Decimal(price),
                )
            )
        # `flat` has a single sale -> insufficient observations.
        session.add(
            HistoricalSale(
                product_id=flat.id,
                sale_date=date(2026, 1, 1),
                quantity=10,
                unit_price=Decimal("4.00"),
            )
        )
        return {"p1": p1.id, "flat": flat.id}


@pytest.mark.integration
def test_product_elasticity() -> None:
    _, factory = make_business_db()
    with session_scope(factory) as session:
        ids = _seed(session)
        product, analysis = AnalyticsService(session).product_elasticity(ids["p1"])
        assert product.sku == "P1"
        assert analysis.elasticity_coefficient == pytest.approx(-1.0, abs=1e-6)
        assert analysis.classification is ElasticityClass.UNIT_ELASTIC
        assert analysis.profit_curve is not None  # product unit cost drives profit curve


@pytest.mark.integration
def test_dataset_elasticity_runs() -> None:
    _, factory = make_business_db()
    with session_scope(factory) as session:
        _seed(session)
        analysis = AnalyticsService(session).dataset_elasticity()
        assert analysis.diagnostics.sample_size >= 4


@pytest.mark.integration
def test_missing_product_raises_not_found() -> None:
    _, factory = make_business_db()
    with session_scope(factory) as session:
        _seed(session)
        with pytest.raises(NotFoundError):
            AnalyticsService(session).product_elasticity(9999)


@pytest.mark.integration
def test_insufficient_data_maps_to_validation_error() -> None:
    _, factory = make_business_db()
    with session_scope(factory) as session:
        ids = _seed(session)
        with pytest.raises(ValidationError):
            AnalyticsService(session).product_elasticity(ids["flat"])
