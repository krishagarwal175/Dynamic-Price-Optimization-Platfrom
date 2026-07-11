"""Deterministic price-elasticity analysis engine (pure business logic).

Given (price, quantity) observations, estimates price elasticity of demand and produces
diagnostics and visualization-ready curves. Method selection:

* **≥ 3 observations** with ≥ 2 distinct prices → **log-log regression** (constant
  elasticity): ``ln(Q) = a + b·ln(P)`` with ``b`` the elasticity coefficient.
* **exactly 2 observations** → **arc (midpoint) elasticity**.

Supplementary measures (arc between the extreme price levels, and point elasticity from a
linear fit at the mean) accompany the log-log estimate. Curves are generated from the
constant-elasticity model ``Q(P) = exp(a)·P^b``.

Formulas are documented in ``app/pricing/elasticity/regression.py``,
``mathematics.py``, and ``vault4/07-Features/price-elasticity-engine.md``.
"""

from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Sequence

from app.pricing.elasticity.diagnostics import build_assumptions, build_notes, classify
from app.pricing.elasticity.errors import (
    DegenerateDataError,
    InsufficientObservationsError,
    InvalidObservationError,
)
from app.pricing.elasticity.mathematics import arc_elasticity, linspace, ln, mean
from app.pricing.elasticity.models import (
    CurvePoint,
    ElasticityAnalysis,
    ElasticityMethod,
    Observation,
    RegressionDiagnostics,
)
from app.pricing.elasticity.regression import fit_ols

MIN_ARC_OBSERVATIONS = 2
MIN_REGRESSION_OBSERVATIONS = 3
DEFAULT_CURVE_POINTS = 25

_COEFF_DP = 6
_R2_DP = 4
_PRICE_DP = 2
_QTY_DP = 4
_MONEY_DP = 2


def analyze_elasticity(
    observations: Sequence[Observation],
    *,
    unit_cost: float | None = None,
    curve_points: int = DEFAULT_CURVE_POINTS,
) -> ElasticityAnalysis:
    """Estimate elasticity and build diagnostics + curves. Raises structured domain errors."""
    obs = list(observations)
    if len(obs) < MIN_ARC_OBSERVATIONS:
        raise InsufficientObservationsError(
            f"At least {MIN_ARC_OBSERVATIONS} observations are required to estimate elasticity."
        )
    for observation in obs:
        if observation.price <= 0:
            raise InvalidObservationError("All prices must be strictly positive.")
        if observation.quantity <= 0:
            raise InvalidObservationError("All quantities must be strictly positive.")

    prices = [p.price for p in obs]
    quantities = [p.quantity for p in obs]
    distinct_prices = len({round(p, 10) for p in prices})
    if distinct_prices < 2:
        raise DegenerateDataError(
            "All observations share the same price; price variation is required."
        )

    ln_prices = [ln(p) for p in prices]
    ln_quantities = [ln(q) for q in quantities]
    fit = fit_ols(ln_prices, ln_quantities)  # slope = constant elasticity

    if len(obs) >= MIN_REGRESSION_OBSERVATIONS:
        method = ElasticityMethod.LOG_LOG
        coefficient = fit.slope
        arc = _extreme_arc(prices, quantities)
        point = _point_elasticity(prices, quantities)
    else:
        method = ElasticityMethod.ARC
        coefficient = _extreme_arc(prices, quantities)
        arc = coefficient
        point = None

    diagnostics = RegressionDiagnostics(
        slope=round(fit.slope, _COEFF_DP),
        intercept=round(fit.intercept, _COEFF_DP),
        r_squared=None if fit.r_squared is None else round(fit.r_squared, _R2_DP),
        residual_std=round(fit.residual_std, _COEFF_DP),
        sample_size=len(obs),
        distinct_prices=distinct_prices,
        assumptions=build_assumptions(method),
        notes=build_notes(
            method=method,
            r_squared=fit.r_squared,
            sample_size=len(obs),
            distinct_prices=distinct_prices,
        ),
    )

    demand, revenue, profit = _build_curves(
        slope=fit.slope,
        intercept=fit.intercept,
        prices=prices,
        unit_cost=unit_cost,
        count=curve_points,
    )

    rounded_coefficient = round(coefficient, _COEFF_DP)
    return ElasticityAnalysis(
        method=method,
        elasticity_coefficient=rounded_coefficient,
        # Classify the reported (rounded) value so classification and coefficient agree at
        # boundaries (e.g. |E| = 2.0 exactly → elastic, not tipped over by float noise).
        classification=classify(rounded_coefficient),
        arc_elasticity=None if arc is None else round(arc, _COEFF_DP),
        point_elasticity=None if point is None else round(point, _COEFF_DP),
        diagnostics=diagnostics,
        demand_curve=demand,
        revenue_curve=revenue,
        profit_curve=profit,
    )


def _extreme_arc(prices: Sequence[float], quantities: Sequence[float]) -> float:
    """Arc elasticity between the lowest- and highest-priced groups (mean quantity each)."""
    grouped: dict[float, list[float]] = defaultdict(list)
    for price, quantity in zip(prices, quantities, strict=True):
        grouped[price].append(quantity)
    low = min(grouped)
    high = max(grouped)
    return arc_elasticity(low, mean(grouped[low]), high, mean(grouped[high]))


def _point_elasticity(prices: Sequence[float], quantities: Sequence[float]) -> float | None:
    """Point elasticity at the mean, from a linear demand fit: E = b·(P̄/Q̄)."""
    linear = fit_ols(prices, quantities)
    mean_q = mean(quantities)
    if mean_q == 0:
        return None
    return linear.slope * (mean(prices) / mean_q)


def _build_curves(
    *,
    slope: float,
    intercept: float,
    prices: Sequence[float],
    unit_cost: float | None,
    count: int,
) -> tuple[tuple[CurvePoint, ...], tuple[CurvePoint, ...], tuple[CurvePoint, ...] | None]:
    grid = linspace(min(prices), max(prices), count)
    demand: list[CurvePoint] = []
    revenue: list[CurvePoint] = []
    profit: list[CurvePoint] = []
    for price in grid:
        quantity = math.exp(intercept + slope * ln(price))
        demand.append(CurvePoint(round(price, _PRICE_DP), round(quantity, _QTY_DP)))
        revenue.append(CurvePoint(round(price, _PRICE_DP), round(price * quantity, _MONEY_DP)))
        if unit_cost is not None:
            profit.append(
                CurvePoint(
                    round(price, _PRICE_DP), round((price - unit_cost) * quantity, _MONEY_DP)
                )
            )
    return tuple(demand), tuple(revenue), (tuple(profit) if unit_cost is not None else None)
