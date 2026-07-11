"""Value objects for the pricing-optimization engine (framework-free).

Demand is modelled with the constant-elasticity form consistent with the elasticity engine:

    Q(P) = Q₀ · (P / P₀)^E

where P₀ is the reference (current) price, Q₀ the reference demand, and E the elasticity.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Objective(str, Enum):
    MAXIMIZE_REVENUE = "maximize_revenue"
    MAXIMIZE_GROSS_PROFIT = "maximize_gross_profit"
    MAXIMIZE_CONTRIBUTION_MARGIN = "maximize_contribution_margin"
    MAXIMIZE_NET_PROFIT = "maximize_net_profit"


@dataclass(frozen=True)
class OptimizationConstraints:
    """Optional, independently composable business constraints (all default to unset)."""

    min_price: float | None = None
    max_price: float | None = None
    min_margin_pct: float | None = None  # fraction in [0, 1)
    min_profit: float | None = None
    min_demand: float | None = None
    max_increase_pct: float | None = None  # fraction, e.g. 0.2 = +20% vs current price
    max_decrease_pct: float | None = None  # fraction, e.g. 0.2 = −20% vs current price


@dataclass(frozen=True)
class OptimizationInput:
    """Everything the optimizer needs — plain business values only (no ORM/DTOs)."""

    current_price: float
    variable_cost: float
    reference_demand: float  # expected demand at the current price (from forecast/history)
    elasticity: float
    fixed_cost: float = 0.0
    objective: Objective = Objective.MAXIMIZE_GROSS_PROFIT
    constraints: OptimizationConstraints = field(default_factory=OptimizationConstraints)


@dataclass(frozen=True)
class DemandModel:
    reference_price: float
    reference_demand: float
    elasticity: float

    def demand(self, price: float) -> float:
        # float(...) pins the type: ``float ** float`` is typed as Any in typeshed.
        return float(self.reference_demand * (price / self.reference_price) ** self.elasticity)


@dataclass(frozen=True)
class PricingContext:
    """Bundle passed to objective functions and constraints (read-only)."""

    demand_model: DemandModel
    variable_cost: float
    fixed_cost: float

    @property
    def current_price(self) -> float:
        return self.demand_model.reference_price

    def demand(self, price: float) -> float:
        return self.demand_model.demand(price)

    def gross_profit(self, price: float) -> float:
        return (price - self.variable_cost) * self.demand(price)


@dataclass(frozen=True)
class OptimizationResult:
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
    active_constraints: tuple[str, ...]
    assumptions: tuple[str, ...]
    notes: tuple[str, ...]
