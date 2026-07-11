"""End-to-end API tests for the simulation endpoints (read-only)."""

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
def test_product_simulation_default(client: TestClient) -> None:
    response = client.get(f"/api/v1/analytics/products/{_IDS['p1']}/simulation")
    assert response.status_code == 200
    sim = response.json()["data"]["simulation"]
    labels = {s["label"] for s in sim["scenarios"]}
    assert {"Baseline", "Recommended"} <= labels
    assert sim["best_scenario"] in labels
    assert sim["ranking_by_objective"]


@pytest.mark.integration
def test_product_simulation_single_percentage_scenario(client: TestClient) -> None:
    response = client.get(
        f"/api/v1/analytics/products/{_IDS['p1']}/simulation",
        params={"scenario": "percentage_increase", "percentage_change": 0.1},
    )
    assert response.status_code == 200
    labels = {s["label"] for s in response.json()["data"]["simulation"]["scenarios"]}
    assert "+10%" in labels
    assert "Baseline" in labels


@pytest.mark.integration
def test_product_simulation_fixed_price_scenario(client: TestClient) -> None:
    response = client.get(
        f"/api/v1/analytics/products/{_IDS['p1']}/simulation",
        params={"scenario": "fixed_price", "price": 12},
    )
    assert response.status_code == 200
    scenarios = response.json()["data"]["simulation"]["scenarios"]
    fixed = next(s for s in scenarios if s["price"] == 12.0)
    assert fixed["scenario_type"] == "fixed_price"


@pytest.mark.integration
def test_dataset_simulation_endpoint(client: TestClient) -> None:
    response = client.get("/api/v1/analytics/simulation")
    assert response.status_code == 200
    assert response.json()["data"]["scope"] == "dataset"


@pytest.mark.integration
def test_missing_product_returns_404(client: TestClient) -> None:
    response = client.get("/api/v1/analytics/products/9999/simulation")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


@pytest.mark.integration
def test_insufficient_data_returns_422(client: TestClient) -> None:
    response = client.get(f"/api/v1/analytics/products/{_IDS['thin']}/simulation")
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.integration
def test_invalid_scenario_enum_rejected(client: TestClient) -> None:
    response = client.get(
        f"/api/v1/analytics/products/{_IDS['p1']}/simulation",
        params={"scenario": "teleport"},
    )
    assert response.status_code == 422
