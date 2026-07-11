"""Unit tests for forecasting strategies and error metrics (hand-calculated)."""

from __future__ import annotations

import pytest

from app.pricing.forecasting.mathematics import mae, mape, population_std, rmse, weighted_mean
from app.pricing.forecasting.strategies import (
    MovingAverageStrategy,
    NaiveStrategy,
    SimpleExponentialSmoothingStrategy,
    WeightedMovingAverageStrategy,
)


@pytest.mark.unit
def test_naive_predicts_last_value() -> None:
    assert NaiveStrategy().predict_next([3, 7, 5]) == 5


@pytest.mark.unit
def test_moving_average() -> None:
    # mean of last 3 of [2,4,6,8] = mean(4,6,8) = 6
    assert MovingAverageStrategy(3).predict_next([2, 4, 6, 8]) == pytest.approx(6.0)


@pytest.mark.unit
def test_weighted_moving_average() -> None:
    # weights 1,2,3 on [4,6,8] = (4+12+24)/6 = 6.6667
    assert WeightedMovingAverageStrategy(3).predict_next([2, 4, 6, 8]) == pytest.approx(40 / 6)


@pytest.mark.unit
def test_simple_exponential_smoothing() -> None:
    # alpha 0.5 on [2,4]: level = 0.5*4 + 0.5*2 = 3
    assert SimpleExponentialSmoothingStrategy(0.5).predict_next([2, 4]) == pytest.approx(3.0)


@pytest.mark.unit
def test_flat_forecast_repeats_level() -> None:
    assert NaiveStrategy().forecast([1, 2, 9], horizon=3) == [9, 9, 9]


@pytest.mark.unit
def test_backtest_alignment() -> None:
    actuals, predictions = NaiveStrategy().backtest([5, 8, 6])
    # predict index1 from [5]->5 (actual 8); index2 from [5,8]->8 (actual 6)
    assert actuals == [8, 6]
    assert predictions == [5, 8]


@pytest.mark.unit
def test_error_metrics() -> None:
    actual = [10.0, 20.0, 30.0]
    predicted = [12.0, 18.0, 33.0]
    assert mae(actual, predicted) == pytest.approx((2 + 2 + 3) / 3)
    assert rmse(actual, predicted) == pytest.approx(((4 + 4 + 9) / 3) ** 0.5)
    # MAPE = mean(2/10, 2/20, 3/30) * 100 = mean(0.2,0.1,0.1)*100 = 13.3333
    assert mape(actual, predicted) == pytest.approx(100 * (0.2 + 0.1 + 0.1) / 3)


@pytest.mark.unit
def test_mape_none_when_all_zero() -> None:
    assert mape([0.0, 0.0], [1.0, 2.0]) is None


@pytest.mark.unit
def test_population_std_and_weighted_mean() -> None:
    assert population_std([2, 4, 6]) == pytest.approx((8 / 3) ** 0.5)
    assert weighted_mean([1, 2], [1, 3]) == pytest.approx((1 + 6) / 4)
