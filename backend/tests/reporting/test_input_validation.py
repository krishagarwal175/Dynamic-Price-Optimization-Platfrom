"""Coverage for the reporting input guards on empty engine outputs."""

from __future__ import annotations

from dataclasses import replace
from types import SimpleNamespace

import pytest

from app.pricing.reporting.errors import ReportingInputError
from app.pricing.reporting.validation import validate_input
from tests.reporting.support import make_report_input


@pytest.mark.unit
def test_valid_report_input_passes() -> None:
    validate_input(make_report_input())  # no exception


@pytest.mark.unit
def test_empty_forecast_is_rejected() -> None:
    broken = replace(make_report_input(), forecast=SimpleNamespace(forecast=[]))
    with pytest.raises(ReportingInputError):
        validate_input(broken)


@pytest.mark.unit
def test_empty_simulation_is_rejected() -> None:
    broken = replace(make_report_input(), simulation=SimpleNamespace(scenarios=[]))
    with pytest.raises(ReportingInputError):
        validate_input(broken)
