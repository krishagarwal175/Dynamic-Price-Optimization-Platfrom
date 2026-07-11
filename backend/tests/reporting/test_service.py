"""Tests for the reporting orchestration in the analytics service."""

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
from app.pricing.optimization import Objective
from app.services.analytics import AnalyticsService
from tests.support import make_business_db

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
def test_product_report_composes_all_sections() -> None:
    _, factory = make_business_db()
    with session_scope(factory) as session:
        ids = _seed(session)
        product, report = AnalyticsService(session).product_report(
            ids["p1"], objective=Objective.MAXIMIZE_GROSS_PROFIT
        )
        assert product.sku == "P1"
        assert report.metadata.subject.startswith("P1")
        assert report.scenario.rows
        assert report.executive_summary.recommended_price > 0


@pytest.mark.integration
def test_dataset_report_runs() -> None:
    _, factory = make_business_db()
    with session_scope(factory) as session:
        _seed(session)
        report = AnalyticsService(session).dataset_report(objective=Objective.MAXIMIZE_REVENUE)
        assert report.metadata.scope == "dataset"
        assert report.limitations.limitations


@pytest.mark.integration
def test_missing_product_raises_not_found() -> None:
    _, factory = make_business_db()
    with session_scope(factory) as session:
        _seed(session)
        with pytest.raises(NotFoundError):
            AnalyticsService(session).product_report(
                9999, objective=Objective.MAXIMIZE_GROSS_PROFIT
            )


@pytest.mark.integration
def test_insufficient_data_maps_to_validation_error() -> None:
    _, factory = make_business_db()
    with session_scope(factory) as session:
        ids = _seed(session)
        with pytest.raises(ValidationError):
            AnalyticsService(session).product_report(
                ids["thin"], objective=Objective.MAXIMIZE_GROSS_PROFIT
            )
