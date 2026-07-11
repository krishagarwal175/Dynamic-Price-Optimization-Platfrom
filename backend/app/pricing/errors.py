"""Analytics domain errors.

Pure, framework-free exceptions raised by the analytics engines. The service layer maps
these to API errors; the engines themselves never import FastAPI or the HTTP error layer.
"""

from __future__ import annotations


class AnalyticsError(Exception):
    """Base class for analytics computation errors."""


class InsufficientDataError(AnalyticsError):
    """Not enough data to compute a metric (e.g. no sales, zero total units)."""


class InvalidInputError(AnalyticsError):
    """An input violated a precondition (e.g. negative quantity, cost, or fixed cost)."""
