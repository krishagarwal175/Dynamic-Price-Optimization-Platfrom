"""Optimization API schemas (independent of the engine's value objects)."""

from __future__ import annotations

from pydantic import BaseModel

from app.pricing.optimization.models import Objective
from app.schemas.common import ORM_CONFIG


class OptimizationResultSchema(BaseModel):
    model_config = ORM_CONFIG

    objective: Objective
    recommended_price: float
    expected_demand: float
    expected_revenue: float
    expected_gross_profit: float
    expected_net_profit: float
    objective_value: float
    baseline_price: float
    baseline_objective_value: float
    improvement: float
    search_lower: float
    search_upper: float
    iterations: int
    active_constraints: list[str]
    assumptions: list[str]
    notes: list[str]


class DatasetOptimizationResponse(BaseModel):
    scope: str
    optimization: OptimizationResultSchema


class ProductOptimizationResponse(BaseModel):
    product_id: int
    sku: str
    name: str
    optimization: OptimizationResultSchema
