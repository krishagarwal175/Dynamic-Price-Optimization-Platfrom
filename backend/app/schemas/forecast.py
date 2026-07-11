"""Forecast API schemas (independent of the engine's value objects)."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel

from app.pricing.forecasting.models import ForecastMethod
from app.schemas.common import ORM_CONFIG


class HistoricalPointSchema(BaseModel):
    model_config = ORM_CONFIG

    period: date
    demand: float


class ForecastPointSchema(BaseModel):
    model_config = ORM_CONFIG

    step: int
    predicted: float
    lower: float
    upper: float


class ResidualSummarySchema(BaseModel):
    model_config = ORM_CONFIG

    count: int
    mean: float
    std: float
    minimum: float
    maximum: float


class StrategyEvaluationSchema(BaseModel):
    model_config = ORM_CONFIG

    method: ForecastMethod
    usable: bool
    mae: float | None
    mape: float | None
    rmse: float | None


class ForecastDiagnosticsSchema(BaseModel):
    model_config = ORM_CONFIG

    selected_strategy: ForecastMethod
    mae: float
    mape: float | None
    rmse: float
    mean_error: float
    residuals: ResidualSummarySchema
    sample_size: int
    distinct_periods: int
    assumptions: list[str]
    notes: list[str]


class ForecastResultSchema(BaseModel):
    model_config = ORM_CONFIG

    horizon: int
    selected_strategy: ForecastMethod
    forecast: list[ForecastPointSchema]
    history: list[HistoricalPointSchema]
    diagnostics: ForecastDiagnosticsSchema
    alternatives: list[StrategyEvaluationSchema]


class DatasetForecastResponse(BaseModel):
    scope: str
    forecast: ForecastResultSchema


class ProductForecastResponse(BaseModel):
    product_id: int
    sku: str
    name: str
    forecast: ForecastResultSchema
