"""Low-level, pure math helpers for elasticity analysis.

Deliberately dependency-free (standard-library ``math`` only) so the statistics are
transparent, deterministic, and hand-verifiable.
"""

from __future__ import annotations

import math
from collections.abc import Sequence


def mean(values: Sequence[float]) -> float:
    return sum(values) / len(values)


def ln(value: float) -> float:
    """Natural log; the caller guarantees ``value > 0`` (validated upstream)."""
    return math.log(value)


def linspace(start: float, stop: float, count: int) -> list[float]:
    """``count`` evenly spaced values from ``start`` to ``stop`` inclusive."""
    if count <= 1:
        return [start]
    step = (stop - start) / (count - 1)
    return [start + step * i for i in range(count)]


def arc_elasticity(price_low: float, qty_low: float, price_high: float, qty_high: float) -> float:
    """Midpoint (arc) elasticity between two points.

        E = (ΔQ / avg(Q)) / (ΔP / avg(P))

    where ΔQ = qty_high − qty_low, ΔP = price_high − price_low, and the averages are the
    midpoints. Requires the two prices to differ.
    """
    avg_q = (qty_low + qty_high) / 2
    avg_p = (price_low + price_high) / 2
    pct_q = (qty_high - qty_low) / avg_q
    pct_p = (price_high - price_low) / avg_p
    return pct_q / pct_p
