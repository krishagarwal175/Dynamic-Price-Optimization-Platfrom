"""Ordinary least-squares simple linear regression (pure Python).

Fits ``y = intercept + slope·x`` via the closed-form normal equations:

    slope     = (n·Σxy − Σx·Σy) / (n·Σxx − (Σx)²)
    intercept = (Σy − slope·Σx) / n
    R²        = 1 − SS_res / SS_tot
    SS_res    = Σ(y − ŷ)² ,  SS_tot = Σ(y − ȳ)²

Used with x = ln(price), y = ln(quantity) to estimate constant elasticity (slope = E).
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from app.pricing.elasticity.errors import SingularRegressionError


@dataclass(frozen=True)
class LinearFit:
    slope: float
    intercept: float
    r_squared: float | None  # None when the response has zero variance (undefined)
    residual_std: float
    n: int


def fit_ols(xs: Sequence[float], ys: Sequence[float]) -> LinearFit:
    """Fit an OLS line. Raises :class:`SingularRegressionError` if ``x`` has no variance."""
    n = len(xs)
    sum_x = sum(xs)
    sum_y = sum(ys)
    sum_xx = sum(x * x for x in xs)
    sum_xy = sum(x * y for x, y in zip(xs, ys, strict=True))

    denominator = n * sum_xx - sum_x * sum_x
    if denominator == 0:
        raise SingularRegressionError("Predictor has zero variance; cannot fit a regression.")

    slope = (n * sum_xy - sum_x * sum_y) / denominator
    intercept = (sum_y - slope * sum_x) / n

    predicted = [intercept + slope * x for x in xs]
    ss_res = sum((y - yhat) ** 2 for y, yhat in zip(ys, predicted, strict=True))
    mean_y = sum_y / n
    ss_tot = sum((y - mean_y) ** 2 for y in ys)

    r_squared = None if ss_tot == 0 else 1.0 - ss_res / ss_tot
    residual_std = math.sqrt(ss_res / (n - 2)) if n > 2 else 0.0

    return LinearFit(
        slope=slope,
        intercept=intercept,
        r_squared=r_squared,
        residual_std=residual_std,
        n=n,
    )
