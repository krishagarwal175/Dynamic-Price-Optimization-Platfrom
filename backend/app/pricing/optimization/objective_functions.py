"""Deterministic objective functions evaluated at a candidate price.

revenue(P)             = P · Q(P)
gross_profit(P)        = (P − variable_cost) · Q(P)
contribution_margin(P) = (P − variable_cost) · Q(P)   (equals gross profit in v1:
                         unit cost is the only variable cost)
net_profit(P)          = gross_profit(P) − fixed_cost
"""

from __future__ import annotations

from collections.abc import Callable

from app.pricing.optimization.models import Objective, PricingContext


def revenue(price: float, ctx: PricingContext) -> float:
    return price * ctx.demand(price)


def gross_profit(price: float, ctx: PricingContext) -> float:
    return ctx.gross_profit(price)


def contribution_margin(price: float, ctx: PricingContext) -> float:
    return ctx.gross_profit(price)


def net_profit(price: float, ctx: PricingContext) -> float:
    return ctx.gross_profit(price) - ctx.fixed_cost


OBJECTIVES: dict[Objective, Callable[[float, PricingContext], float]] = {
    Objective.MAXIMIZE_REVENUE: revenue,
    Objective.MAXIMIZE_GROSS_PROFIT: gross_profit,
    Objective.MAXIMIZE_CONTRIBUTION_MARGIN: contribution_margin,
    Objective.MAXIMIZE_NET_PROFIT: net_profit,
}
