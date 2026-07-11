"""End-to-end API tests for the read-only analytics endpoints."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import app.models  # noqa: F401  (register models before create_all)
from app.core.config import AppEnv, Settings
from app.core.database import Base, transaction
from app.main import create_app
from app.models.category import Category
from app.models.historical_sale import HistoricalSale
from app.models.product import Product

_IDS: dict[str, int] = {}


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    settings = Settings(  # type: ignore[call-arg]
        _env_file=None,
        app_env=AppEnv.LOCAL,
        app_name="Test API",
        log_level="WARNING",
        cors_allowed_origins=["http://testserver"],
        database_url="sqlite://",
        file_storage_path=str(tmp_path / "storage"),
    )
    application = create_app(settings)
    Base.metadata.create_all(application.state.db_engine)

    factory = application.state.db_sessionmaker
    session = factory()
    with transaction(session):
        bev = Category(name="Beverages")
        session.add(bev)
        session.flush()
        p1 = Product(
            category_id=bev.id,
            sku="P1",
            name="Cola",
            unit_cost=Decimal("2.00"),
            base_price=Decimal("5.00"),
        )
        empty = Product(
            category_id=bev.id,
            sku="P0",
            name="NoSales",
            unit_cost=Decimal("1.00"),
            base_price=Decimal("2.00"),
        )
        session.add_all([p1, empty])
        session.flush()
        session.add(
            HistoricalSale(
                product_id=p1.id,
                sale_date=date(2026, 1, 1),
                quantity=10,
                unit_price=Decimal("5.00"),
            )
        )
        _IDS.update({"bev": bev.id, "p1": p1.id, "empty": empty.id})
    session.close()

    with TestClient(application) as test_client:
        yield test_client


@pytest.mark.integration
def test_dataset_financial_endpoint(client: TestClient) -> None:
    response = client.get("/api/v1/analytics/financial")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["scope"] == "dataset"
    assert data["metrics"]["revenue"] == "50.00"
    assert data["metrics"]["total_units"] == 10


@pytest.mark.integration
def test_product_financial_endpoint(client: TestClient) -> None:
    response = client.get(f"/api/v1/analytics/products/{_IDS['p1']}")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["sku"] == "P1"
    assert data["metrics"]["gross_profit"] == "30.00"


@pytest.mark.integration
def test_fixed_cost_query_affects_net_profit(client: TestClient) -> None:
    response = client.get("/api/v1/analytics/financial", params={"fixed_cost": "100"})
    assert response.status_code == 200
    metrics = response.json()["data"]["metrics"]
    assert metrics["total_fixed_cost"] == "100.00"
    assert metrics["net_profit"] == "-70.00"  # gross profit 30 - 100


@pytest.mark.integration
def test_category_financial_endpoint(client: TestClient) -> None:
    response = client.get(f"/api/v1/analytics/categories/{_IDS['bev']}")
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "Beverages"


@pytest.mark.integration
def test_missing_product_returns_404(client: TestClient) -> None:
    response = client.get("/api/v1/analytics/products/9999")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


@pytest.mark.integration
def test_product_without_sales_returns_422(client: TestClient) -> None:
    response = client.get(f"/api/v1/analytics/products/{_IDS['empty']}")
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.integration
def test_negative_fixed_cost_rejected_by_query_validation(client: TestClient) -> None:
    response = client.get("/api/v1/analytics/financial", params={"fixed_cost": "-5"})
    assert response.status_code == 422
