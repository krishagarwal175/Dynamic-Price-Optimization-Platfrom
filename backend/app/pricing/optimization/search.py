"""Deterministic numerical search: bounded grid search with iterative refinement.

**Why this algorithm (v1 trade-offs).** A bounded grid search is fully transparent and
robust to non-smooth feasible regions created by arbitrary composable constraints — every
candidate price is evaluated explicitly, so the recommendation is trivially explainable and
deterministic. Its weakness (coarse resolution) is removed by **iterative refinement**:
after the best grid point is found, the search re-grids a narrow window around it and
repeats. This keeps the method simple and gradient-free while reaching fine precision.
Golden-section search would be faster but assumes a unimodal objective — not guaranteed
once constraints carve up the range — so it is intentionally avoided in v1.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from app.pricing.optimization.errors import InfeasibleConstraintsError

DEFAULT_GRID_POINTS = 101
DEFAULT_REFINEMENTS = 3


@dataclass(frozen=True)
class SearchResult:
    best_price: float
    best_value: float
    iterations: int
    evaluated_lower: float
    evaluated_upper: float


def _linspace(start: float, stop: float, count: int) -> list[float]:
    if count <= 1 or stop <= start:
        return [start]
    step = (stop - start) / (count - 1)
    return [start + step * i for i in range(count)]


def maximize(
    objective: Callable[[float], float],
    feasible: Callable[[float], bool],
    lower: float,
    upper: float,
    *,
    grid_points: int = DEFAULT_GRID_POINTS,
    refinements: int = DEFAULT_REFINEMENTS,
) -> SearchResult:
    """Maximize ``objective`` over feasible prices in ``[lower, upper]``.

    Raises :class:`InfeasibleConstraintsError` if no candidate is feasible.
    """
    window_lower, window_upper = lower, upper
    best_price: float | None = None
    best_value = float("-inf")
    iterations = 0

    for _ in range(refinements + 1):
        grid = _linspace(window_lower, window_upper, grid_points)
        for price in grid:
            iterations += 1
            if not feasible(price):
                continue
            value = objective(price)
            if value > best_value:
                best_value = value
                best_price = price
        if best_price is None:
            raise InfeasibleConstraintsError(
                "No price in the allowed range satisfies all constraints."
            )
        # Refine: re-grid a window of ±one coarse step around the incumbent.
        step = (window_upper - window_lower) / (grid_points - 1) if grid_points > 1 else 0.0
        window_lower = max(lower, best_price - step)
        window_upper = min(upper, best_price + step)

    assert best_price is not None  # guaranteed by the loop above
    return SearchResult(
        best_price=best_price,
        best_value=best_value,
        iterations=iterations,
        evaluated_lower=lower,
        evaluated_upper=upper,
    )
