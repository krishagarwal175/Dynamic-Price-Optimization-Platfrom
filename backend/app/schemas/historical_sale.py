"""HistoricalSale API schemas (independent of the ORM model)."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field

from app.schemas.common import INPUT_CONFIG, ORM_CONFIG, Money


class HistoricalSaleBase(BaseModel):
    product_id: int = Field(gt=0)
    sale_date: date
    quantity: int = Field(ge=0)
    unit_price: Money


class HistoricalSaleCreate(HistoricalSaleBase):
    model_config = INPUT_CONFIG


class HistoricalSaleUpdate(BaseModel):
    model_config = INPUT_CONFIG

    sale_date: date | None = None
    quantity: int | None = Field(default=None, ge=0)
    unit_price: Money | None = None


class HistoricalSaleRead(HistoricalSaleBase):
    model_config = ORM_CONFIG

    id: int
    created_at: datetime
    updated_at: datetime


class HistoricalSaleSummary(BaseModel):
    model_config = ORM_CONFIG

    id: int
    sale_date: date
    quantity: int
    unit_price: Money
