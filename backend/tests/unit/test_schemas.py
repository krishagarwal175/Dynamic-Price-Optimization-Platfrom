"""Unit tests for Pydantic API schemas (strict validation, ORM independence)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.schemas.category import CategoryCreate
from app.schemas.historical_sale import HistoricalSaleCreate
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate


@pytest.mark.unit
def test_product_create_valid() -> None:
    model = ProductCreate(
        category_id=1,
        sku="SKU-1",
        name="Widget",
        unit_cost=Decimal("2.00"),
        base_price=Decimal("5.00"),
    )
    assert model.currency == "USD"
    assert model.is_active is True


@pytest.mark.unit
def test_product_create_rejects_negative_money() -> None:
    with pytest.raises(ValidationError):
        ProductCreate(
            category_id=1,
            sku="S",
            name="W",
            unit_cost=Decimal("2.00"),
            base_price=Decimal("-5.00"),
        )


@pytest.mark.unit
def test_input_schema_forbids_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        CategoryCreate(name="X", bogus="nope")  # type: ignore[call-arg]


@pytest.mark.unit
def test_currency_must_be_three_chars() -> None:
    with pytest.raises(ValidationError):
        ProductCreate(
            category_id=1,
            sku="S",
            name="W",
            unit_cost=Decimal("1.00"),
            base_price=Decimal("2.00"),
            currency="US",
        )


@pytest.mark.unit
def test_update_schema_is_fully_optional() -> None:
    model = ProductUpdate(name="Renamed")
    assert model.name == "Renamed"
    assert model.base_price is None


@pytest.mark.unit
def test_historical_sale_rejects_negative_quantity() -> None:
    with pytest.raises(ValidationError):
        HistoricalSaleCreate(
            product_id=1,
            sale_date="2026-01-01",  # type: ignore[arg-type]
            quantity=-1,
            unit_price=Decimal("2.00"),
        )


@pytest.mark.unit
def test_read_schema_maps_from_orm_like_object() -> None:
    now = datetime(2026, 1, 1)
    orm_like = SimpleNamespace(
        id=7,
        category_id=1,
        sku="SKU-7",
        name="Widget",
        description=None,
        unit_cost=Decimal("2.00"),
        base_price=Decimal("5.00"),
        currency="USD",
        is_active=True,
        created_at=now,
        updated_at=now,
    )
    read = ProductRead.model_validate(orm_like)
    assert read.id == 7
    assert read.sku == "SKU-7"
