"""Explanation helpers: assumptions and notes that make a recommendation transparent."""

from __future__ import annotations

from app.pricing.optimization.models import Objective

_BOUNDARY_TOL = 1e-6


def build_assumptions(elasticity: float) -> tuple[str, ...]:
    return (
        "Demand follows a constant-elasticity curve Q(P) = Q₀·(P/P₀)^E anchored at the "
        f"current price (E = {elasticity:.4f}).",
        "Elasticity is constant over the evaluated price range.",
        "Unit (variable) cost and fixed cost are constant with respect to price and volume.",
        "One product is optimized in isolation (no cross-product or inventory effects).",
    )


def build_notes(
    *,
    objective: Objective,
    elasticity: float,
    recommended_price: float,
    lower: float,
    upper: float,
    active_constraints: tuple[str, ...],
    improvement: float,
) -> tuple[str, ...]:
    notes: list[str] = []

    at_lower = abs(recommended_price - lower) <= _BOUNDARY_TOL
    at_upper = abs(recommended_price - upper) <= _BOUNDARY_TOL
    if at_lower or at_upper:
        edge = "lower" if at_lower else "upper"
        notes.append(
            f"Recommendation sits at the {edge} bound of the search range; the unconstrained "
            "optimum may lie beyond the allowed prices."
        )

    if elasticity >= 0:
        notes.append("Estimated elasticity is non-negative (atypical); interpret with care.")
    elif abs(elasticity) < 1 and objective is Objective.MAXIMIZE_REVENUE:
        notes.append(
            "Demand is inelastic (|E| < 1): revenue rises with price, so the optimizer pushes "
            "toward the maximum allowed price."
        )

    if active_constraints:
        notes.append(
            "Binding constraints at the recommendation: " + ", ".join(active_constraints) + "."
        )
    else:
        notes.append("No constraints are binding; the recommendation is an interior optimum.")

    if improvement <= 0:
        notes.append("The current price is already at or above the optimum for this objective.")

    return tuple(notes)
