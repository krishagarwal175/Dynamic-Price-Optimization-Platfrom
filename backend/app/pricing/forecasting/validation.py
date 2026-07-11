"""Validation and normalization of raw observations into a clean demand series.

Duplicate periods are aggregated (summed); irregular intervals are tolerated but flagged.
Bad input raises structured domain errors — never infrastructure exceptions.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date

from app.pricing.forecasting.errors import EmptyDatasetError, InvalidObservationError
from app.pricing.forecasting.models import Observation


@dataclass(frozen=True)
class CleanSeries:
    periods: list[date]
    values: list[float]
    distinct_periods: int
    had_duplicates: bool
    irregular_intervals: bool


def prepare(observations: Sequence[Observation]) -> CleanSeries:
    if not observations:
        raise EmptyDatasetError("No observations were provided.")

    aggregated: dict[date, float] = defaultdict(float)
    for obs in observations:
        if obs.demand < 0:
            raise InvalidObservationError("Demand values must not be negative.")
        aggregated[obs.period] += obs.demand

    periods = sorted(aggregated)
    values = [aggregated[p] for p in periods]

    had_duplicates = len(observations) != len(periods)
    irregular_intervals = _has_irregular_intervals(periods)

    return CleanSeries(
        periods=periods,
        values=values,
        distinct_periods=len(periods),
        had_duplicates=had_duplicates,
        irregular_intervals=irregular_intervals,
    )


def _has_irregular_intervals(periods: Sequence[date]) -> bool:
    if len(periods) < 3:
        return False
    gaps = {(periods[i + 1] - periods[i]).days for i in range(len(periods) - 1)}
    return len(gaps) > 1
