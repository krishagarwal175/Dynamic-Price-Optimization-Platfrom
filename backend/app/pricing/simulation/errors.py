"""Scenario-simulation domain errors (pure, framework-free)."""

from __future__ import annotations

from app.pricing.errors import AnalyticsError


class SimulationError(AnalyticsError):
    """Base class for scenario-simulation failures."""


class SimulationInputError(SimulationError):
    """A numeric input violated a precondition (bad price/cost/demand/elasticity)."""


class InvalidScenarioError(SimulationError):
    """A scenario definition is malformed (e.g. missing price, bad percentage)."""


class SimulationConfigurationError(SimulationError):
    """The simulation is misconfigured (e.g. a recommended scenario without a price)."""


class SimulationExecutionError(SimulationError):
    """A scenario could not be evaluated (unexpected numeric failure)."""
