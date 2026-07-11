"""Unit tests for simulation building blocks: scenarios, validation, diagnostics."""

from __future__ import annotations

import math

import pytest

from app.pricing.simulation.diagnostics import build_diagnostics
from app.pricing.simulation.errors import (
    InvalidScenarioError,
    SimulationConfigurationError,
    SimulationInputError,
)
from app.pricing.simulation.models import (
    Objective,
    ScenarioSpec,
    ScenarioType,
    SimulationInput,
)
from app.pricing.simulation.scenarios import default_scenarios, resolve_price
from app.pricing.simulation.validation import validate_input


def _input(**overrides: object) -> SimulationInput:
    base: dict[str, object] = {
        "current_price": 10.0,
        "baseline_demand": 50.0,
        "elasticity": -1.5,
        "unit_cost": 4.0,
        "fixed_cost": 0.0,
        "objective": Objective.MAXIMIZE_GROSS_PROFIT,
        "recommended_price": 9.0,
        "scenarios": default_scenarios(recommended_available=True),
    }
    base.update(overrides)
    return SimulationInput(**base)  # type: ignore[arg-type]


# ---- scenarios / resolution ------------------------------------------------
@pytest.mark.unit
def test_resolve_baseline_and_recommended() -> None:
    inp = _input()
    assert resolve_price(ScenarioSpec(ScenarioType.BASELINE, label="b"), inp) == 10.0
    assert resolve_price(ScenarioSpec(ScenarioType.RECOMMENDED, label="r"), inp) == 9.0


@pytest.mark.unit
def test_resolve_percentages() -> None:
    inp = _input()
    up = ScenarioSpec(ScenarioType.PERCENTAGE_INCREASE, label="+20%", percentage=0.2)
    down = ScenarioSpec(ScenarioType.PERCENTAGE_DECREASE, label="-20%", percentage=0.2)
    assert resolve_price(up, inp) == pytest.approx(12.0)
    assert resolve_price(down, inp) == pytest.approx(8.0)


@pytest.mark.unit
def test_resolve_recommended_without_price_raises() -> None:
    inp = _input(recommended_price=None)
    with pytest.raises(SimulationConfigurationError):
        resolve_price(ScenarioSpec(ScenarioType.RECOMMENDED, label="r"), inp)


@pytest.mark.unit
def test_default_scenarios_composition() -> None:
    with_rec = default_scenarios(recommended_available=True)
    without = default_scenarios(recommended_available=False)
    assert any(s.type is ScenarioType.RECOMMENDED for s in with_rec)
    assert not any(s.type is ScenarioType.RECOMMENDED for s in without)
    assert sum(1 for s in with_rec if s.type is ScenarioType.PERCENTAGE_INCREASE) == 3


# ---- validation ------------------------------------------------------------
@pytest.mark.unit
@pytest.mark.parametrize(
    "overrides",
    [
        {"current_price": 0.0},
        {"current_price": -1.0},
        {"baseline_demand": -1.0},
        {"unit_cost": -1.0},
        {"fixed_cost": -1.0},
        {"elasticity": math.nan},
        {"current_price": math.inf},
    ],
)
def test_invalid_numeric_inputs(overrides: dict[str, object]) -> None:
    with pytest.raises(SimulationInputError):
        validate_input(_input(**overrides))


@pytest.mark.unit
def test_empty_scenarios_rejected() -> None:
    with pytest.raises(SimulationConfigurationError):
        validate_input(_input(scenarios=()))


@pytest.mark.unit
def test_duplicate_scenarios_rejected() -> None:
    spec = ScenarioSpec(ScenarioType.PERCENTAGE_INCREASE, label="+5%", percentage=0.05)
    with pytest.raises(InvalidScenarioError):
        validate_input(_input(scenarios=(spec, spec)))


@pytest.mark.unit
def test_fixed_price_without_price_rejected() -> None:
    spec = ScenarioSpec(ScenarioType.FIXED_PRICE, label="fx")
    with pytest.raises(InvalidScenarioError):
        validate_input(_input(scenarios=(spec,)))


@pytest.mark.unit
def test_full_decrease_rejected() -> None:
    spec = ScenarioSpec(ScenarioType.PERCENTAGE_DECREASE, label="-100%", percentage=1.0)
    with pytest.raises(InvalidScenarioError):
        validate_input(_input(scenarios=(spec,)))


# ---- diagnostics -----------------------------------------------------------
@pytest.mark.unit
def test_diagnostics_flags() -> None:
    diag = build_diagnostics(
        scenario_type=ScenarioType.PERCENTAGE_INCREASE,
        price_change_pct=8.0,
        demand_change_pct=-15.0,
        revenue_delta=-10.0,
        net_profit_delta=-5.0,
        margin_points=2.0,
        is_recommended=False,
    )
    assert diag.revenue_improved is False
    assert diag.profit_improved is False
    assert diag.margin_improved is True
    assert any("Demand loss outweighed" in n for n in diag.notes)


@pytest.mark.unit
def test_diagnostics_unchanged_price() -> None:
    diag = build_diagnostics(
        scenario_type=ScenarioType.BASELINE,
        price_change_pct=0.0,
        demand_change_pct=0.0,
        revenue_delta=0.0,
        net_profit_delta=0.0,
        margin_points=0.0,
        is_recommended=False,
    )
    assert any("unchanged" in n.lower() for n in diag.notes)
