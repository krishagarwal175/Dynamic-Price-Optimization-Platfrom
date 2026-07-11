"""End-to-end API tests for the forecast endpoints."""

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
        for i in range(6):
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
        _IDS.update({"p1": p1.id, "one": one.id})
    session.close()

    with TestClient(application) as test_client:
        yield test_client


@pytest.mark.integration
def test_product_forecast_endpoint(client: TestClient) -> None:
    response = client.get(
        f"/api/v1/analytics/products/{_IDS['p1']}/forecast", params={"horizon": 3}
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["sku"] == "P1"
    forecast = data["forecast"]
    assert forecast["selected_strategy"] == "naive"
    assert forecast["horizon"] == 3
    assert len(forecast["forecast"]) == 3
    assert forecast["forecast"][0]["predicted"] == pytest.approx(10.0)
    assert len(forecast["history"]) == 6
    assert "rmse" in forecast["diagnostics"]
    assert len(forecast["alternatives"]) == 4


@pytest.mark.integration
def test_dataset_forecast_endpoint(client: TestClient) -> None:
    response = client.get("/api/v1/analytics/forecast")
    assert response.status_code == 200
    assert response.json()["data"]["scope"] == "dataset"


@pytest.mark.integration
def test_missing_product_returns_404(client: TestClient) -> None:
    response = client.get("/api/v1/analytics/products/9999/forecast")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


@pytest.mark.integration
def test_insufficient_history_returns_422(client: TestClient) -> None:
    response = client.get(f"/api/v1/analytics/products/{_IDS['one']}/forecast")
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.integration
def test_invalid_horizon_rejected(client: TestClient) -> None:
    response = client.get(
        f"/api/v1/analytics/products/{_IDS['p1']}/forecast", params={"horizon": 0}
    )
    assert response.status_code == 422
