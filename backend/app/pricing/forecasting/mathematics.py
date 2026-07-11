"""Mathematical utilities and error metrics for forecasting (pure, stdlib only).

Error metrics compare aligned actual/predicted sequences:

    MAE  = mean(|actualᵢ − predᵢ|)
    RMSE = sqrt(mean((actualᵢ − predᵢ)²))
    MAPE = mean(|actualᵢ − predᵢ| / |actualᵢ|) × 100     (over actualᵢ ≠ 0)
"""

from __future__ import annotations

import math
from collections.abc import Sequence


def mean(values: Sequence[float]) -> float:
    return sum(values) / len(values)


def population_std(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    mu = mean(values)
    return math.sqrt(sum((v - mu) ** 2 for v in values) / len(values))


def weighted_mean(values: Sequence[float], weights: Sequence[float]) -> float:
    total_weight = sum(weights)
    return sum(v * w for v, w in zip(values, weights, strict=True)) / total_weight


def mae(actual: Sequence[float], predicted: Sequence[float]) -> float:
    diffs = [abs(a - p) for a, p in zip(actual, predicted, strict=True)]
    return mean(diffs)


def rmse(actual: Sequence[float], predicted: Sequence[float]) -> float:
    squared = [(a - p) ** 2 for a, p in zip(actual, predicted, strict=True)]
    return math.sqrt(mean(squared))


def mape(actual: Sequence[float], predicted: Sequence[float]) -> float | None:
    """Mean absolute percentage error over non-zero actuals; ``None`` if all are zero."""
    ratios = [abs(a - p) / abs(a) for a, p in zip(actual, predicted, strict=True) if a != 0]
    if not ratios:
        return None
    return mean(ratios) * 100.0
