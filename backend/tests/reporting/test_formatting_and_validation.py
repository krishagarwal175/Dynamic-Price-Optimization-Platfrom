"""Unit tests for formatting and validation."""

from __future__ import annotations

import pytest

from app.pricing.reporting import ReportFormat, generate_report, render, to_dict
from app.pricing.reporting.errors import (
    FormattingError,
    ReportingConfigurationError,
    ReportingInputError,
)
from app.pricing.reporting.validation import validate_input
from tests.reporting.support import make_report_input


# ---- formatting ------------------------------------------------------------
@pytest.mark.unit
def test_to_dict_has_all_sections() -> None:
    report = generate_report(make_report_input())
    data = to_dict(report)
    assert set(data.keys()) == {
        "metadata",
        "executive_summary",
        "financial",
        "elasticity",
        "forecast",
        "optimization",
        "scenario",
        "recommendations",
        "assumptions",
        "limitations",
    }


@pytest.mark.unit
def test_to_dict_is_json_primitive() -> None:
    import json

    data = to_dict(generate_report(make_report_input()))
    # Round-trips through JSON without custom encoders.
    assert json.loads(json.dumps(data))["metadata"]["title"] == "Pricing Analysis Report"


@pytest.mark.unit
def test_markdown_has_headings() -> None:
    md = render(generate_report(make_report_input()), ReportFormat.MARKDOWN)
    assert md.startswith("# Pricing Analysis Report")
    for heading in ("## Executive Summary", "## Financial Summary", "## Scenario Summary"):
        assert heading in md
    assert "| Scenario | Price |" in md  # scenario table


@pytest.mark.unit
def test_text_strips_markdown_markers() -> None:
    text = render(generate_report(make_report_input()), ReportFormat.TEXT)
    assert "#" not in text
    assert "**" not in text
    assert "Executive Summary" in text


@pytest.mark.unit
def test_render_json_raises() -> None:
    with pytest.raises(FormattingError):
        render(generate_report(make_report_input()), ReportFormat.JSON)


# ---- validation ------------------------------------------------------------
@pytest.mark.unit
def test_invalid_scope() -> None:
    with pytest.raises(ReportingConfigurationError):
        validate_input(make_report_input(scope="galaxy"))


@pytest.mark.unit
def test_empty_subject() -> None:
    with pytest.raises(ReportingConfigurationError):
        validate_input(make_report_input(subject="  "))


@pytest.mark.unit
def test_bad_currency() -> None:
    with pytest.raises(ReportingConfigurationError):
        validate_input(make_report_input(currency="US"))


@pytest.mark.unit
def test_valid_input_passes() -> None:
    validate_input(make_report_input())  # must not raise


@pytest.mark.unit
def test_generate_report_rejects_bad_scope() -> None:
    with pytest.raises(ReportingConfigurationError):
        generate_report(make_report_input(scope="nope"))


@pytest.mark.unit
def test_reporting_input_error_type() -> None:
    # ReportingInputError is part of the domain error hierarchy.
    assert issubclass(ReportingInputError, Exception)
