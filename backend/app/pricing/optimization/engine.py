"""Deterministic pricing-optimization engine (pure business logic).

Given a plain :class:`OptimizationInput` (current price, costs, a constant-elasticity demand
model anchored to a forecast/baseline demand, an objective, and optional constraints), it
recommends the price that maximizes the chosen objective within the feasible range, and
explains the recommendation.

Mathematical formulation. With demand ``Q(P) = Q₀·(P/P₀)^E`` and variable cost ``c``:

    revenue(P)      = P · Q(P)
    gross_profit(P) = (P − c) · Q(P)          contribution_margin(P) = gross_profit(P)
    net_profit(P)   = gross_profit(P) − F

The optimizer maximizes the selected objective over ``[lower, upper]`` (a ±band around the
current price, tightened by any price constraints) subject to the feasibility constraints,
using the bounded grid search with refinement in ``search.py``.

For gross/net profit under elastic demand this reproduces the classic monopoly optimum
``P* = c · E / (E + 1)`` (E < −1); for revenue under constant elasticity the objective is
monotonic, so the optimum lies at a boundary — both are covered by the numerical search.
"""

from __future__ import annotations

from app.pricing.optimization.constraints import Constraint, build_constraints
from app.pricing.optimization.diagnostics import build_assumptions, build_notes
from app.pricing.optimization.errors import InfeasibleConstraintsError
from app.pricing.optimization.models import (
    DemandModel,
    OptimizationInput,
    OptimizationResult,
    PricingContext,
)
from app.pricing.optimization.objective_functions import OBJECTIVES, net_profit, revenue
from app.pricing.optimization.search import maximize
from app.pricing.optimization.validation import validate

DEFAULT_LOWER_FACTOR = 0.5  # search from 50% of the current price ...
DEFAULT_UPPER_FACTOR = 2.0  # ... up to 200% of it, unless constraints tighten this
_MIN_PRICE = 1e-6
_DP_PRICE = 2
_DP_MONEY = 2
_DP_QTY = 4
_DP_OBJ = 4


def optimize(inp: OptimizationInput) -> OptimizationResult:
    """Recommend an optimal price. Raises structured domain errors on bad/infeasible input."""
    validate(inp)

    demand_model = DemandModel(
        reference_price=inp.current_price,
        reference_demand=inp.reference_demand,
        elasticity=inp.elasticity,
    )
    ctx = PricingContext(
        demand_model=demand_model,
        variable_cost=inp.variable_cost,
        fixed_cost=inp.fixed_cost,
    )
    constraints = build_constraints(inp.constraints, inp.current_price)
    lower, upper = _search_bounds(inp.current_price, constraints)

    objective_fn = OBJECTIVES[inp.objective]

    def objective(price: float) -> float:
        return objective_fn(price, ctx)

    def feasible(price: float) -> bool:
        return all(constraint.feasible(price, ctx) for constraint in constraints)

    result = maximize(objective, feasible, lower, upper)

    price = result.best_price
    baseline_value = objective(inp.current_price)
    improvement = result.best_value - baseline_value
    active = tuple(c.label for c in constraints if c.is_active(price, ctx))

    return OptimizationResult(
        objective=inp.objective,
        recommended_price=round(price, _DP_PRICE),
        expected_demand=round(ctx.demand(price), _DP_QTY),
        expected_revenue=round(revenue(price, ctx), _DP_MONEY),
        expected_gross_profit=round(ctx.gross_profit(price), _DP_MONEY),
        expected_net_profit=round(net_profit(price, ctx), _DP_MONEY),
        objective_value=round(result.best_value, _DP_OBJ),
        baseline_price=round(inp.current_price, _DP_PRICE),
        baseline_objective_value=round(baseline_value, _DP_OBJ),
        improvement=round(improvement, _DP_OBJ),
        search_lower=round(lower, _DP_PRICE),
        search_upper=round(upper, _DP_PRICE),
        iterations=result.iterations,
        active_constraints=active,
        assumptions=build_assumptions(inp.elasticity),
        notes=build_notes(
            objective=inp.objective,
            elasticity=inp.elasticity,
            recommended_price=price,
            lower=lower,
            upper=upper,
            active_constraints=active,
            improvement=improvement,
        ),
    )


def _search_bounds(current_price: float, constraints: list[Constraint]) -> tuple[float, float]:
    """Default ±band around the current price, tightened by any price-bound constraints."""
    lower = current_price * DEFAULT_LOWER_FACTOR
    upper = current_price * DEFAULT_UPPER_FACTOR
    for constraint in constraints:
        c_lower, c_upper = constraint.bounds()
        if c_lower is not None:
            lower = max(lower, c_lower)
        if c_upper is not None:
            upper = min(upper, c_upper)
    lower = max(lower, _MIN_PRICE)
    if lower > upper:
        raise InfeasibleConstraintsError(
            "Price constraints leave no valid search range (lower bound exceeds upper bound)."
        )
    return lower, upper
