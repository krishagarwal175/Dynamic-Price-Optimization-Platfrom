"""Simulation API schemas (independent of the engine's value objects)."""

from __future__ import annotations

from pydantic import BaseModel

from app.pricing.optimization.models import Objective
from app.pricing.simulation.models import ScenarioType
from app.schemas.common import ORM_CONFIG


class DeltaSetSchema(BaseModel):
    model_config = ORM_CONFIG

    demand_abs: float
    demand_pct: float | None
    revenue_abs: float
    revenue_pct: float | None
    gross_profit_abs: float
    gross_profit_pct: float | None
    net_profit_abs: float
    net_profit_pct: float | None
    margin_points: float


class ScenarioDiagnosticsSchema(BaseModel):
    model_config = ORM_CONFIG

    price_change_pct: float | None
    demand_change_pct: float | None
    revenue_improved: bool
    profit_improved: bool
    margin_improved: bool
    is_recommended: bool
    notes: list[str]


class ScenarioResultSchema(BaseModel):
    model_config = ORM_CONFIG

    label: str
    scenario_type: ScenarioType
    price: float
    demand: float
    revenue: float
    gross_profit: float
    contribution_margin: float
    net_profit: float
    margin_pct: float
    objective_value: float
    vs_baseline: DeltaSetSchema
    vs_recommended: DeltaSetSchema | None
    rank: int
    diagnostics: ScenarioDiagnosticsSchema


class SimulationResultSchema(BaseModel):
    model_config = ORM_CONFIG

    objective: Objective
    baseline_label: str
    scenarios: list[ScenarioResultSchema]
    ranking_by_objective: list[str]
    ranking_by_revenue: list[str]
    ranking_by_net_profit: list[str]
    best_scenario: str
    notes: list[str]


class DatasetSimulationResponse(BaseModel):
    scope: str
    simulation: SimulationResultSchema


class ProductSimulationResponse(BaseModel):
    product_id: int
    sku: str
    name: str
    simulation: SimulationResultSchema
