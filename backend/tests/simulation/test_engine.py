"""Unit tests for the scenario-simulation engine (deterministic, hand-checked)."""

from __future__ import annotations

import pytest

from app.pricing.simulation import (
    Objective,
    ScenarioSpec,
    ScenarioType,
    SimulationInput,
    default_scenarios,
    simulate,
)


def _input(**overrides: object) -> SimulationInput:
    base: dict[str, object] = {
        "current_price": 5.0,
        "baseline_demand": 100.0,
        "elasticity": -2.0,
        "unit_cost": 2.0,
        "fixed_cost": 50.0,
        "objective": Objective.MAXIMIZE_GROSS_PROFIT,
        "recommended_price": 4.0,
        "scenarios": default_scenarios(recommended_available=True),
    }
    base.update(overrides)
    return SimulationInput(**base)  # type: ignore[arg-type]


def _by_label(result, label):  # type: ignore[no-untyped-def]
    return next(s for s in result.scenarios if s.label == label)


@pytest.mark.unit
def test_baseline_metrics() -> None:
    result = simulate(_input())
    b = _by_label(result, "Baseline")
    assert b.price == 5.0
    assert b.demand == pytest.approx(100.0)
    assert b.revenue == pytest.approx(500.0)  # 5 * 100
    assert b.gross_profit == pytest.approx(300.0)  # (5-2)*100
    assert b.net_profit == pytest.approx(250.0)  # 300 - 50
    assert b.contribution_margin == pytest.approx(300.0)
    assert b.margin_pct == pytest.approx(0.6)  # (5-2)/5


@pytest.mark.unit
def test_baseline_deltas_are_zero() -> None:
    b = _by_label(simulate(_input()), "Baseline")
    assert b.vs_baseline.revenue_abs == 0.0
    assert b.vs_baseline.demand_abs == 0.0
    assert b.vs_baseline.revenue_pct == pytest.approx(0.0)


@pytest.mark.unit
def test_recommended_scenario_metrics() -> None:
    r = _by_label(simulate(_input()), "Recommended")
    # P=4 -> Q=100*(4/5)^-2=156.25 ; rev=625 ; gp=(4-2)*156.25=312.5 ; np=262.5
    assert r.price == 4.0
    assert r.demand == pytest.approx(156.25)
    assert r.revenue == pytest.approx(625.0)
    assert r.gross_profit == pytest.approx(312.5)
    assert r.net_profit == pytest.approx(262.5)
    assert r.diagnostics.is_recommended is True


@pytest.mark.unit
def test_percentage_increase_price_and_demand() -> None:
    result = simulate(_input())
    plus10 = _by_label(result, "+10%")
    assert plus10.price == pytest.approx(5.5)
    # Q = 100*(5.5/5)^-2 = 100/1.21 = 82.6446
    assert plus10.demand == pytest.approx(82.6446, abs=1e-3)


@pytest.mark.unit
def test_percentage_decrease_price_and_demand() -> None:
    minus10 = _by_label(simulate(_input()), "-10%")
    assert minus10.price == pytest.approx(4.5)
    assert minus10.demand == pytest.approx(123.4568, abs=1e-3)


@pytest.mark.unit
def test_fixed_price_scenario() -> None:
    result = simulate(
        _input(
            scenarios=(
                ScenarioSpec(ScenarioType.BASELINE, label="Baseline"),
                ScenarioSpec(ScenarioType.FIXED_PRICE, label="$12", price=12.0),
            )
        )
    )
    fixed = _by_label(result, "$12")
    assert fixed.price == 12.0


@pytest.mark.unit
def test_ranking_selects_best_objective() -> None:
    result = simulate(_input())
    # gross-profit optimum is at P=4 (Recommended / -20%)
    assert result.best_scenario in {"Recommended", "-20%"}
    assert result.scenarios  # non-empty
    top = min(result.scenarios, key=lambda s: s.rank)
    assert top.rank == 1
    assert top.label == result.ranking_by_objective[0]


@pytest.mark.unit
def test_rankings_are_consistent() -> None:
    result = simulate(_input())
    labels = {s.label for s in result.scenarios}
    assert set(result.ranking_by_objective) == labels
    assert set(result.ranking_by_revenue) == labels
    assert set(result.ranking_by_net_profit) == labels


@pytest.mark.unit
def test_vs_recommended_present_when_recommended_available() -> None:
    b = _by_label(simulate(_input()), "Baseline")
    assert b.vs_recommended is not None


@pytest.mark.unit
def test_vs_recommended_absent_without_recommendation() -> None:
    result = simulate(
        _input(
            recommended_price=None,
            scenarios=default_scenarios(recommended_available=False),
        )
    )
    assert all(s.vs_recommended is None for s in result.scenarios)


@pytest.mark.unit
def test_diagnostics_direction_notes() -> None:
    result = simulate(_input())
    plus10 = _by_label(result, "+10%")
    joined = " ".join(plus10.diagnostics.notes)
    assert "Price increased by 10.0%" in joined
    assert "Demand decreased" in joined


@pytest.mark.unit
def test_overall_note_when_recommended_is_best() -> None:
    result = simulate(_input())
    if result.best_scenario == "Recommended":
        assert any("remains optimal" in n for n in result.notes)


@pytest.mark.unit
def test_deterministic() -> None:
    assert simulate(_input()) == simulate(_input())


@pytest.mark.unit
def test_revenue_objective_changes_ranking() -> None:
    # Use a recommended price that is NOT the revenue optimum so the ranking is unambiguous.
    result = simulate(_input(objective=Objective.MAXIMIZE_REVENUE, recommended_price=5.0))
    # For elastic demand revenue is maximized by the lowest price; among the default set
    # that is -20% (P = 4.0), lower than the recommended (P = 5.0).
    assert result.best_scenario == "-20%"
