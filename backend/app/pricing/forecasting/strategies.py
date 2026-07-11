"""Forecasting strategies (Strategy Pattern).

Each strategy implements :meth:`predict_next` — the one-step-ahead forecast from a history.
The base class derives the (flat) multi-step forecast and the one-step-ahead backtest from
it, so a new technique is added by subclassing without touching existing code.

Formulas (history hₜ = series[:t], most recent value hₜ[-1]):

* **Naive**:                    ŷ = hₜ[-1]
* **Moving Average (w)**:       ŷ = mean(hₜ[-w:])
* **Weighted Moving Average**:  ŷ = Σ wᵢ·hₜ[-w:]ᵢ / Σ wᵢ  (weights 1..w, recent-heaviest)
* **Simple Exp. Smoothing (α)**: ℓₜ = α·yₜ + (1−α)·ℓₜ₋₁ ; ŷ = ℓₗₐₛₜ
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from app.pricing.forecasting.mathematics import mean, weighted_mean
from app.pricing.forecasting.models import ForecastMethod

DEFAULT_WINDOW = 3
DEFAULT_ALPHA = 0.3


class ForecastStrategy(ABC):
    """Base strategy. Subclasses only implement :meth:`predict_next`."""

    method: ForecastMethod
    min_observations: int

    @abstractmethod
    def predict_next(self, history: Sequence[float]) -> float:
        """One-step-ahead forecast given all prior observations."""

    def forecast(self, series: Sequence[float], horizon: int) -> list[float]:
        """Flat multi-step forecast: the next-step level repeated ``horizon`` times."""
        level = self.predict_next(series)
        return [level] * horizon

    def backtest(self, series: Sequence[float]) -> tuple[list[float], list[float]]:
        """One-step-ahead in-sample (actual, predicted) pairs where predictions exist."""
        actuals: list[float] = []
        predictions: list[float] = []
        for t in range(self.min_observations, len(series)):
            predictions.append(self.predict_next(series[:t]))
            actuals.append(series[t])
        return actuals, predictions


class NaiveStrategy(ForecastStrategy):
    method = ForecastMethod.NAIVE
    min_observations = 1

    def predict_next(self, history: Sequence[float]) -> float:
        return history[-1]


class MovingAverageStrategy(ForecastStrategy):
    method = ForecastMethod.MOVING_AVERAGE

    def __init__(self, window: int = DEFAULT_WINDOW) -> None:
        self.window = window
        self.min_observations = window

    def predict_next(self, history: Sequence[float]) -> float:
        return mean(history[-self.window :])


class WeightedMovingAverageStrategy(ForecastStrategy):
    method = ForecastMethod.WEIGHTED_MOVING_AVERAGE

    def __init__(self, window: int = DEFAULT_WINDOW) -> None:
        self.window = window
        self.min_observations = window
        self._weights = [float(i) for i in range(1, window + 1)]  # recent-heaviest

    def predict_next(self, history: Sequence[float]) -> float:
        window = history[-self.window :]
        return weighted_mean(window, self._weights)


class SimpleExponentialSmoothingStrategy(ForecastStrategy):
    method = ForecastMethod.SIMPLE_EXPONENTIAL_SMOOTHING
    min_observations = 2

    def __init__(self, alpha: float = DEFAULT_ALPHA) -> None:
        self.alpha = alpha

    def predict_next(self, history: Sequence[float]) -> float:
        level = history[0]
        for value in history[1:]:
            level = self.alpha * value + (1 - self.alpha) * level
        return level


def build_strategies(
    window: int = DEFAULT_WINDOW, alpha: float = DEFAULT_ALPHA
) -> list[ForecastStrategy]:
    """The registry of available strategies (order = tie-break preference: simpler first)."""
    return [
        NaiveStrategy(),
        MovingAverageStrategy(window),
        WeightedMovingAverageStrategy(window),
        SimpleExponentialSmoothingStrategy(alpha),
    ]
