"""Forecasting domain errors (pure, framework-free)."""

from __future__ import annotations

from app.pricing.errors import AnalyticsError


class EmptyDatasetError(AnalyticsError):
    """No observations were provided."""


class InsufficientObservationsError(AnalyticsError):
    """Too few observations to produce a forecast."""


class InvalidObservationError(AnalyticsError):
    """An observation violated a precondition (e.g. negative demand)."""


class InvalidHorizonError(AnalyticsError):
    """The requested forecast horizon is not a positive integer."""
