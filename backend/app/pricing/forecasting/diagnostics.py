"""Diagnostics helpers: residual summaries and explainability notes."""

from __future__ import annotations

from collections.abc import Sequence

from app.pricing.forecasting.mathematics import mean, population_std
from app.pricing.forecasting.models import ForecastMethod, ResidualSummary


def residual_summary(residuals: Sequence[float]) -> ResidualSummary:
    if not residuals:
        return ResidualSummary(count=0, mean=0.0, std=0.0, minimum=0.0, maximum=0.0)
    return ResidualSummary(
        count=len(residuals),
        mean=round(mean(residuals), 4),
        std=round(population_std(residuals), 4),
        minimum=round(min(residuals), 4),
        maximum=round(max(residuals), 4),
    )


def build_assumptions() -> tuple[str, ...]:
    return (
        "Observations are ordered by period; each period's demand is the sum of its sales.",
        "Future demand behaves like the recent past (level persistence; no trend/seasonality).",
        "Forecasts are flat (constant) over the horizon.",
    )


def build_notes(
    *,
    selected: ForecastMethod,
    sample_size: int,
    had_duplicates: bool,
    irregular_intervals: bool,
    mape_defined: bool,
    residual_count: int,
) -> tuple[str, ...]:
    notes: list[str] = [f"Selected '{selected.value}' by lowest backtest RMSE."]
    if sample_size < 6:
        notes.append(f"Small sample (n={sample_size}); forecasts are low-confidence.")
    if had_duplicates:
        notes.append("Duplicate periods were aggregated (summed).")
    if irregular_intervals:
        notes.append("Observation intervals are irregular; treated as an ordered sequence.")
    if not mape_defined:
        notes.append("MAPE is undefined (zero actuals present) and reported as null.")
    if residual_count == 0:
        notes.append(
            "Too few points to estimate residuals; intervals collapse to the point forecast."
        )
    return tuple(notes)
