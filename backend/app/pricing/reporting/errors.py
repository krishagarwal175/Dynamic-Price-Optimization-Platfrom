"""Reporting domain errors (pure, framework-free)."""

from __future__ import annotations

from app.pricing.errors import AnalyticsError


class ReportingError(AnalyticsError):
    """Base class for reporting failures."""


class ReportingInputError(ReportingError):
    """A required engine output or input value is missing or malformed."""


class ReportingConfigurationError(ReportingError):
    """The report request is misconfigured (e.g. invalid metadata)."""


class ReportGenerationError(ReportingError):
    """A report section could not be assembled."""


class FormattingError(ReportingError):
    """The report could not be rendered in the requested format."""
