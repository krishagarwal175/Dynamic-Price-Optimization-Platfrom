"""Validation of report inputs — structured domain errors only."""

from __future__ import annotations

from app.pricing.reporting.errors import ReportingConfigurationError, ReportingInputError
from app.pricing.reporting.models import ReportInput

_VALID_SCOPES = {"product", "dataset"}


def validate_input(inp: ReportInput) -> None:
    if inp.scope not in _VALID_SCOPES:
        raise ReportingConfigurationError(
            f"Report scope must be one of {sorted(_VALID_SCOPES)}, got {inp.scope!r}."
        )
    if not inp.subject.strip():
        raise ReportingConfigurationError("Report subject must not be empty.")
    if len(inp.currency) != 3:
        raise ReportingConfigurationError("Currency must be a 3-letter code.")

    # Required engine outputs must carry usable content.
    if not inp.forecast.forecast:
        raise ReportingInputError("Forecast output is empty; cannot build the forecast section.")
    if not inp.simulation.scenarios:
        raise ReportingInputError("Simulation output is empty; cannot build the scenario section.")
