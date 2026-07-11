"""Input validation for the optimization engine — structured domain errors only."""

from __future__ import annotations

from app.pricing.optimization.errors import InvalidInputError
from app.pricing.optimization.models import OptimizationConstraints, OptimizationInput


def validate(inp: OptimizationInput) -> None:
    if inp.current_price <= 0:
        raise InvalidInputError("Current price must be positive.")
    if inp.variable_cost < 0:
        raise InvalidInputError("Variable cost must not be negative.")
    if inp.fixed_cost < 0:
        raise InvalidInputError("Fixed cost must not be negative.")
    if inp.reference_demand <= 0:
        raise InvalidInputError("Reference demand must be positive (a forecast is required).")
    _validate_constraints(inp.constraints, inp.current_price)


def _validate_constraints(spec: OptimizationConstraints, current_price: float) -> None:
    if spec.min_price is not None and spec.min_price <= 0:
        raise InvalidInputError("min_price must be positive.")
    if spec.max_price is not None and spec.max_price <= 0:
        raise InvalidInputError("max_price must be positive.")
    if (
        spec.min_price is not None
        and spec.max_price is not None
        and spec.min_price > spec.max_price
    ):
        raise InvalidInputError("Impossible constraints: min_price exceeds max_price.")
    if spec.min_margin_pct is not None and not (0.0 <= spec.min_margin_pct < 1.0):
        raise InvalidInputError("min_margin_pct must be in [0, 1).")
    if spec.min_demand is not None and spec.min_demand < 0:
        raise InvalidInputError("min_demand must not be negative.")
    if spec.max_increase_pct is not None and spec.max_increase_pct < 0:
        raise InvalidInputError("max_increase_pct must not be negative.")
    if spec.max_decrease_pct is not None and not (0.0 <= spec.max_decrease_pct <= 1.0):
        raise InvalidInputError("max_decrease_pct must be in [0, 1].")
