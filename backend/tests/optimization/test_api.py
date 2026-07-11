"""End-to-end API tests for the optimization endpoints (read-only)."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import date, timedelta
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
_PATTERN = [(4, 100), (6, 44), (4, 100), (6, 44), (4, 100), (6, 44)]


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

    session = application.state.db_sessionmaker()
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
        _IDS.update({"p1": p1.id, "thin": thin.id})
    session.close()

    with TestClient(application) as test_client:
        yield test_client


@pytest.mark.integration
def test_product_optimization_endpoint(client: TestClient) -> None:
    response = client.get(f"/api/v1/analytics/products/{_IDS['p1']}/optimization")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["sku"] == "P1"
    opt = data["optimization"]
    assert opt["objective"] == "maximize_gross_profit"
    assert opt["recommended_price"] > 0
    assert opt["iterations"] > 0
    assert "assumptions" in opt and opt["assumptions"]


@pytest.mark.integration
def test_optimization_objective_and_constraint_params(client: TestClient) -> None:
    response = client.get(
        f"/api/v1/analytics/products/{_IDS['p1']}/optimization",
        params={"objective": "maximize_revenue", "min_price": 4.5},
    )
    assert response.status_code == 200
    opt = response.json()["data"]["optimization"]
    assert opt["objective"] == "maximize_revenue"
    assert opt["recommended_price"] >= 4.5 - 1e-6


@pytest.mark.integration
def test_dataset_optimization_endpoint(client: TestClient) -> None:
    response = client.get("/api/v1/analytics/optimization")
    assert response.status_code == 200
    assert response.json()["data"]["scope"] == "dataset"


@pytest.mark.integration
def test_missing_product_returns_404(client: TestClient) -> None:
    response = client.get("/api/v1/analytics/products/9999/optimization")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


@pytest.mark.integration
def test_insufficient_data_returns_422(client: TestClient) -> None:
    response = client.get(f"/api/v1/analytics/products/{_IDS['thin']}/optimization")
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.integration
def test_invalid_objective_rejected(client: TestClient) -> None:
    response = client.get(
        f"/api/v1/analytics/products/{_IDS['p1']}/optimization",
        params={"objective": "maximize_unicorns"},
    )
    assert response.status_code == 422
