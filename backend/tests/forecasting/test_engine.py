"""Unit tests for the forecasting engine — selection, diagnostics, intervals."""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from app.pricing.forecasting import ForecastMethod, Observation, forecast_demand
from app.pricing.forecasting.errors import (
    EmptyDatasetError,
    InsufficientObservationsError,
    InvalidHorizonError,
    InvalidObservationError,
)


def _series(values: list[float]) -> list[Observation]:
    start = date(2026, 1, 1)
    return [Observation(period=start + timedelta(days=i), demand=v) for i, v in enumerate(values)]


@pytest.mark.unit
def test_constant_demand_is_forecast_perfectly() -> None:
    result = forecast_demand(_series([10, 10, 10, 10, 10, 10]), horizon=3)
    assert result.selected_strategy is ForecastMethod.NAIVE
    assert result.diagnostics.rmse == 0.0
    assert [p.predicted for p in result.forecast] == [10.0, 10.0, 10.0]
    # zero residual variance -> intervals collapse to the point
    assert result.forecast[0].lower == 10.0
    assert result.forecast[0].upper == 10.0


@pytest.mark.unit
def test_horizon_length_and_steps() -> None:
    result = forecast_demand(_series([5, 6, 7, 8, 9]), horizon=5)
    assert result.horizon == 5
    assert [p.step for p in result.forecast] == [1, 2, 3, 4, 5]


@pytest.mark.unit
def test_intervals_widen_with_horizon() -> None:
    result = forecast_demand(_series([10, 12, 9, 13, 8, 14, 7]), horizon=3)
    widths = [p.upper - p.lower for p in result.forecast]
    assert widths[0] <= widths[1] <= widths[2]
    assert all(p.lower >= 0 for p in result.forecast)


@pytest.mark.unit
def test_selection_returns_alternatives_with_metrics() -> None:
    result = forecast_demand(_series([1, 2, 3, 4, 5, 6, 7, 8]), horizon=2)
    methods = {e.method for e in result.alternatives}
    assert methods == set(ForecastMethod)
    usable = [e for e in result.alternatives if e.usable]
    assert usable  # at least one strategy evaluated
    # the selected strategy must have the minimum RMSE among usable ones
    best = min(e.rmse for e in usable if e.rmse is not None)
    selected_eval = next(e for e in result.alternatives if e.method is result.selected_strategy)
    assert selected_eval.rmse == pytest.approx(best)


@pytest.mark.unit
def test_moving_average_wins_on_noisy_mean_reverting() -> None:
    # Oscillating around 10 -> smoothing beats naive.
    result = forecast_demand(_series([8, 12, 8, 12, 8, 12, 8, 12]), horizon=1)
    assert result.selected_strategy in {
        ForecastMethod.MOVING_AVERAGE,
        ForecastMethod.WEIGHTED_MOVING_AVERAGE,
        ForecastMethod.SIMPLE_EXPONENTIAL_SMOOTHING,
    }


@pytest.mark.unit
def test_diagnostics_fields_present() -> None:
    result = forecast_demand(_series([3, 5, 4, 6, 5, 7]), horizon=2)
    diag = result.diagnostics
    assert diag.sample_size == 6
    assert diag.mae >= 0
    assert diag.rmse >= 0
    assert diag.residuals.count >= 1
    assert len(diag.assumptions) >= 1
    assert any("RMSE" in note for note in diag.notes)


@pytest.mark.unit
def test_fallback_to_naive_with_two_points() -> None:
    # Only 2 points: MA/WMA (window 3) cannot evaluate; naive is used.
    result = forecast_demand(_series([4, 9]), horizon=2)
    assert result.selected_strategy is ForecastMethod.NAIVE
    assert [p.predicted for p in result.forecast] == [9.0, 9.0]


@pytest.mark.unit
def test_insufficient_observations() -> None:
    with pytest.raises(InsufficientObservationsError):
        forecast_demand(_series([5]), horizon=2)


@pytest.mark.unit
def test_empty_dataset() -> None:
    with pytest.raises(EmptyDatasetError):
        forecast_demand([], horizon=2)


@pytest.mark.unit
def test_negative_demand() -> None:
    with pytest.raises(InvalidObservationError):
        forecast_demand(_series([5, -1, 3]), horizon=2)


@pytest.mark.unit
def test_invalid_horizon() -> None:
    with pytest.raises(InvalidHorizonError):
        forecast_demand(_series([1, 2, 3]), horizon=0)


@pytest.mark.unit
def test_history_is_returned() -> None:
    result = forecast_demand(_series([2, 4, 6]), horizon=1)
    assert [h.demand for h in result.history] == [2.0, 4.0, 6.0]
