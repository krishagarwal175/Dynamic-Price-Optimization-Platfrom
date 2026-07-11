"""Scenario-simulation sub-engine (pure, deterministic what-if analysis)."""

from __future__ import annotations

from app.pricing.simulation.engine import simulate
from app.pricing.simulation.models import (
    Objective,
    ScenarioResult,
    ScenarioSpec,
    ScenarioType,
    SimulationInput,
    SimulationResult,
)
from app.pricing.simulation.scenarios import default_scenarios

__all__ = [
    "Objective",
    "ScenarioResult",
    "ScenarioSpec",
    "ScenarioType",
    "SimulationInput",
    "SimulationResult",
    "default_scenarios",
    "simulate",
]
