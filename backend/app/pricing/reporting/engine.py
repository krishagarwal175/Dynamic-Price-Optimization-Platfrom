"""Reporting engine — pure composition of the analytics outputs into a report.

This engine does not compute; it communicates. Every number in the report originates from
an existing analytics engine (finance, elasticity, forecasting, optimization, simulation).
It validates the input, then assembles each section.
"""

from __future__ import annotations

from app.pricing.reporting.models import PricingReport, ReportInput
from app.pricing.reporting.sections import (
    build_assumptions,
    build_elasticity_summary,
    build_executive_summary,
    build_financial_summary,
    build_forecast_summary,
    build_limitations,
    build_metadata,
    build_optimization_summary,
    build_recommendations,
    build_scenario_summary,
)
from app.pricing.reporting.validation import validate_input


def generate_report(inp: ReportInput) -> PricingReport:
    """Assemble the full structured pricing report. Raises structured domain errors."""
    validate_input(inp)
    return PricingReport(
        metadata=build_metadata(inp),
        executive_summary=build_executive_summary(inp),
        financial=build_financial_summary(inp),
        elasticity=build_elasticity_summary(inp),
        forecast=build_forecast_summary(inp),
        optimization=build_optimization_summary(inp),
        scenario=build_scenario_summary(inp),
        recommendations=build_recommendations(inp),
        assumptions=build_assumptions(inp),
        limitations=build_limitations(inp),
    )
