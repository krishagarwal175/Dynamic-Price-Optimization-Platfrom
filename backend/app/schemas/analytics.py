"""Analytics API schemas (independent of the engine's value objects)."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel

from app.schemas.common import ORM_CONFIG


class FinancialMetricsSchema(BaseModel):
    """Serialized financial metrics. ``None`` fields are metrics that are undefined for the
    given data (e.g. a margin when revenue is zero)."""

    model_config = ORM_CONFIG

    total_units: int
    revenue: Decimal
    gross_revenue: Decimal
    cogs: Decimal
    total_variable_cost: Decimal
    total_fixed_cost: Decimal
    gross_profit: Decimal
    net_profit: Decimal
    contribution_margin: Decimal
    gross_margin: Decimal | None
    contribution_margin_ratio: Decimal | None
    average_selling_price: Decimal | None
    unit_cost: Decimal | None
    profit_per_unit: Decimal | None
    breakeven_units: Decimal | None
    breakeven_revenue: Decimal | None


class DatasetFinancialsResponse(BaseModel):
    scope: str
    metrics: FinancialMetricsSchema


class ProductFinancialsResponse(BaseModel):
    product_id: int
    sku: str
    name: str
    metrics: FinancialMetricsSchema


class CategoryFinancialsResponse(BaseModel):
    category_id: int
    name: str
    metrics: FinancialMetricsSchema
