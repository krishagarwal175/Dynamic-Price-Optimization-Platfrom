"""Elasticity-analysis domain errors (pure, framework-free)."""

from __future__ import annotations

from app.pricing.errors import AnalyticsError


class InsufficientObservationsError(AnalyticsError):
    """Too few observations to estimate elasticity."""


class DegenerateDataError(AnalyticsError):
    """Data cannot support estimation (e.g. all prices identical → no price variation)."""


class InvalidObservationError(AnalyticsError):
    """An observation violated a precondition (non-positive price or quantity)."""


class SingularRegressionError(AnalyticsError):
    """The regression has no unique solution (zero variance in the predictor)."""
