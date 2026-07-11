"""Validation of simulation inputs — structured domain errors only."""

from __future__ import annotations

import math

from app.pricing.simulation.errors import (
    InvalidScenarioError,
    SimulationConfigurationError,
    SimulationInputError,
)
from app.pricing.simulation.models import ScenarioSpec, ScenarioType, SimulationInput


def _finite(name: str, value: float) -> None:
    if math.isnan(value) or math.isinf(value):
        raise SimulationInputError(f"{name} must be a finite number.")


def validate_input(inp: SimulationInput) -> None:
    _finite("current_price", inp.current_price)
    _finite("baseline_demand", inp.baseline_demand)
    _finite("elasticity", inp.elasticity)
    _finite("unit_cost", inp.unit_cost)
    _finite("fixed_cost", inp.fixed_cost)

    if inp.current_price <= 0:
        raise SimulationInputError("Current price must be positive.")
    if inp.baseline_demand < 0:
        raise SimulationInputError("Baseline demand must not be negative.")
    if inp.unit_cost < 0:
        raise SimulationInputError("Unit cost must not be negative.")
    if inp.fixed_cost < 0:
        raise SimulationInputError("Fixed cost must not be negative.")
    if inp.recommended_price is not None:
        _finite("recommended_price", inp.recommended_price)
        if inp.recommended_price <= 0:
            raise SimulationInputError("Recommended price must be positive.")

    if not inp.scenarios:
        raise SimulationConfigurationError("At least one scenario must be provided.")

    seen: set[tuple[ScenarioType, float | None, float | None]] = set()
    for spec in inp.scenarios:
        _validate_scenario(spec)
        key = (spec.type, spec.price, spec.percentage)
        if key in seen:
            raise InvalidScenarioError(f"Duplicate scenario: {spec.label!r}.")
        seen.add(key)


def _validate_scenario(spec: ScenarioSpec) -> None:
    if spec.type is ScenarioType.FIXED_PRICE:
        if spec.price is None:
            raise InvalidScenarioError("A fixed-price scenario requires a price.")
        _finite("scenario price", spec.price)
        if spec.price <= 0:
            raise InvalidScenarioError("Scenario price must be positive.")
    if spec.type in (ScenarioType.PERCENTAGE_INCREASE, ScenarioType.PERCENTAGE_DECREASE):
        if spec.percentage is None:
            raise InvalidScenarioError("A percentage scenario requires a percentage value.")
        _finite("scenario percentage", spec.percentage)
        if spec.percentage < 0:
            raise InvalidScenarioError("Scenario percentage must not be negative.")
        if spec.type is ScenarioType.PERCENTAGE_DECREASE and spec.percentage >= 1:
            raise InvalidScenarioError("A price decrease of 100% or more is not allowed.")
