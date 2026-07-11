"""End-to-end API tests for the elasticity endpoints."""

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
_UNIT_ELASTIC = [(2, 100), (4, 50), (5, 40), (8, 25)]


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
        session.add(
            HistoricalSale(
                product_id=flat.id,
                sale_date=date(2026, 1, 1),
                quantity=10,
                unit_price=Decimal("4.00"),
            )
        )
        _IDS.update({"p1": p1.id, "flat": flat.id})
    session.close()

    with TestClient(application) as test_client:
        yield test_client


@pytest.mark.integration
def test_product_elasticity_endpoint(client: TestClient) -> None:
    response = client.get(f"/api/v1/analytics/products/{_IDS['p1']}/elasticity")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["sku"] == "P1"
    analysis = data["analysis"]
    assert analysis["method"] == "log_log"
    assert analysis["classification"] == "unit_elastic"
    assert analysis["elasticity_coefficient"] == pytest.approx(-1.0, abs=1e-6)
    assert analysis["diagnostics"]["r_squared"] == pytest.approx(1.0)
    assert len(analysis["demand_curve"]) == 25
    assert analysis["profit_curve"] is not None


@pytest.mark.integration
def test_dataset_elasticity_endpoint(client: TestClient) -> None:
    response = client.get("/api/v1/analytics/elasticity")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["scope"] == "dataset"
    assert "elasticity_coefficient" in data["analysis"]


@pytest.mark.integration
def test_missing_product_returns_404(client: TestClient) -> None:
    response = client.get("/api/v1/analytics/products/9999/elasticity")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


@pytest.mark.integration
def test_insufficient_data_returns_422(client: TestClient) -> None:
    response = client.get(f"/api/v1/analytics/products/{_IDS['flat']}/elasticity")
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
