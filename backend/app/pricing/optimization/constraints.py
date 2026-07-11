"""Composable optimization constraints.

Each constraint independently contributes price **bounds** (which shrink the search range)
and/or a **feasibility** test (which rejects candidate prices), plus an ``is_active`` check
used to explain which constraints bind at the recommendation.
"""

from __future__ import annotations

from abc import ABC

from app.pricing.optimization.models import OptimizationConstraints, PricingContext

_REL_TOL = 1e-3


def _close(a: float, b: float) -> bool:
    return abs(a - b) <= max(_REL_TOL, _REL_TOL * abs(b))


class Constraint(ABC):
    label: str

    def bounds(self) -> tuple[float | None, float | None]:
        return (None, None)

    def feasible(self, price: float, ctx: PricingContext) -> bool:
        return True

    def is_active(self, price: float, ctx: PricingContext) -> bool:
        return False


class MinPriceConstraint(Constraint):
    def __init__(self, value: float) -> None:
        self.value = value
        self.label = f"min_price>={value}"

    def bounds(self) -> tuple[float | None, float | None]:
        return (self.value, None)

    def is_active(self, price: float, ctx: PricingContext) -> bool:
        return _close(price, self.value)


class MaxPriceConstraint(Constraint):
    def __init__(self, value: float) -> None:
        self.value = value
        self.label = f"max_price<={value}"

    def bounds(self) -> tuple[float | None, float | None]:
        return (None, self.value)

    def is_active(self, price: float, ctx: PricingContext) -> bool:
        return _close(price, self.value)


class MaxIncreaseConstraint(Constraint):
    def __init__(self, current_price: float, pct: float) -> None:
        self.cap = current_price * (1 + pct)
        self.label = f"max_increase<={pct:.0%}"

    def bounds(self) -> tuple[float | None, float | None]:
        return (None, self.cap)

    def is_active(self, price: float, ctx: PricingContext) -> bool:
        return _close(price, self.cap)


class MaxDecreaseConstraint(Constraint):
    def __init__(self, current_price: float, pct: float) -> None:
        self.floor = current_price * (1 - pct)
        self.label = f"max_decrease<={pct:.0%}"

    def bounds(self) -> tuple[float | None, float | None]:
        return (self.floor, None)

    def is_active(self, price: float, ctx: PricingContext) -> bool:
        return _close(price, self.floor)


class MinMarginConstraint(Constraint):
    def __init__(self, pct: float) -> None:
        self.pct = pct
        self.label = f"min_margin>={pct:.0%}"

    def _margin(self, price: float, ctx: PricingContext) -> float:
        return (price - ctx.variable_cost) / price if price > 0 else -1.0

    def feasible(self, price: float, ctx: PricingContext) -> bool:
        return self._margin(price, ctx) >= self.pct

    def is_active(self, price: float, ctx: PricingContext) -> bool:
        return _close(self._margin(price, ctx), self.pct)


class MinProfitConstraint(Constraint):
    def __init__(self, value: float) -> None:
        self.value = value
        self.label = f"min_profit>={value}"

    def feasible(self, price: float, ctx: PricingContext) -> bool:
        return ctx.gross_profit(price) >= self.value

    def is_active(self, price: float, ctx: PricingContext) -> bool:
        return _close(ctx.gross_profit(price), self.value)


class MinDemandConstraint(Constraint):
    def __init__(self, value: float) -> None:
        self.value = value
        self.label = f"min_demand>={value}"

    def feasible(self, price: float, ctx: PricingContext) -> bool:
        return ctx.demand(price) >= self.value

    def is_active(self, price: float, ctx: PricingContext) -> bool:
        return _close(ctx.demand(price), self.value)


def build_constraints(spec: OptimizationConstraints, current_price: float) -> list[Constraint]:
    """Translate the flat constraint spec into a list of composable constraint objects."""
    constraints: list[Constraint] = []
    if spec.min_price is not None:
        constraints.append(MinPriceConstraint(spec.min_price))
    if spec.max_price is not None:
        constraints.append(MaxPriceConstraint(spec.max_price))
    if spec.max_increase_pct is not None:
        constraints.append(MaxIncreaseConstraint(current_price, spec.max_increase_pct))
    if spec.max_decrease_pct is not None:
        constraints.append(MaxDecreaseConstraint(current_price, spec.max_decrease_pct))
    if spec.min_margin_pct is not None:
        constraints.append(MinMarginConstraint(spec.min_margin_pct))
    if spec.min_profit is not None:
        constraints.append(MinProfitConstraint(spec.min_profit))
    if spec.min_demand is not None:
        constraints.append(MinDemandConstraint(spec.min_demand))
    return constraints
