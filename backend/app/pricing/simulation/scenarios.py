"""Scenario definitions and price resolution.

Turns an abstract :class:`ScenarioSpec` into a concrete price given the simulation input,
and provides the default scenario set. One responsibility: *what price does each scenario
imply?*
"""

from __future__ import annotations

from app.pricing.simulation.errors import (
    InvalidScenarioError,
    SimulationConfigurationError,
)
from app.pricing.simulation.models import ScenarioSpec, ScenarioType, SimulationInput

DEFAULT_PERCENTAGES = (0.05, 0.10, 0.20)


def resolve_price(spec: ScenarioSpec, inp: SimulationInput) -> float:
    """Resolve the concrete price a scenario evaluates. Raises structured errors."""
    if spec.type is ScenarioType.BASELINE:
        return inp.current_price
    if spec.type is ScenarioType.RECOMMENDED:
        if inp.recommended_price is None:
            raise SimulationConfigurationError(
                "A recommended scenario was requested but no recommended price is available."
            )
        return inp.recommended_price
    if spec.type is ScenarioType.FIXED_PRICE:
        if spec.price is None:
            raise InvalidScenarioError("A fixed-price scenario requires a price.")
        return spec.price
    if spec.type is ScenarioType.PERCENTAGE_INCREASE:
        return inp.current_price * (1.0 + _percentage(spec))
    # PERCENTAGE_DECREASE
    return inp.current_price * (1.0 - _percentage(spec))


def _percentage(spec: ScenarioSpec) -> float:
    if spec.percentage is None:
        raise InvalidScenarioError("A percentage scenario requires a percentage value.")
    return spec.percentage


def default_scenarios(recommended_available: bool) -> tuple[ScenarioSpec, ...]:
    """The standard comparison set: baseline, (recommended), and ±5/10/20%."""
    specs: list[ScenarioSpec] = [ScenarioSpec(ScenarioType.BASELINE, label="Baseline")]
    if recommended_available:
        specs.append(ScenarioSpec(ScenarioType.RECOMMENDED, label="Recommended"))
    for pct in DEFAULT_PERCENTAGES:
        specs.append(
            ScenarioSpec(ScenarioType.PERCENTAGE_INCREASE, label=f"+{pct:.0%}", percentage=pct)
        )
        specs.append(
            ScenarioSpec(ScenarioType.PERCENTAGE_DECREASE, label=f"-{pct:.0%}", percentage=pct)
        )
    return tuple(specs)
