"""End-to-end API tests for the read-only catalog endpoints."""

from __future__ import annotations

from collections.abc import Iterator
from decimal import Decimal
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import app.models  # noqa: F401
from app.core.config import AppEnv, Settings
from app.core.database import Base, transaction
from app.main import create_app
from app.models.category import Category
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
        bev = Category(name="Beverages")
        snacks = Category(name="Snacks")
        session.add_all([bev, snacks])
        session.flush()
        cola = Product(
            category_id=bev.id,
            sku="COLA-1",
            name="Cola",
            unit_cost=Decimal("1.00"),
            base_price=Decimal("2.50"),
        )
        chips = Product(
            category_id=snacks.id,
            sku="CHIP-1",
            name="Chips",
            unit_cost=Decimal("0.80"),
            base_price=Decimal("1.90"),
        )
        session.add_all([cola, chips])
        session.flush()
        _IDS.update({"cola": cola.id, "bev": bev.id})
    session.close()
    with TestClient(application) as c:
        yield c


@pytest.mark.integration
def test_list_products(client: TestClient) -> None:
    response = client.get("/api/v1/products")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total"] == 2
    assert {p["sku"] for p in data["items"]} == {"COLA-1", "CHIP-1"}


@pytest.mark.integration
def test_search_products(client: TestClient) -> None:
    response = client.get("/api/v1/products", params={"search": "cola"})
    data = response.json()["data"]
    assert data["total"] == 1
    assert data["items"][0]["sku"] == "COLA-1"


@pytest.mark.integration
def test_filter_by_category(client: TestClient) -> None:
    response = client.get("/api/v1/products", params={"category_id": _IDS["bev"]})
    data = response.json()["data"]
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Cola"


@pytest.mark.integration
def test_pagination(client: TestClient) -> None:
    response = client.get("/api/v1/products", params={"limit": 1, "offset": 0})
    data = response.json()["data"]
    assert len(data["items"]) == 1
    assert data["total"] == 2
    assert data["limit"] == 1


@pytest.mark.integration
def test_get_product(client: TestClient) -> None:
    response = client.get(f"/api/v1/products/{_IDS['cola']}")
    assert response.status_code == 200
    assert response.json()["data"]["sku"] == "COLA-1"


@pytest.mark.integration
def test_get_missing_product_404(client: TestClient) -> None:
    response = client.get("/api/v1/products/9999")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


@pytest.mark.integration
def test_list_categories(client: TestClient) -> None:
    response = client.get("/api/v1/categories")
    data = response.json()["data"]
    assert data["total"] == 2
    assert {c["name"] for c in data["items"]} == {"Beverages", "Snacks"}
