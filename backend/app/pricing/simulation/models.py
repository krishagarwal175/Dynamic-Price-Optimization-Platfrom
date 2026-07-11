"""Immutable value objects for the scenario-simulation engine (framework-free).

Consistent with the previous engines: plain frozen dataclasses, no ORM/DTO/framework
types. Demand propagation and financial math are reused from the optimization engine
(``DemandModel`` / objective functions) — never re-derived here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from app.pricing.optimization.models import Objective

# Re-exported for callers/tests so the simulation objective type is discoverable here.
__all__ = [
    "DeltaSet",
    "Objective",
    "ScenarioDiagnostics",
    "ScenarioResult",
    "ScenarioSpec",
    "ScenarioType",
    "SimulationInput",
    "SimulationResult",
]


class ScenarioType(str, Enum):
    BASELINE = "baseline"  # keep the current price
    RECOMMENDED = "recommended"  # the optimizer's recommended price
    FIXED_PRICE = "fixed_price"  # an arbitrary business-supplied price
    PERCENTAGE_INCREASE = "percentage_increase"  # current price × (1 + pct)
    PERCENTAGE_DECREASE = "percentage_decrease"  # current price × (1 − pct)


@dataclass(frozen=True)
class ScenarioSpec:
    """A hypothetical pricing decision to evaluate."""

    type: ScenarioType
    label: str
    price: float | None = None  # required for FIXED_PRICE
    percentage: float | None = None  # fraction, required for PERCENTAGE_* (e.g. 0.05 = 5%)


@dataclass(frozen=True)
class SimulationInput:
    """Validated inputs for a what-if run — plain business values only."""

    current_price: float
    baseline_demand: float  # expected demand at the current price (from the forecast)
    elasticity: float
    unit_cost: float  # variable/unit cost
    fixed_cost: float
    objective: Objective
    scenarios: tuple[ScenarioSpec, ...]
    recommended_price: float | None = None
    constraint_summary: str | None = None


@dataclass(frozen=True)
class DeltaSet:
    """Absolute and percentage differences of a scenario vs a reference point."""

    demand_abs: float
    demand_pct: float | None
    revenue_abs: float
    revenue_pct: float | None
    gross_profit_abs: float
    gross_profit_pct: float | None
    net_profit_abs: float
    net_profit_pct: float | None
    margin_points: float  # margin difference in percentage points


@dataclass(frozen=True)
class ScenarioDiagnostics:
    """Structured explanation of a scenario's outcome (booleans/numbers + short notes)."""

    price_change_pct: float | None
    demand_change_pct: float | None
    revenue_improved: bool
    profit_improved: bool
    margin_improved: bool
    is_recommended: bool
    notes: tuple[str, ...]


@dataclass(frozen=True)
class ScenarioResult:
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
    vs_baseline: DeltaSet
    vs_recommended: DeltaSet | None
    rank: int  # 1 = best by the chosen objective
    diagnostics: ScenarioDiagnostics


@dataclass(frozen=True)
class SimulationResult:
    objective: Objective
    baseline_label: str
    scenarios: tuple[ScenarioResult, ...]
    ranking_by_objective: tuple[str, ...]
    ranking_by_revenue: tuple[str, ...]
    ranking_by_net_profit: tuple[str, ...]
    best_scenario: str
    notes: tuple[str, ...] = field(default_factory=tuple)
