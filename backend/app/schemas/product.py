"""Product API schemas (independent of the ORM model)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import INPUT_CONFIG, ORM_CONFIG, CurrencyCode, Money


class ProductBase(BaseModel):
    category_id: int = Field(gt=0)
    sku: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    unit_cost: Money
    base_price: Money
    currency: CurrencyCode = "USD"
    is_active: bool = True


class ProductCreate(ProductBase):
    model_config = INPUT_CONFIG


class ProductUpdate(BaseModel):
    model_config = INPUT_CONFIG

    category_id: int | None = Field(default=None, gt=0)
    sku: str | None = Field(default=None, min_length=1, max_length=64)
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    unit_cost: Money | None = None
    base_price: Money | None = None
    currency: CurrencyCode | None = None
    is_active: bool | None = None


class ProductRead(ProductBase):
    model_config = ORM_CONFIG

    id: int
    created_at: datetime
    updated_at: datetime


class ProductSummary(BaseModel):
    model_config = ORM_CONFIG

    id: int
    sku: str
    name: str
    base_price: Money
