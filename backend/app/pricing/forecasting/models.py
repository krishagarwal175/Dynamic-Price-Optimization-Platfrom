"""Value objects for the forecasting engine (framework-free)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum


class ForecastMethod(str, Enum):
    NAIVE = "naive"
    MOVING_AVERAGE = "moving_average"
    WEIGHTED_MOVING_AVERAGE = "weighted_moving_average"
    SIMPLE_EXPONENTIAL_SMOOTHING = "simple_exponential_smoothing"


@dataclass(frozen=True)
class Observation:
    """One demand observation for a period (duplicate periods are aggregated)."""

    period: date
    demand: float


@dataclass(frozen=True)
class HistoricalPoint:
    period: date
    demand: float


@dataclass(frozen=True)
class ForecastPoint:
    """A single forecast step with a simple statistical prediction interval."""

    step: int  # 1-based steps ahead
    predicted: float
    lower: float
    upper: float


@dataclass(frozen=True)
class ResidualSummary:
    count: int
    mean: float
    std: float
    minimum: float
    maximum: float


@dataclass(frozen=True)
class StrategyEvaluation:
    """Backtest performance of one candidate strategy."""

    method: ForecastMethod
    usable: bool  # had enough data to be evaluated / selected
    mae: float | None
    mape: float | None
    rmse: float | None


@dataclass(frozen=True)
class ForecastDiagnostics:
    selected_strategy: ForecastMethod
    mae: float
    mape: float | None
    rmse: float
    mean_error: float
    residuals: ResidualSummary
    sample_size: int
    distinct_periods: int
    assumptions: tuple[str, ...]
    notes: tuple[str, ...]


@dataclass(frozen=True)
class ForecastResult:
    horizon: int
    selected_strategy: ForecastMethod
    forecast: tuple[ForecastPoint, ...]
    history: tuple[HistoricalPoint, ...]
    diagnostics: ForecastDiagnostics
    alternatives: tuple[StrategyEvaluation, ...]
