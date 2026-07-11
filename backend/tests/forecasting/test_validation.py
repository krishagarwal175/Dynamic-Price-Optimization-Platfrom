"""Unit tests for observation validation/normalization."""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from app.pricing.forecasting.errors import EmptyDatasetError, InvalidObservationError
from app.pricing.forecasting.models import Observation
from app.pricing.forecasting.validation import prepare


def _obs(values: list[tuple[date, float]]) -> list[Observation]:
    return [Observation(period=d, demand=v) for d, v in values]


@pytest.mark.unit
def test_empty_raises() -> None:
    with pytest.raises(EmptyDatasetError):
        prepare([])


@pytest.mark.unit
def test_negative_demand_raises() -> None:
    with pytest.raises(InvalidObservationError):
        prepare(_obs([(date(2026, 1, 1), -1.0)]))


@pytest.mark.unit
def test_duplicate_periods_are_summed() -> None:
    d = date(2026, 1, 1)
    clean = prepare(_obs([(d, 3.0), (d, 4.0), (date(2026, 1, 2), 5.0)]))
    assert clean.values == [7.0, 5.0]
    assert clean.had_duplicates is True


@pytest.mark.unit
def test_sorted_by_period() -> None:
    clean = prepare(
        _obs([(date(2026, 1, 3), 3.0), (date(2026, 1, 1), 1.0), (date(2026, 1, 2), 2.0)])
    )
    assert clean.values == [1.0, 2.0, 3.0]


@pytest.mark.unit
def test_irregular_intervals_detected() -> None:
    d = date(2026, 1, 1)
    regular = _obs([(d + timedelta(days=i), 1.0) for i in range(4)])
    assert prepare(regular).irregular_intervals is False

    irregular = _obs([(d, 1.0), (d + timedelta(days=1), 1.0), (d + timedelta(days=5), 1.0)])
    assert prepare(irregular).irregular_intervals is True
