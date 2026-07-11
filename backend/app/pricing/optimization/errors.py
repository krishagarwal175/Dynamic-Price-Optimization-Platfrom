"""Optimization domain errors (pure, framework-free)."""

from __future__ import annotations

from app.pricing.errors import AnalyticsError


class OptimizationError(AnalyticsError):
    """Base class for pricing-optimization failures."""


class InvalidInputError(OptimizationError):
    """An optimization input violated a precondition (bad price/cost/elasticity)."""


class InfeasibleConstraintsError(OptimizationError):
    """No price in the search range satisfies all constraints."""


class OptimizationFailedError(OptimizationError):
    """The search failed to find an optimum (should not normally happen)."""
