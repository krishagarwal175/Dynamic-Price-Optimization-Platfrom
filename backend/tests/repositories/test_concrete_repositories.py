"""Tests for the concrete entity repositories."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from app.core.database import session_scope, transaction
from app.models.category import Category
from app.models.competitor import Competitor
from app.models.competitor_price import CompetitorPrice
from app.models.historical_sale import HistoricalSale
from app.models.product import Product
from app.repositories.category import CategoryRepository
from app.repositories.competitor import CompetitorRepository
from app.repositories.competitor_price import CompetitorPriceRepository
from app.repositories.historical_sale import HistoricalSaleRepository
from app.repositories.product import ProductRepository
from tests.support import make_business_db


@pytest.mark.integration
def test_category_crud_and_get_by_name() -> None:
    _, factory = make_business_db()
    with session_scope(factory) as session, transaction(session):
        repo = CategoryRepository(session)
        created = repo.add(Category(name="Electronics"))
        assert created.id is not None
        assert repo.get(created.id) is not None
        assert repo.get_by_name("Electronics") is created
        assert repo.get_by_name("Missing") is None


@pytest.mark.integration
def test_product_get_by_sku_and_list_by_category() -> None:
    _, factory = make_business_db()
    with session_scope(factory) as session, transaction(session):
        cat_repo = CategoryRepository(session)
        prod_repo = ProductRepository(session)
        c1 = cat_repo.add(Category(name="A"))
        c2 = cat_repo.add(Category(name="B"))
        for i in range(3):
            prod_repo.add(
                Product(
                    category_id=c1.id,
                    sku=f"A-{i}",
                    name="p",
                    unit_cost=Decimal("1.00"),
                    base_price=Decimal("2.00"),
                )
            )
        prod_repo.add(
            Product(
                category_id=c2.id,
                sku="B-0",
                name="p",
                unit_cost=Decimal("1.00"),
                base_price=Decimal("2.00"),
            )
        )

        assert prod_repo.get_by_sku("A-1") is not None
        page = prod_repo.list_by_category(c1.id)
        assert page.total == 3
        assert all(p.category_id == c1.id for p in page.items)


@pytest.mark.integration
def test_historical_sale_list_for_product_is_ordered() -> None:
    _, factory = make_business_db()
    with session_scope(factory) as session, transaction(session):
        cat = CategoryRepository(session).add(Category(name="A"))
        product = ProductRepository(session).add(
            Product(
                category_id=cat.id,
                sku="S",
                name="p",
                unit_cost=Decimal("1.00"),
                base_price=Decimal("2.00"),
            )
        )
        repo = HistoricalSaleRepository(session)
        repo.add(
            HistoricalSale(
                product_id=product.id,
                sale_date=date(2026, 3, 1),
                quantity=1,
                unit_price=Decimal("2.00"),
            )
        )
        repo.add(
            HistoricalSale(
                product_id=product.id,
                sale_date=date(2026, 1, 1),
                quantity=2,
                unit_price=Decimal("2.00"),
            )
        )

        sales = repo.list_for_product(product.id)
        assert [s.sale_date for s in sales] == [date(2026, 1, 1), date(2026, 3, 1)]


@pytest.mark.integration
def test_competitor_and_price_repositories() -> None:
    _, factory = make_business_db()
    with session_scope(factory) as session, transaction(session):
        cat = CategoryRepository(session).add(Category(name="A"))
        product = ProductRepository(session).add(
            Product(
                category_id=cat.id,
                sku="S",
                name="p",
                unit_cost=Decimal("1.00"),
                base_price=Decimal("2.00"),
            )
        )
        comp_repo = CompetitorRepository(session)
        competitor = comp_repo.add(Competitor(name="RivalCo", website="https://rival.example"))
        assert comp_repo.get_by_name("RivalCo") is competitor

        price_repo = CompetitorPriceRepository(session)
        price_repo.add(
            CompetitorPrice(
                product_id=product.id,
                competitor_id=competitor.id,
                price=Decimal("1.80"),
                observed_at=date(2026, 1, 1),
            )
        )
        assert len(price_repo.list_for_product(product.id)) == 1
