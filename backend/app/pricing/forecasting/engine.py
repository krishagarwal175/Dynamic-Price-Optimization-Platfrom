"""Deterministic demand-forecasting engine (pure business logic).

Pipeline: validate/normalize → backtest every applicable strategy (one-step-ahead in
sample) → select the lowest-RMSE strategy → produce a flat forecast with simple normal
prediction intervals and full diagnostics.

**Model selection.** Each strategy usable on the series (``len ≥ min_observations + 1`` so
at least one holdout exists) is backtested; the one with the smallest RMSE is chosen. Ties
break toward the simpler strategy (registry order). If only the naive strategy is
evaluable, it is used (graceful fallback).

**Prediction intervals.** Using the selected model's in-sample residual standard deviation
``σ``, the step-``h`` interval is ``ŷ ± z·σ·√h`` with ``z = 1.96`` (≈95%), lower-bounded at
0 (demand is non-negative). This widens with the horizon and is a simple normal
approximation, not a guarantee.
"""

from __future__ import annotations

import math

from app.pricing.forecasting.diagnostics import (
    build_assumptions,
    build_notes,
    residual_summary,
)
from app.pricing.forecasting.errors import (
    InsufficientObservationsError,
    InvalidHorizonError,
)
from app.pricing.forecasting.mathematics import mae, mape, mean, population_std, rmse
from app.pricing.forecasting.models import (
    ForecastDiagnostics,
    ForecastPoint,
    ForecastResult,
    HistoricalPoint,
    Observation,
    StrategyEvaluation,
)
from app.pricing.forecasting.strategies import ForecastStrategy, build_strategies
from app.pricing.forecasting.validation import prepare

MIN_OBSERVATIONS = 2
_Z_95 = 1.96
_DP = 4


def forecast_demand(
    observations: list[Observation],
    *,
    horizon: int = 4,
    window: int = 3,
    alpha: float = 0.3,
) -> ForecastResult:
    """Forecast future demand. Raises structured domain errors on bad input."""
    if horizon < 1:
        raise InvalidHorizonError("Forecast horizon must be a positive integer.")

    clean = prepare(observations)
    series = clean.values
    if len(series) < MIN_OBSERVATIONS:
        raise InsufficientObservationsError(
            f"At least {MIN_OBSERVATIONS} periods are required to forecast."
        )

    strategies = build_strategies(window=window, alpha=alpha)
    evaluations, ranked = _evaluate(strategies, series)
    selected_strategy, selected_actuals, selected_predictions = ranked

    residuals = [a - p for a, p in zip(selected_actuals, selected_predictions, strict=True)]
    resid_std = population_std(residuals) if residuals else 0.0

    forecast_values = selected_strategy.forecast(series, horizon)
    forecast_points = _forecast_points(forecast_values, resid_std)

    mape_value = mape(selected_actuals, selected_predictions) if residuals else None
    diagnostics = ForecastDiagnostics(
        selected_strategy=selected_strategy.method,
        mae=round(mae(selected_actuals, selected_predictions), _DP) if residuals else 0.0,
        mape=None if mape_value is None else round(mape_value, _DP),
        rmse=round(rmse(selected_actuals, selected_predictions), _DP) if residuals else 0.0,
        mean_error=round(mean(residuals), _DP) if residuals else 0.0,
        residuals=residual_summary(residuals),
        sample_size=len(series),
        distinct_periods=clean.distinct_periods,
        assumptions=build_assumptions(),
        notes=build_notes(
            selected=selected_strategy.method,
            sample_size=len(series),
            had_duplicates=clean.had_duplicates,
            irregular_intervals=clean.irregular_intervals,
            mape_defined=mape_value is not None,
            residual_count=len(residuals),
        ),
    )

    history = tuple(
        HistoricalPoint(period=period, demand=round(value, _DP))
        for period, value in zip(clean.periods, clean.values, strict=True)
    )

    return ForecastResult(
        horizon=horizon,
        selected_strategy=selected_strategy.method,
        forecast=forecast_points,
        history=history,
        diagnostics=diagnostics,
        alternatives=evaluations,
    )


def _evaluate(
    strategies: list[ForecastStrategy],
    series: list[float],
) -> tuple[tuple[StrategyEvaluation, ...], tuple[ForecastStrategy, list[float], list[float]]]:
    """Backtest each strategy and pick the lowest-RMSE evaluable one."""
    evaluations: list[StrategyEvaluation] = []
    scored: list[tuple[float, int, ForecastStrategy, list[float], list[float]]] = []

    for order, strategy in enumerate(strategies):
        # Need at least one holdout point beyond the warm-up to evaluate.
        if len(series) <= strategy.min_observations:
            evaluations.append(
                StrategyEvaluation(strategy.method, usable=False, mae=None, mape=None, rmse=None)
            )
            continue
        actuals, predictions = strategy.backtest(series)
        strategy_rmse = rmse(actuals, predictions)
        evaluations.append(
            StrategyEvaluation(
                method=strategy.method,
                usable=True,
                mae=round(mae(actuals, predictions), _DP),
                mape=(lambda m: None if m is None else round(m, _DP))(mape(actuals, predictions)),
                rmse=round(strategy_rmse, _DP),
            )
        )
        scored.append((strategy_rmse, order, strategy, actuals, predictions))

    if not scored:
        raise InsufficientObservationsError("No strategy could be evaluated on the series.")

    scored.sort(key=lambda item: (item[0], item[1]))  # RMSE asc, then registry order
    _, _, best_strategy, best_actuals, best_predictions = scored[0]
    return tuple(evaluations), (best_strategy, best_actuals, best_predictions)


def _forecast_points(values: list[float], resid_std: float) -> tuple[ForecastPoint, ...]:
    points: list[ForecastPoint] = []
    for index, predicted in enumerate(values, start=1):
        half_width = _Z_95 * resid_std * math.sqrt(index)
        lower = max(0.0, predicted - half_width)
        upper = predicted + half_width
        points.append(
            ForecastPoint(
                step=index,
                predicted=round(predicted, _DP),
                lower=round(lower, _DP),
                upper=round(upper, _DP),
            )
        )
    return tuple(points)
