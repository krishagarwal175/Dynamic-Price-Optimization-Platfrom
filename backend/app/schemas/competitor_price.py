"""CompetitorPrice API schemas (independent of the ORM model)."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field

from app.schemas.common import INPUT_CONFIG, ORM_CONFIG, CurrencyCode, Money


class CompetitorPriceBase(BaseModel):
    product_id: int = Field(gt=0)
    competitor_id: int = Field(gt=0)
    price: Money
    currency: CurrencyCode = "USD"
    observed_at: date


class CompetitorPriceCreate(CompetitorPriceBase):
    model_config = INPUT_CONFIG


class CompetitorPriceRead(CompetitorPriceBase):
    model_config = ORM_CONFIG

    id: int
    created_at: datetime
    updated_at: datetime


class CompetitorPriceSummary(BaseModel):
    model_config = ORM_CONFIG

    id: int
    competitor_id: int
    price: Money
    observed_at: date
