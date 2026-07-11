"""Elasticity API schemas (independent of the engine's value objects)."""

from __future__ import annotations

from pydantic import BaseModel

from app.pricing.elasticity.models import ElasticityClass, ElasticityMethod
from app.schemas.common import ORM_CONFIG


class CurvePointSchema(BaseModel):
    model_config = ORM_CONFIG

    price: float
    value: float


class RegressionDiagnosticsSchema(BaseModel):
    model_config = ORM_CONFIG

    slope: float
    intercept: float
    r_squared: float | None
    residual_std: float
    sample_size: int
    distinct_prices: int
    assumptions: list[str]
    notes: list[str]


class ElasticityAnalysisSchema(BaseModel):
    model_config = ORM_CONFIG

    method: ElasticityMethod
    elasticity_coefficient: float
    classification: ElasticityClass
    arc_elasticity: float | None
    point_elasticity: float | None
    diagnostics: RegressionDiagnosticsSchema
    demand_curve: list[CurvePointSchema]
    revenue_curve: list[CurvePointSchema]
    profit_curve: list[CurvePointSchema] | None


class DatasetElasticityResponse(BaseModel):
    scope: str
    analysis: ElasticityAnalysisSchema


class ProductElasticityResponse(BaseModel):
    product_id: int
    sku: str
    name: str
    analysis: ElasticityAnalysisSchema
